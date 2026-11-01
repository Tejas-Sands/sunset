//! One transferable discovery-mirror stewardship right per public release.
use super::*;
use serde_json::{json, Value};

const MAX_MIRROR: usize = 512;
pub(super) const TRANSFER_CALL_GAS: u64 = 40_000_000_000_000;

// Fixed-capacity fields are paid for on campaign creation, before escrow exists.
#[derive(Clone, BorshSerialize, BorshDeserialize)]
pub(super) struct Stewardship {
    owner_bytes: [u8; 64],
    owner_len: u8,
    mirror_bytes: [u8; MAX_MIRROR],
    mirror_len: u16,
    pub(super) issued_at_ns: u64,
    pub(super) updated_at_ns: u64,
}

impl Stewardship {
    pub(super) fn new(owner: &str, mirror: &str) -> Self {
        let mut result = Self {
            owner_bytes: [0; 64],
            owner_len: 0,
            mirror_bytes: [0; MAX_MIRROR],
            mirror_len: 0,
            issued_at_ns: 0,
            updated_at_ns: 0,
        };
        result.set_owner(owner);
        result.set_mirror(mirror);
        result
    }
    pub(super) fn owner(&self) -> &str {
        std::str::from_utf8(&self.owner_bytes[..self.owner_len as usize])
            .expect("stored owner is valid UTF-8")
    }
    pub(super) fn mirror(&self) -> &str {
        std::str::from_utf8(&self.mirror_bytes[..self.mirror_len as usize])
            .expect("stored mirror is valid UTF-8")
    }
    fn set_owner(&mut self, owner: &str) {
        self.owner_bytes.fill(0);
        self.owner_bytes[..owner.len()].copy_from_slice(owner.as_bytes());
        self.owner_len = owner.len() as u8;
    }
    fn set_mirror(&mut self, mirror: &str) {
        self.mirror_bytes.fill(0);
        self.mirror_bytes[..mirror.len()].copy_from_slice(mirror.as_bytes());
        self.mirror_len = mirror.len() as u16;
    }
}

pub(super) fn is_view(method: &str) -> bool {
    matches!(
        method,
        "nft_token"
            | "nft_metadata"
            | "nft_total_supply"
            | "nft_tokens"
            | "nft_supply_for_owner"
            | "nft_tokens_for_owner"
    )
}
pub(super) fn is_method(method: &str) -> bool {
    is_view(method)
        || matches!(
            method,
            "nft_transfer" | "nft_transfer_call" | "nft_resolve_transfer" | "set_mirror"
        )
}

pub(super) fn event(name: &str, data: Value) {
    let value = json!({"standard":"nep171","version":"1.2.0","event":name,"data":data});
    #[cfg(target_arch = "wasm32")]
    super::host::log_event(&format!("EVENT_JSON:{value}"));
    #[cfg(not(target_arch = "wasm32"))]
    let _ = value;
}

