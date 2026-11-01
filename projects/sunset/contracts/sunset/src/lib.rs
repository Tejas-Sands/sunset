#![cfg_attr(not(target_arch = "wasm32"), allow(dead_code))]

use borsh::{BorshDeserialize, BorshSerialize};

const MAX_CAMPAIGNS: usize = 5;
const MAX_ACCOUNTS: usize = 100;
const STORAGE_PRICE: u128 = 10_000_000_000_000_000_000;
const ACCOUNT_STORAGE: u128 = 10_000_000_000_000_000_000_000;
const CAMPAIGN_STORAGE: u128 = 50_000_000_000_000_000_000_000;
type Result<T> = std::result::Result<T, &'static str>;

#[derive(Clone, BorshSerialize, BorshDeserialize)]
struct Terms {
    id: String,
    title: String,
    reviewer: String,
    manifest_uri: String,
    manifest_hash: [u8; 32],
    plaintext_hash: [u8; 32],
    ciphertext_hash: [u8; 32],
    key_commitment: [u8; 32],
    license_hash: [u8; 32],
    target: u128,
    funding_deadline_ns: u64,
    release_window_ns: u64,
}

#[derive(Clone, BorshSerialize, BorshDeserialize)]
struct Campaign {
    terms: Terms,
    creator: String,
    digest: [u8; 32],
    approved: bool,
    funded_at_ns: u64,
    released: bool,
    public_key: [u8; 32],
    escrow: u128,
    total_contributed: u128,
}

#[derive(Clone, Default, BorshSerialize, BorshDeserialize)]
struct Account {
    id: String,
    credit: u128,
    contributions: [u128; MAX_CAMPAIGNS],
    refunded: [bool; MAX_CAMPAIGNS],
    pending_amount: u128,
    operation_id: u64,
    pending: bool,
    paid: u128,
}

#[derive(Clone, Default, BorshSerialize, BorshDeserialize)]
struct State {
    owner: String,
    campaigns: Vec<Campaign>,
    accounts: Vec<Account>,
    economic_deposits: u128,
    storage_deposits: u128,
    storage_retained: u128,
    withdrawn: u128,
}

