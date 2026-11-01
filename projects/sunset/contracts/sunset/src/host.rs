//! Minimal stable NEAR host ABI. All business transitions live in the tested shared module.
use super::*;

const STATE_KEY: &[u8] = b"STATE";
const MAX_BYTES: u64 = 65_536;
const CALLBACK_GAS: u64 = 15_000_000_000_000;

#[link(wasm_import_module = "env")]
extern "C" {
    fn input(register_id: u64);
    fn register_len(register_id: u64) -> u64;
    fn read_register(register_id: u64, pointer: u64);
    fn current_account_id(register_id: u64);
    fn predecessor_account_id(register_id: u64);
    fn attached_deposit(pointer: u64);
    fn block_timestamp() -> u64;
    fn prepaid_gas() -> u64;
    fn used_gas() -> u64;
    #[link_name = "sha256"]
    fn host_sha256(value_len: u64, value_ptr: u64, register_id: u64);
    fn storage_read(key_len: u64, key_ptr: u64, register_id: u64) -> u64;
    fn storage_write(
        key_len: u64,
        key_ptr: u64,
        value_len: u64,
        value_ptr: u64,
        register_id: u64,
    ) -> u64;
    fn value_return(value_len: u64, value_ptr: u64);
    fn panic_utf8(value_len: u64, value_ptr: u64);
    fn promise_results_count() -> u64;
    fn promise_result(index: u64, register_id: u64) -> u64;
    fn promise_batch_create(account_id_len: u64, account_id_ptr: u64) -> u64;
    fn promise_batch_action_transfer(promise_index: u64, amount_ptr: u64);
    fn promise_batch_then(promise_index: u64, account_id_len: u64, account_id_ptr: u64) -> u64;
    fn promise_batch_action_function_call(
        promise_index: u64,
        method_name_len: u64,
        method_name_ptr: u64,
        arguments_len: u64,
        arguments_ptr: u64,
        amount_ptr: u64,
        gas: u64,
    );
    fn promise_return(promise_index: u64);
}

fn fail(message: &str) -> ! {
    unsafe {
        panic_utf8(message.len() as u64, message.as_ptr() as u64);
    }
    core::arch::wasm32::unreachable()
}
fn checked<T>(result: Result<T>) -> T {
    result.unwrap_or_else(|e| fail(e))
}
fn register() -> Vec<u8> {
    let size = unsafe { register_len(0) };
    if size > MAX_BYTES {
        fail("register exceeds bounded size");
    }
    let mut bytes = vec![0; size as usize];
    unsafe {
        read_register(0, bytes.as_mut_ptr() as u64);
    }
    bytes
}
fn account(getter: unsafe extern "C" fn(u64)) -> String {
    unsafe {
        getter(0);
    }
    String::from_utf8(register()).unwrap_or_else(|_| fail("invalid account encoding"))
}
pub(super) fn sha256(bytes: &[u8]) -> [u8; 32] {
    unsafe {
        host_sha256(bytes.len() as u64, bytes.as_ptr() as u64, 0);
    }
    register()
        .try_into()
        .unwrap_or_else(|_| fail("invalid SHA-256 host result"))
}