fn fields(input: &Value, required: &[&str], optional: &[&str]) -> Result<()> {
    let object = input.as_object().ok_or("arguments must be an object")?;
    ensure(
        required.iter().all(|key| object.contains_key(*key))
            && object
                .keys()
                .all(|key| required.contains(&key.as_str()) || optional.contains(&key.as_str())),
        "missing or unknown argument",
    )
}
fn optional_text<'a>(input: &'a Value, key: &str, maximum: usize) -> Result<Option<&'a str>> {
    match input.get(key) {
        None | Some(Value::Null) => Ok(None),
        Some(Value::String(value)) if value.len() <= maximum => Ok(Some(value)),
        _ => Err("invalid optional text argument"),
    }
}
fn valid_uri(uri: &str) -> bool {
    let Some(rest) = uri.strip_prefix("https://") else {
        return false;
    };
    let authority = rest.split(['/', '?', '#']).next().unwrap_or("");
    uri.len() <= MAX_MIRROR
        && !authority.is_empty()
        && !authority.contains('@')
        && !uri
            .chars()
            .any(|c| c.is_control() || c.is_whitespace() || c == '\\')
}
fn token_index(state: &State, id: &str) -> Result<usize> {
    let index = state.campaign_index(id)?;
    ensure(state.campaigns[index].released, "token is not minted")?;
    Ok(index)
}
fn change_owner(state: &mut State, index: usize, receiver: &str, memo: Option<&str>, now: u64) {
    let campaign = &mut state.campaigns[index];
    let previous = campaign.stewardship.owner().to_string();
    campaign.stewardship.set_owner(receiver);
    campaign
        .stewardship
        .set_mirror(&campaign.terms.manifest_uri);
    campaign.stewardship.updated_at_ns = now;
    let mut data =
        json!({"old_owner_id":previous,"new_owner_id":receiver,"token_ids":[campaign.terms.id]});
    if let Some(memo) = memo {
        data["memo"] = json!(memo);
    }
    event("nft_transfer", json!([data]));
    event(
        "nft_metadata_update",
        json!([{"token_ids":[campaign.terms.id]}]),
    );
}
fn token(campaign: &Campaign) -> Value {
    use base64::{engine::general_purpose::STANDARD, Engine};
    json!({"token_id":campaign.terms.id,"owner_id":campaign.stewardship.owner(),"metadata":{
        "title":format!("{} — stewardship",campaign.terms.title),
        "description":"Transferable authority to choose a discovery mirror for this committed public release. No exclusivity, copyright, escrow, refund, payment or licensing authority. Every ownership change resets the mirror to the original manifest URI.",
        "media":null,"media_hash":null,"copies":1,
        "issued_at":campaign.stewardship.issued_at_ns / 1_000_000,"expires_at":null,"starts_at":null,"updated_at":campaign.stewardship.updated_at_ns / 1_000_000,
        "extra":json!({"right":"public-release-mirror-stewardship","mirror_uri":campaign.stewardship.mirror(),"original_manifest_uri":campaign.terms.manifest_uri,"manifest_hash":hex(&campaign.terms.manifest_hash),"agreement_digest":hex(&campaign.digest)}).to_string(),
        "reference":campaign.terms.manifest_uri,"reference_hash":STANDARD.encode(campaign.terms.manifest_hash)
    }})
}
fn page(state: &State, owner: Option<&str>, input: &Value) -> Result<Value> {
    let from = match input.get("from_index") {
        None | Some(Value::Null) => 0,
        _ => number(input, "from_index")?,
    };
    let limit = match input.get("limit") {
        None | Some(Value::Null) => MAX_CAMPAIGNS as u64,
        Some(value) => value
            .as_u64()
            .filter(|n| *n > 0)
            .ok_or("limit must be a positive integer")?,
    };
    let tokens = state
        .campaigns
        .iter()
        .filter(|c| c.released && owner.is_none_or(|id| c.stewardship.owner() == id));
    Ok(json!(tokens
        .enumerate()
        .filter(|(index, _)| *index as u128 >= from)
        .take(limit.min(MAX_CAMPAIGNS as u64) as usize)
        .map(|(_, c)| token(c))
        .collect::<Vec<_>>()))
}