impl State {
    fn new(owner: &str) -> Self {
        Self {
            owner: owner.into(),
            ..Self::default()
        }
    }
    fn create(
        &mut self,
        terms: Terms,
        caller: &str,
        contract: &str,
        now: u64,
        deposit: u128,
    ) -> Result<()> {
        ensure(
            caller == self.owner,
            "only configured owner may create campaigns",
        )?;
        ensure(
            self.campaigns.len() < MAX_CAMPAIGNS,
            "campaign limit reached",
        )?;
        ensure(
            self.campaigns.iter().all(|c| c.terms.id != terms.id),
            "campaign already exists",
        )?;
        ensure(
            !terms.id.is_empty()
                && terms.id.len() <= 64
                && terms
                    .id
                    .bytes()
                    .all(|b| b.is_ascii_alphanumeric() || b == b'-' || b == b'_'),
            "invalid campaign id",
        )?;
        ensure(
            !terms.title.is_empty() && terms.title.len() <= 120,
            "invalid title",
        )?;
        ensure(
            terms.manifest_uri.starts_with("https://") && terms.manifest_uri.len() <= 512,
            "invalid manifest URI",
        )?;
        ensure(
            valid_account(caller) && valid_account(&terms.reviewer),
            "invalid account",
        )?;
        ensure(
            now > 0 && terms.target > 0 && terms.funding_deadline_ns > now,
            "invalid funding terms",
        )?;
        ensure(
            terms.release_window_ns > 0
                && terms.release_window_ns <= 2_592_000_000_000_000
                && terms
                    .funding_deadline_ns
                    .checked_add(terms.release_window_ns)
                    .is_some(),
            "invalid release window",
        )?;
        ensure(
            deposit == CAMPAIGN_STORAGE,
            "attach exact campaign storage allowance",
        )?;
        let old_size = self.size();
        self.register(caller)?;
        let digest = hash(
            &borsh::to_vec(&(1u8, "testnet", contract, caller, &terms))
                .map_err(|_| "cannot encode agreement")?,
        );
        self.campaigns.push(Campaign {
            terms,
            creator: caller.into(),
            digest,
            approved: false,
            funded_at_ns: 0,
            released: false,
            public_key: [0; 32],
            escrow: 0,
            total_contributed: 0,
        });
        self.charge_storage(old_size, deposit, caller)
    }
    fn approve(&mut self, id: &str, digest: &[u8; 32], caller: &str, now: u64) -> Result<()> {
        let i = self.campaign_index(id)?;
        let campaign = &mut self.campaigns[i];
        ensure(
            caller == campaign.terms.reviewer,
            "only named reviewer may approve",
        )?;
        ensure(digest == &campaign.digest, "agreement digest mismatch")?;
        ensure(now < campaign.terms.funding_deadline_ns, "funding expired")?;
        campaign.approved = true;
        Ok(())
    }
    fn contribute(
        &mut self,
        id: &str,
        caller: &str,
        amount: u128,
        deposit: u128,
        now: u64,
    ) -> Result<()> {
        let i = self.campaign_index(id)?;
        ensure(
            self.status(i, now) == "Active",
            "campaign is not accepting contributions",
        )?;
        ensure(amount > 0, "contribution must be positive")?;
        let allowance = if self.account(caller).is_err() {
            ACCOUNT_STORAGE
        } else {
            0
        };
        ensure(
            deposit == add(amount, allowance)?,
            "attach amount plus exact new-account storage allowance",
        )?;
        let old_size = self.size();
        self.register(caller)?;
        let accepted =
            amount.min(self.campaigns[i].terms.target - self.campaigns[i].total_contributed);
        self.economic_deposits = add(self.economic_deposits, amount)?;
        let account = self.account_mut(caller)?;
        account.credit = add(account.credit, amount - accepted)?;
        account.contributions[i] = add(account.contributions[i], accepted)?;
        let campaign = &mut self.campaigns[i];
        campaign.total_contributed = add(campaign.total_contributed, accepted)?;
        campaign.escrow = add(campaign.escrow, accepted)?;
        if campaign.total_contributed == campaign.terms.target {
            campaign.funded_at_ns = now;
        }
        self.charge_storage(old_size, allowance, caller)
    }
    fn release(&mut self, id: &str, key: &[u8; 32], now: u64) -> Result<()> {
        let i = self.campaign_index(id)?;
        ensure(
            key_commitment(key) == self.campaigns[i].terms.key_commitment,
            "content key mismatch",
        )?;
        if self.campaigns[i].released {
            return Ok(());
        }
        ensure(
            self.status(i, now) == "Funded",
            "campaign is not funded or release expired",
        )?;
        let creator = self.campaigns[i].creator.clone();
        let credit = add(self.account(&creator)?.credit, self.campaigns[i].escrow)?;
        self.account_mut(&creator)?.credit = credit;
        let campaign = &mut self.campaigns[i];
        campaign.public_key = *key;
        campaign.released = true;
        campaign.escrow = 0;
        Ok(())
    }
    fn refund(&mut self, id: &str, caller: &str, now: u64) -> Result<()> {
        let i = self.campaign_index(id)?;
        ensure(
            self.status(i, now) == "Refundable",
            "campaign is not refundable",
        )?;
        let account = self.account(caller)?;
        if account.refunded[i] {
            return Ok(());
        }
        let amount = account.contributions[i];
        ensure(amount > 0, "no contribution to refund")?;
        let credit = add(account.credit, amount)?;
        let escrow = self.campaigns[i]
            .escrow
            .checked_sub(amount)
            .ok_or("escrow underflow")?;
        let account = self.account_mut(caller)?;
        account.refunded[i] = true;
        account.credit = credit;
        self.campaigns[i].escrow = escrow;
        Ok(())
    }
    fn account(&self, id: &str) -> Result<&Account> {
        self.accounts
            .iter()
            .find(|a| a.id == id)
            .ok_or("account not registered")
    }
    fn begin_withdraw(&mut self, caller: &str, amount: u128, gas: u64) -> Result<u64> {
        ensure(
            gas >= 40_000_000_000_000,
            "withdraw requires at least 40 Tgas remaining",
        )?;
        let account = self.account_mut(caller)?;
        ensure(!account.pending, "withdrawal is pending")?;
        ensure(
            amount > 0 && amount <= account.credit,
            "insufficient credit or zero amount",
        )?;
        let operation = account
            .operation_id
            .checked_add(1)
            .ok_or("operation id overflow")?;
        account.credit -= amount;
        account.pending_amount = amount;
        account.operation_id = operation;
        account.pending = true;
        Ok(operation)
    }
    fn complete_withdraw(&mut self, id: &str, operation: u64, success: bool) -> Result<()> {
        let account = self.account(id)?;
        ensure(
            account.pending && account.operation_id == operation,
            "unknown or completed withdrawal",
        )?;
        let amount = account.pending_amount;
        let withdrawn = if success {
            add(self.withdrawn, amount)?
        } else {
            self.withdrawn
        };
        let account = self.account_mut(id)?;
        if success {
            account.paid = add(account.paid, amount)?;
        } else {
            account.credit = add(account.credit, amount)?;
        }
        account.pending_amount = 0;
        account.pending = false;
        self.withdrawn = withdrawn;
        Ok(())
    }
    fn account_mut(&mut self, id: &str) -> Result<&mut Account> {
        self.accounts
            .iter_mut()
            .find(|a| a.id == id)
            .ok_or("account not registered")
    }
    fn campaign_index(&self, id: &str) -> Result<usize> {
        self.campaigns
            .iter()
            .position(|c| c.terms.id == id)
            .ok_or("unknown campaign")
    }
    fn register(&mut self, id: &str) -> Result<()> {
        ensure(valid_account(id), "invalid account")?;
        if self.account(id).is_ok() {
            return Ok(());
        }
        ensure(self.accounts.len() < MAX_ACCOUNTS, "account limit reached")?;
        self.accounts.push(Account {
            id: id.into(),
            ..Account::default()
        });
        Ok(())
    }
    fn size(&self) -> usize {
        borsh::to_vec(self)
            .expect("fixed bounded state encodes")
            .len()
    }
    fn charge_storage(&mut self, old_size: usize, allowance: u128, payer: &str) -> Result<()> {
        let growth = self
            .size()
            .checked_sub(old_size)
            .ok_or("unexpected storage shrink")?;
        let cost = (growth as u128)
            .checked_mul(STORAGE_PRICE)
            .ok_or("storage overflow")?;
        ensure(cost <= allowance, "insufficient storage allowance")?;
        self.storage_deposits = add(self.storage_deposits, allowance)?;
        self.storage_retained = add(self.storage_retained, cost)?;
        let account = self.account_mut(payer)?;
        account.credit = add(account.credit, allowance - cost)?;
        Ok(())
    }
    fn status(&self, i: usize, now: u64) -> &'static str {
        let c = &self.campaigns[i];
        if c.released {
            "Released"
        } else if !c.approved {
            "Draft"
        } else if c.funded_at_ns > 0 {
            if now >= c.funded_at_ns + c.terms.release_window_ns {
                "Refundable"
            } else {
                "Funded"
            }
        } else if now >= c.terms.funding_deadline_ns {
            "Refundable"
        } else {
            "Active"
        }
    }
    fn check_accounting(&self) -> Result<()> {
        let mut liabilities = add(self.storage_retained, self.withdrawn)?;
        for c in &self.campaigns {
            liabilities = add(liabilities, c.escrow)?;
        }
        for a in &self.accounts {
            liabilities = add(liabilities, add(a.credit, a.pending_amount)?)?;
        }
        ensure(
            add(self.economic_deposits, self.storage_deposits)? == liabilities,
            "accounting invariant violated",
        )
    }
}