fn run(method: &str) {
    unsafe {
        input(0);
    }
    let args: serde_json::Value =
        serde_json::from_slice(&register()).unwrap_or_else(|_| fail("invalid JSON input"));
    let current = account(current_account_id);
    let is_view = matches!(
        method,
        "get_config" | "get_campaign" | "get_account" | "list_campaigns"
    );
    let predecessor = if is_view {
        String::new()
    } else {
        account(predecessor_account_id)
    };
    let mut amount = [0u8; 16];
    if !is_view {
        unsafe {
            attached_deposit(amount.as_mut_ptr() as u64);
        }
    }
    let callback_count = if method == "on_withdraw_complete" {
        unsafe { promise_results_count() }
    } else {
        0
    };
    let callback_result = if callback_count == 1 {
        match unsafe { promise_result(0, 0) } {
            1 => Some(true),
            2 => Some(false),
            _ => None,
        }
    } else {
        None
    };
    let ctx = Context {
        current,
        predecessor,
        attached: u128::from_le_bytes(amount),
        now: unsafe { block_timestamp() },
        remaining_gas: if is_view {
            0
        } else {
            unsafe { prepaid_gas().saturating_sub(used_gas()) }
        },
        callback_count,
        callback_result,
    };
    let exists = unsafe { storage_read(STATE_KEY.len() as u64, STATE_KEY.as_ptr() as u64, 0) } == 1;
    if method == "new" {
        checked(ensure(!exists, "already initialized"));
        checked(ensure(
            ctx.current == ctx.predecessor,
            "initializer is private",
        ));
        checked(ensure(
            ctx.attached == 0
                && args
                    .as_object()
                    .is_some_and(|o| o.len() == 1 && o.contains_key("owner")),
            "new requires owner argument and no deposit",
        ));
        let owner = checked(text(&args, "owner"));
        checked(ensure(valid_account(owner), "invalid owner account"));
        save(&State::new(owner));
        output(
            &serde_json::json!({"schema_version":1,"network":"testnet","contract_id":ctx.current}),
        );
        return;
    }
    if !exists {
        fail("contract is not initialized");
    }
    let mut state =
        State::try_from_slice(&register()).unwrap_or_else(|_| fail("invalid contract state"));
    let result = checked(execute(&mut state, method, &args, &ctx));
    if !is_view {
        checked(state.check_accounting());
        save(&state);
    }
    if method == "withdraw" {
        let owner = checked(state.account(&ctx.predecessor));
        schedule_transfer(&ctx, owner);
    } else {
        output(&result);
    }
}
fn save(state: &State) {
    let bytes = borsh::to_vec(state).unwrap_or_else(|_| fail("state serialization failed"));
    if bytes.len() as u64 > MAX_BYTES {
        fail("contract state limit reached");
    }
    unsafe {
        storage_write(
            STATE_KEY.len() as u64,
            STATE_KEY.as_ptr() as u64,
            bytes.len() as u64,
            bytes.as_ptr() as u64,
            0,
        );
    }
}
fn output(value: &serde_json::Value) {
    let bytes = serde_json::to_vec(value).unwrap_or_else(|_| fail("response serialization failed"));
    unsafe {
        value_return(bytes.len() as u64, bytes.as_ptr() as u64);
    }
}
fn schedule_transfer(ctx: &Context, owner: &Account) {
    let remaining = unsafe { prepaid_gas().saturating_sub(used_gas()) };
    checked(ensure(
        remaining >= CALLBACK_GAS + 10_000_000_000_000,
        "insufficient gas to schedule safe callback",
    ));
    let amount = owner.pending_amount.to_le_bytes();
    let zero = 0u128.to_le_bytes();
    let args = serde_json::to_vec(
        &serde_json::json!({"account_id":owner.id,"operation_id":owner.operation_id.to_string()}),
    )
    .unwrap_or_else(|_| fail("callback serialization failed"));
    let name = b"on_withdraw_complete";
    unsafe {
        let transfer = promise_batch_create(owner.id.len() as u64, owner.id.as_ptr() as u64);
        promise_batch_action_transfer(transfer, amount.as_ptr() as u64);
        let callback = promise_batch_then(
            transfer,
            ctx.current.len() as u64,
            ctx.current.as_ptr() as u64,
        );
        promise_batch_action_function_call(
            callback,
            name.len() as u64,
            name.as_ptr() as u64,
            args.len() as u64,
            args.as_ptr() as u64,
            zero.as_ptr() as u64,
            CALLBACK_GAS,
        );
        promise_return(callback);
    }
}

macro_rules! entrypoints {
    ($($name:ident),* $(,)?) => {$(#[no_mangle] pub extern "C" fn $name() { run(stringify!($name)); })*};
}
entrypoints!(
    new,
    create_campaign,
    approve_campaign,
    contribute,
    publish_release,
    claim_refund,
    withdraw,
    on_withdraw_complete,
    get_config,
    get_campaign,
    get_account,
    list_campaigns
);