pub(super) fn execute(
    state: &mut State,
    method: &str,
    input: &Value,
    ctx: &Context,
) -> Result<Value> {
    let (required, optional): (&[&str], &[&str]) = match method {
        "nft_transfer" => (&["receiver_id", "token_id"], &["approval_id", "memo"]),
        "nft_transfer_call" => (
            &["receiver_id", "token_id", "msg"],
            &["approval_id", "memo"],
        ),
        "nft_resolve_transfer" => (
            &["previous_owner_id", "receiver_id", "token_id"],
            &["approved_account_ids"],
        ),
        "set_mirror" => (&["token_id", "mirror_uri"], &[]),
        "nft_token" => (&["token_id"], &[]),
        "nft_metadata" | "nft_total_supply" => (&[], &[]),
        "nft_tokens" => (&[], &["from_index", "limit"]),
        "nft_supply_for_owner" => (&["account_id"], &[]),
        "nft_tokens_for_owner" => (&["account_id"], &["from_index", "limit"]),
        _ => return Err("unknown NFT method"),
    };
    fields(input, required, optional)?;
    let secured = matches!(method, "nft_transfer" | "nft_transfer_call" | "set_mirror");
    ensure(
        ctx.attached == u128::from(secured),
        if secured {
            "attach exactly 1 yoctoNEAR"
        } else {
            "this method accepts no deposit"
        },
    )?;
    match method {
        "nft_transfer" | "nft_transfer_call" => {
            if let Some(value) = input.get("approval_id").filter(|v| !v.is_null()) {
                ensure(
                    value.as_u64().is_some_and(|n| n < (1u64 << 53)),
                    "invalid approval id",
                )?;
            }
            let memo = optional_text(input, "memo", 512)?;
            let receiver = text(input, "receiver_id")?;
            ensure(valid_account(receiver), "invalid receiver account")?;
            let index = token_index(state, text(input, "token_id")?)?;
            ensure(
                state.campaigns[index].stewardship.owner() == ctx.predecessor,
                "only token owner may transfer",
            )?;
            ensure(
                receiver != ctx.predecessor,
                "current and next owner must differ",
            )?;
            if method == "nft_transfer_call" {
                ensure(
                    text(input, "msg")?.len() <= 4096,
                    "receiver message too large",
                )?;
                ensure(
                    ctx.remaining_gas >= TRANSFER_CALL_GAS,
                    "nft_transfer_call requires at least 40 Tgas remaining",
                )?;
            }
            let reserve = add(state.security_deposits, 1)?;
            change_owner(state, index, receiver, memo, ctx.now);
            state.security_deposits = reserve;
            Ok(Value::Null)
        }
        "set_mirror" => {
            let uri = text(input, "mirror_uri")?;
            ensure(valid_uri(uri), "invalid HTTPS mirror URI")?;
            let index = token_index(state, text(input, "token_id")?)?;
            ensure(
                state.campaigns[index].stewardship.owner() == ctx.predecessor,
                "only token owner may update mirror",
            )?;
            let reserve = add(state.security_deposits, 1)?;
            let c = &mut state.campaigns[index];
            c.stewardship.set_mirror(uri);
            c.stewardship.updated_at_ns = ctx.now;
            event("nft_metadata_update", json!([{"token_ids":[c.terms.id]}]));
            state.security_deposits = reserve;
            Ok(token(c))
        }
        "nft_resolve_transfer" => {
            ensure(ctx.predecessor == ctx.current, "private callback")?;
            ensure(
                ctx.callback_count == 1,
                "callback requires one promise result",
            )?;
            ensure(ctx.callback_result.is_some(), "promise result is not ready")?;
            ensure(
                input.get("approved_account_ids").is_none_or(Value::is_null),
                "approval management is not enabled",
            )?;
            let previous = text(input, "previous_owner_id")?;
            let receiver = text(input, "receiver_id")?;
            ensure(
                valid_account(previous) && valid_account(receiver) && previous != receiver,
                "invalid resolver accounts",
            )?;
            let index = token_index(state, text(input, "token_id")?)?;
            let accepted = ctx.callback_result == Some(true)
                && ctx
                    .callback_data
                    .as_deref()
                    .filter(|data| data.len() <= 5)
                    .and_then(|data| serde_json::from_slice::<bool>(data).ok())
                    == Some(false);
            if accepted || state.campaigns[index].stewardship.owner() != receiver {
                return Ok(json!(true));
            }
            change_owner(state, index, previous, None, ctx.now);
            Ok(json!(false))
        }
        "nft_token" => {
            let id = text(input, "token_id")?;
            Ok(state
                .campaigns
                .iter()
                .find(|c| c.terms.id == id && c.released)
                .map(token)
                .unwrap_or(Value::Null))
        }
        "nft_metadata" => Ok(
            json!({"spec":"nft-1.0.0","name":"SUNSET public release stewardship","symbol":"SUNSET","icon":null,"base_uri":null,"reference":null,"reference_hash":null}),
        ),
        "nft_total_supply" => Ok(json!(state
            .campaigns
            .iter()
            .filter(|c| c.released)
            .count()
            .to_string())),
        "nft_tokens" => page(state, None, input),
        "nft_supply_for_owner" | "nft_tokens_for_owner" => {
            let owner = text(input, "account_id")?;
            ensure(valid_account(owner), "invalid owner account")?;
            if method == "nft_supply_for_owner" {
                Ok(json!(state
                    .campaigns
                    .iter()
                    .filter(|c| c.released && c.stewardship.owner() == owner)
                    .count()
                    .to_string()))
            } else {
                page(state, Some(owner), input)
            }
        }
        _ => Err("unknown NFT method"),
    }
}