fn add(a: u128, b: u128) -> Result<u128> {
    a.checked_add(b).ok_or("amount overflow")
}
fn ensure(condition: bool, error: &'static str) -> Result<()> {
    if condition {
        Ok(())
    } else {
        Err(error)
    }
}
fn valid_account(id: &str) -> bool {
    if !(2..=64).contains(&id.len()) {
        return false;
    }
    let mut separator = true;
    for b in id.bytes() {
        if b.is_ascii_lowercase() || b.is_ascii_digit() {
            separator = false;
        } else if matches!(b, b'.' | b'_' | b'-') && !separator {
            separator = true;
        } else {
            return false;
        }
    }
    !separator
}

struct Context {
    current: String,
    predecessor: String,
    attached: u128,
    now: u64,
    remaining_gas: u64,
    callback_result: Option<bool>,
    callback_count: u64,
}

fn hex(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}
fn text<'a>(input: &'a serde_json::Value, name: &str) -> Result<&'a str> {
    input
        .get(name)
        .and_then(|v| v.as_str())
        .ok_or("missing or non-string argument")
}
fn number(input: &serde_json::Value, name: &str) -> Result<u128> {
    let value = text(input, name)?;
    ensure(
        !value.is_empty() && value.len() <= 39 && value.bytes().all(|b| b.is_ascii_digit()),
        "expected unsigned decimal string",
    )?;
    value.parse().map_err(|_| "decimal value out of range")
}
fn time(input: &serde_json::Value, name: &str) -> Result<u64> {
    number(input, name)?
        .try_into()
        .map_err(|_| "timestamp or id out of range")
}
fn hash_argument(input: &serde_json::Value, name: &str) -> Result<[u8; 32]> {
    let value = text(input, name)?;
    ensure(
        value.len() == 64
            && value
                .bytes()
                .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b)),
        "expected lowercase SHA-256 hex",
    )?;
    let mut result = [0; 32];
    for (i, byte) in result.iter_mut().enumerate() {
        *byte = u8::from_str_radix(&value[i * 2..i * 2 + 2], 16).map_err(|_| "invalid hash")?;
    }
    Ok(result)
}
fn execute(
    state: &mut State,
    method: &str,
    input: &serde_json::Value,
    ctx: &Context,
) -> Result<serde_json::Value> {
    use base64::{engine::general_purpose::STANDARD, Engine};
    use serde_json::json;
    let allowed: &[&str] = match method {
        "create_campaign" => &[
            "id",
            "title",
            "reviewer",
            "manifest_uri",
            "manifest_hash",
            "plaintext_hash",
            "ciphertext_hash",
            "key_commitment",
            "license_hash",
            "target",
            "funding_deadline_ns",
            "release_window_ns",
        ],
        "approve_campaign" => &["id", "agreement_digest"],
        "contribute" => &["id", "amount"],
        "publish_release" => &["id", "key_base64"],
        "claim_refund" | "get_campaign" => &["id"],
        "withdraw" => &["amount"],
        "on_withdraw_complete" => &["account_id", "operation_id"],
        "get_account" => &["account_id"],
        "get_config" | "list_campaigns" => &[],
        _ => return Err("unknown method"),
    };
    let object = input.as_object().ok_or("arguments must be an object")?;
    ensure(
        object.keys().all(|k| allowed.contains(&k.as_str())) && object.len() == allowed.len(),
        "missing or unknown argument",
    )?;
    if !matches!(method, "create_campaign" | "contribute") {
        ensure(ctx.attached == 0, "this method accepts no deposit")?;
    }
    match method {
        "create_campaign" => {
            let terms = Terms {
                id: text(input, "id")?.into(),
                title: text(input, "title")?.into(),
                reviewer: text(input, "reviewer")?.into(),
                manifest_uri: text(input, "manifest_uri")?.into(),
                manifest_hash: hash_argument(input, "manifest_hash")?,
                plaintext_hash: hash_argument(input, "plaintext_hash")?,
                ciphertext_hash: hash_argument(input, "ciphertext_hash")?,
                key_commitment: hash_argument(input, "key_commitment")?,
                license_hash: hash_argument(input, "license_hash")?,
                target: number(input, "target")?,
                funding_deadline_ns: time(input, "funding_deadline_ns")?,
                release_window_ns: time(input, "release_window_ns")?,
            };
            state.create(terms, &ctx.predecessor, &ctx.current, ctx.now, ctx.attached)?;
            state.campaign_view(text(input, "id")?, ctx.now)
        }
        "approve_campaign" => {
            state.approve(
                text(input, "id")?,
                &hash_argument(input, "agreement_digest")?,
                &ctx.predecessor,
                ctx.now,
            )?;
            state.campaign_view(text(input, "id")?, ctx.now)
        }
        "contribute" => {
            state.contribute(
                text(input, "id")?,
                &ctx.predecessor,
                number(input, "amount")?,
                ctx.attached,
                ctx.now,
            )?;
            Ok(
                json!({"campaign":state.campaign_view(text(input,"id")?,ctx.now)?,"account":state.account_view(&ctx.predecessor)}),
            )
        }
        "publish_release" => {
            let key = STANDARD
                .decode(text(input, "key_base64")?)
                .map_err(|_| "invalid key base64")?;
            let key: [u8; 32] = key.try_into().map_err(|_| "key must be exactly 32 bytes")?;
            state.release(text(input, "id")?, &key, ctx.now)?;
            state.campaign_view(text(input, "id")?, ctx.now)
        }
        "claim_refund" => {
            state.refund(text(input, "id")?, &ctx.predecessor, ctx.now)?;
            Ok(state.account_view(&ctx.predecessor))
        }
        "withdraw" => {
            state.begin_withdraw(
                &ctx.predecessor,
                number(input, "amount")?,
                ctx.remaining_gas,
            )?;
            Ok(state.account_view(&ctx.predecessor))
        }
        "on_withdraw_complete" => {
            ensure(ctx.predecessor == ctx.current, "private callback")?;
            ensure(
                ctx.callback_count == 1,
                "callback requires one promise result",
            )?;
            let success = ctx.callback_result.ok_or("promise result is not ready")?;
            state.complete_withdraw(
                text(input, "account_id")?,
                time(input, "operation_id")?,
                success,
            )?;
            Ok(state.account_view(text(input, "account_id")?))
        }
        "get_campaign" => state.campaign_view(text(input, "id")?, ctx.now),
        "get_account" => Ok(state.account_view(text(input, "account_id")?)),
        "list_campaigns" => Ok(json!(state
            .campaigns
            .iter()
            .map(|c| state.campaign_view(&c.terms.id, ctx.now))
            .collect::<Result<Vec<_>>>()?)),
        "get_config" => Ok(
            json!({"schema_version":1,"network":"testnet","contract_id":ctx.current,"owner":state.owner,"deployment_mode":"upgradeable", "max_campaigns":MAX_CAMPAIGNS,"max_accounts":MAX_ACCOUNTS,"campaign_count":state.campaigns.len(),"account_count":state.accounts.len(),"account_storage_allowance":ACCOUNT_STORAGE.to_string(),"campaign_storage_allowance":CAMPAIGN_STORAGE.to_string(),"storage_price_per_byte":STORAGE_PRICE.to_string(),"economic_deposits":state.economic_deposits.to_string(),"storage_deposits":state.storage_deposits.to_string(),"storage_retained":state.storage_retained.to_string(),"withdrawn":state.withdrawn.to_string()}),
        ),
        _ => Err("unknown method"),
    }
}

impl State {
    fn campaign_view(&self, id: &str, now: u64) -> Result<serde_json::Value> {
        use base64::{engine::general_purpose::STANDARD, Engine};
        let i = self.campaign_index(id)?;
        let c = &self.campaigns[i];
        Ok(
            serde_json::json!({"schema_version":1,"id":c.terms.id,"title":c.terms.title,"creator":c.creator,"reviewer":c.terms.reviewer,"manifest_uri":c.terms.manifest_uri,"manifest_hash":hex(&c.terms.manifest_hash),"plaintext_hash":hex(&c.terms.plaintext_hash),"ciphertext_hash":hex(&c.terms.ciphertext_hash),"key_commitment":hex(&c.terms.key_commitment),"license_hash":hex(&c.terms.license_hash),"target":c.terms.target.to_string(),"total_contributed":c.total_contributed.to_string(),"escrow":c.escrow.to_string(),"funding_deadline_ns":c.terms.funding_deadline_ns.to_string(),"release_window_ns":c.terms.release_window_ns.to_string(),"funded_at_ns":c.funded_at_ns.to_string(),"release_deadline_ns":if c.funded_at_ns > 0 {Some((c.funded_at_ns+c.terms.release_window_ns).to_string())}else{None},"agreement_digest":hex(&c.digest),"state":self.status(i,now),"public_key_base64":if c.released {Some(STANDARD.encode(c.public_key))}else{None}}),
        )
    }
    fn account_view(&self, id: &str) -> serde_json::Value {
        use serde_json::json;
        match self.account(id) {
            Ok(a) => {
                json!({"schema_version":1,"account_id":a.id,"registered":true,"credit":a.credit.to_string(),"paid":a.paid.to_string(),"pending":if a.pending {Some(json!({"amount":a.pending_amount.to_string(),"operation_id":a.operation_id.to_string()}))}else{None},"contributions":self.campaigns.iter().enumerate().filter(|(i,_)| a.contributions[*i]>0).map(|(i,c)| json!({"campaign_id":c.terms.id,"amount":a.contributions[i].to_string(),"refunded":a.refunded[i]})).collect::<Vec<_>>()})
            }
            Err(_) => {
                json!({"schema_version":1,"account_id":id,"registered":false,"credit":"0","paid":"0","pending":null,"contributions":[]})
            }
        }
    }
}

fn key_commitment(key: &[u8; 32]) -> [u8; 32] {
    let mut data = b"SUNSET:KEY:1:".to_vec();
    data.extend_from_slice(key);
    hash(&data)
}

#[cfg(not(target_arch = "wasm32"))]
fn hash(data: &[u8]) -> [u8; 32] {
    use std::{
        io::Write,
        process::{Command, Stdio},
    };
    let mut child = Command::new("openssl")
        .args(["dgst", "-sha256", "-binary"])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .expect("native tests require openssl");
    child.stdin.take().unwrap().write_all(data).unwrap();
    let output = child.wait_with_output().unwrap();
    assert!(output.status.success());
    output.stdout.try_into().expect("SHA-256 is 32 bytes")
}

#[cfg(test)]
mod tests;

#[cfg(target_arch = "wasm32")]
mod host;

#[cfg(target_arch = "wasm32")]
fn hash(data: &[u8]) -> [u8; 32] {
    host::sha256(data)
}
