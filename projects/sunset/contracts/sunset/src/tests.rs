use super::*;

#[test]
fn sponsorship_caps_and_release_credits_only_creator_once() {
    let mut state = State::new("creator.testnet");
    let terms = fixture_terms("pack", 100, 100);
    state
        .create(
            terms,
            "creator.testnet",
            "sunset.testnet",
            1,
            CAMPAIGN_STORAGE,
        )
        .unwrap();
    let digest = state.campaigns[0].digest;
    state
        .approve("pack", &digest, "reviewer.testnet", 2)
        .unwrap();
    state
        .contribute("pack", "buyer.testnet", 80, 80 + ACCOUNT_STORAGE, 3)
        .unwrap();
    state
        .contribute("pack", "buyer.testnet", 40, 40, 4)
        .unwrap();
    assert_eq!(state.campaigns[0].escrow, 100);
    assert_eq!(
        state.account("buyer.testnet").unwrap().contributions[0],
        100
    );
    assert!(state.account("buyer.testnet").unwrap().credit >= 20);
    state.release("pack", &[7; 32], 5).unwrap();
    assert_eq!(state.campaigns[0].escrow, 0);
    assert!(state.account("creator.testnet").unwrap().credit >= 100);
    let before = state.account("creator.testnet").unwrap().credit;
    state.release("pack", &[7; 32], 6).unwrap();
    assert_eq!(state.account("creator.testnet").unwrap().credit, before);
    assert!(state.refund("pack", "buyer.testnet", 200).is_err());
    assert!(state.contribute("pack", "buyer.testnet", 1, 1, 6).is_err());
    state.check_accounting().unwrap();
}

fn fixture_terms(id: &str, target: u128, deadline: u64) -> Terms {
    Terms {
        id: id.into(),
        title: "Original arithmetic pack".into(),
        reviewer: "reviewer.testnet".into(),
        manifest_uri: "https://example.test/pack.json".into(),
        manifest_hash: [1; 32],
        plaintext_hash: [2; 32],
        ciphertext_hash: [3; 32],
        key_commitment: key_commitment(&[7; 32]),
        license_hash: [4; 32],
        target,
        funding_deadline_ns: deadline,
        release_window_ns: 20,
    }
}

fn active_state(target: u128, deadline: u64) -> State {
    let mut state = State::new("creator.testnet");
    state
        .create(
            fixture_terms("pack", target, deadline),
            "creator.testnet",
            "sunset.testnet",
            1,
            CAMPAIGN_STORAGE,
        )
        .unwrap();
    let digest = state.campaigns[0].digest;
    state
        .approve("pack", &digest, "reviewer.testnet", 2)
        .unwrap();
    state
}

#[test]
fn both_deadline_paths_refund_once_and_never_release() {
    for (target, now) in [(100, 100), (50, 23)] {
        let mut state = active_state(target, 100);
        state
            .contribute("pack", "buyer.testnet", 50, 50 + ACCOUNT_STORAGE, 3)
            .unwrap();
        let credit = state.account("buyer.testnet").unwrap().credit;
        assert!(state.refund("pack", "buyer.testnet", now - 1).is_err());
        state.refund("pack", "buyer.testnet", now).unwrap();
        assert_eq!(state.account("buyer.testnet").unwrap().credit, credit + 50);
        state.refund("pack", "buyer.testnet", now).unwrap();
        assert_eq!(state.account("buyer.testnet").unwrap().credit, credit + 50);
        assert!(state.release("pack", &[7; 32], now).is_err());
        state.check_accounting().unwrap();
    }
}

#[test]
fn review_key_and_funding_boundaries_fail_closed() {
    let mut state = active_state(50, 100);
    assert!(state
        .approve("pack", &[1; 32], "reviewer.testnet", 3)
        .is_err());
    let digest = state.campaigns[0].digest;
    assert!(state
        .approve("pack", &digest, "attacker.testnet", 3)
        .is_err());
    assert!(state.release("pack", &[7; 32], 3).is_err());
    assert!(state
        .contribute("pack", "buyer.testnet", 50, 50 + ACCOUNT_STORAGE, 100)
        .is_err());
    assert!(state
        .contribute("pack", "buyer.testnet", 50, 50, 3)
        .is_err());
    state
        .contribute("pack", "buyer.testnet", 50, 50 + ACCOUNT_STORAGE, 3)
        .unwrap();
    assert!(state.release("pack", &[8; 32], 4).is_err());
    state.release("pack", &[7; 32], 22).unwrap();
    state.check_accounting().unwrap();
}

#[test]
fn disclosure_refund_and_withdraw_states_never_grow() {
    let mut state = active_state(50, 100);
    state
        .contribute("pack", "buyer.testnet", 50, 50 + ACCOUNT_STORAGE, 3)
        .unwrap();
    let size = state.size();
    state.release("pack", &[7; 32], 4).unwrap();
    assert_eq!(state.size(), size);
    let operation = state
        .begin_withdraw("creator.testnet", 50, 40_000_000_000_000)
        .unwrap();
    assert_eq!(state.size(), size);
    assert!(state
        .begin_withdraw("creator.testnet", 1, 40_000_000_000_000)
        .is_err());
    state
        .complete_withdraw("creator.testnet", operation, true)
        .unwrap();
    assert_eq!(state.size(), size);
    assert!(state
        .complete_withdraw("creator.testnet", operation, true)
        .is_err());
    state.check_accounting().unwrap();
}

#[test]
fn withdrawal_failure_restores_once_and_low_gas_cannot_start() {
    let mut state = active_state(50, 100);
    let initial = state.account("creator.testnet").unwrap().credit;
    assert!(state.begin_withdraw("creator.testnet", 1, 1).is_err());
    assert_eq!(state.account("creator.testnet").unwrap().credit, initial);
    let op = state
        .begin_withdraw("creator.testnet", 10, 40_000_000_000_000)
        .unwrap();
    assert!(state
        .complete_withdraw("creator.testnet", op + 1, false)
        .is_err());
    state
        .complete_withdraw("creator.testnet", op, false)
        .unwrap();
    assert_eq!(state.account("creator.testnet").unwrap().credit, initial);
    assert!(state
        .complete_withdraw("creator.testnet", op, false)
        .is_err());
    state.check_accounting().unwrap();
}

#[test]
fn crypto_vector_and_json_roundtrip_preserve_large_integers() {
    let key: [u8; 32] = std::array::from_fn(|i| i as u8);
    assert_eq!(
        hex(&key_commitment(&key)),
        "e537e7d09b63e03318dc8b601070e14c2804137cc09890fe071f7cfe7e708c22"
    );
    let mut state = active_state(50, 100);
    let ctx = context("viewer.testnet", 0, 3);
    let out = execute(
        &mut state,
        "get_campaign",
        &serde_json::json!({"id":"pack"}),
        &ctx,
    )
    .unwrap();
    assert_eq!(out["target"], "50");
    assert_eq!(out["state"], "Active");
    assert!(out["public_key_base64"].is_null());
    assert!(execute(
        &mut state,
        "contribute",
        &serde_json::json!({"id":"pack","amount":50}),
        &ctx
    )
    .is_err());
    assert!(execute(
        &mut state,
        "get_campaign",
        &serde_json::json!({"id":"pack","typo":true}),
        &ctx
    )
    .is_err());
}

#[test]
fn callback_requires_self_exact_result_and_matching_operation() {
    let mut state = active_state(50, 100);
    let op = state
        .begin_withdraw("creator.testnet", 10, 40_000_000_000_000)
        .unwrap();
    let args = serde_json::json!({"account_id":"creator.testnet","operation_id":op.to_string()});
    let mut ctx = context("attacker.testnet", 0, 3);
    ctx.callback_result = Some(false);
    ctx.callback_count = 1;
    assert!(execute(&mut state, "on_withdraw_complete", &args, &ctx).is_err());
    ctx.predecessor = ctx.current.clone();
    ctx.callback_count = 0;
    assert!(execute(&mut state, "on_withdraw_complete", &args, &ctx).is_err());
    ctx.callback_count = 1;
    ctx.callback_result = None;
    assert!(execute(&mut state, "on_withdraw_complete", &args, &ctx).is_err());
    ctx.callback_result = Some(false);
    execute(&mut state, "on_withdraw_complete", &args, &ctx).unwrap();
    assert!(!state.account("creator.testnet").unwrap().pending);
    state.check_accounting().unwrap();
}

fn context(predecessor: &str, attached: u128, now: u64) -> Context {
    Context {
        current: "sunset.testnet".into(),
        predecessor: predecessor.into(),
        attached,
        now,
        remaining_gas: 100_000_000_000_000,
        callback_result: None,
        callback_count: 0,
        callback_data: None,
    }
}

#[test]
fn record_bounds_and_storage_allowances_match_actual_serialized_growth() {
    let mut state = active_state(1_000, 100);
    let initial_size = State::new("creator.testnet").size();
    for index in 0..99 {
        let account = format!("buyer{index}.testnet");
        state
            .contribute("pack", &account, 1, 1 + ACCOUNT_STORAGE, 3)
            .unwrap();
        state.check_accounting().unwrap();
    }
    assert_eq!(state.accounts.len(), MAX_ACCOUNTS);
    assert!(state
        .contribute("pack", "overflow.testnet", 1, 1 + ACCOUNT_STORAGE, 3)
        .is_err());
    assert_eq!(
        state.storage_retained,
        ((state.size() - initial_size) as u128) * STORAGE_PRICE
    );
    assert!(state.size() < 65_536);
    for index in 1..MAX_CAMPAIGNS {
        state
            .create(
                fixture_terms(&format!("pack{index}"), 100, 100),
                "creator.testnet",
                "sunset.testnet",
                1,
                CAMPAIGN_STORAGE,
            )
            .unwrap();
    }
    assert!(state
        .create(
            fixture_terms("overflow", 100, 100),
            "creator.testnet",
            "sunset.testnet",
            1,
            CAMPAIGN_STORAGE
        )
        .is_err());
    state.check_accounting().unwrap();
}

#[test]
fn interleaved_campaigns_refunds_and_withdrawals_conserve_every_deposit() {
    let mut state = active_state(100, 100);
    state
        .create(
            fixture_terms("other", 200, 100),
            "creator.testnet",
            "sunset.testnet",
            1,
            CAMPAIGN_STORAGE,
        )
        .unwrap();
    let digest = state.campaigns[1].digest;
    state
        .approve("other", &digest, "reviewer.testnet", 2)
        .unwrap();
    for index in 0..10 {
        let account = format!("buyer{index}.testnet");
        state
            .contribute("pack", &account, 10, 10 + ACCOUNT_STORAGE, 3)
            .unwrap();
        state.contribute("other", &account, 10, 10, 3).unwrap();
        state.check_accounting().unwrap();
    }
    state.release("pack", &[7; 32], 4).unwrap();
    for index in 0..10 {
        let account = format!("buyer{index}.testnet");
        state.refund("other", &account, 100).unwrap();
        let op = state
            .begin_withdraw(&account, 10, 40_000_000_000_000)
            .unwrap();
        state.check_accounting().unwrap();
        state
            .complete_withdraw(&account, op, index % 2 == 0)
            .unwrap();
        state.check_accounting().unwrap();
    }
    assert_eq!(state.withdrawn, 50);
}

#[test]
fn curated_campaign_capacity_cannot_be_consumed_by_another_creator() {
    let mut state = active_state(50, 100);
    assert!(state
        .create(
            fixture_terms("squatted", 50, 100),
            "attacker.testnet",
            "sunset.testnet",
            1,
            CAMPAIGN_STORAGE
        )
        .is_err());
    assert_eq!(state.campaigns.len(), 1);
    state.check_accounting().unwrap();
}

#[test]
fn campaign_reviewer_must_differ_from_creator_before_storage_is_charged() {
    let mut state = State::new("creator.testnet");
    let before = borsh::to_vec(&state).unwrap();
    let mut terms = fixture_terms("self-reviewed", 50, 100);
    terms.reviewer = "creator.testnet".into();
    assert!(state
        .create(
            terms,
            "creator.testnet",
            "sunset.testnet",
            1,
            CAMPAIGN_STORAGE
        )
        .is_err());
    assert_eq!(borsh::to_vec(&state).unwrap(), before);
    state.check_accounting().unwrap();
}

fn released_state() -> State {
    let mut state = active_state(50, 100);
    state
        .contribute("pack", "buyer.testnet", 50, 50 + ACCOUNT_STORAGE, 3)
        .unwrap();
    state.release("pack", &[7; 32], 4).unwrap();
    state
}

fn invalid_resource_uris() -> Vec<String> {
    let mut uris: Vec<String> = [
        "https://",
        "https://:",
        "https://[",
        "https://example.org:",
        "https://example.org:zero/pack",
        "https://example.org:0/pack",
        "https://example.org:65536/pack",
        "https://example.org:999999999999999999999/pack",
        "https://name:secret@example.org/pack",
        "https://example.org/white space",
        "https://example.org/\npack",
        "https://example.org/\u{7f}pack",
        "https://example.org/\\pack",
        "https://example.org/pack#part",
        "https://localhost/pack",
        "https://files.local/pack",
        "https://files.internal/pack",
        "https://127.0.0.1/pack",
        "https://127.1/pack",
        "https://0x7f.0x0.0x0.0x1/pack",
        "https://[::1]/pack",
        "https://example.org./pack",
        "https://bad..example.org/pack",
        "https://-bad.example.org/pack",
        "https://bad-.example.org/pack",
        "https://bad_host.example.org/pack",
        "https://éxample.org/pack",
        "https://EXAMPLE.org/pack",
    ]
    .into_iter()
    .map(String::from)
    .collect();
    uris.push(format!("https://{}.org/pack", "a".repeat(64)));
    uris.push(format!(
        "https://{}.org/pack",
        vec!["a".repeat(63); 4].join(".")
    ));
    uris.push(format!("https://example.org/{}a", "é".repeat(246)));
    uris
}

#[test]
fn invalid_resource_uris_cannot_create_campaigns_or_charge_storage() {
    let mut initial = State::new("creator.testnet");
    for uri in invalid_resource_uris() {
        let before = borsh::to_vec(&initial).unwrap();
        let mut terms = fixture_terms("invalid-uri", 50, 100);
        terms.manifest_uri = uri.clone();
        assert!(
            initial
                .create(
                    terms,
                    "creator.testnet",
                    "sunset.testnet",
                    1,
                    CAMPAIGN_STORAGE
                )
                .is_err(),
            "campaign accepted {uri:?}"
        );
        assert_eq!(borsh::to_vec(&initial).unwrap(), before);
    }
    initial.check_accounting().unwrap();
}

#[test]
fn invalid_resource_uris_cannot_change_stewardship_or_money() {
    use serde_json::json;
    let mut released = released_state();
    for uri in invalid_resource_uris() {
        let before = borsh::to_vec(&released).unwrap();
        assert!(
            execute(
                &mut released,
                "set_mirror",
                &json!({"token_id":"pack","mirror_uri":uri}),
                &context("creator.testnet", 1, 5)
            )
            .is_err(),
            "mirror accepted {uri:?}"
        );
        assert_eq!(borsh::to_vec(&released).unwrap(), before);
    }
    released.check_accounting().unwrap();
}

#[test]
fn resource_uris_allow_dns_ports_paths_queries_and_enforce_utf8_byte_limit() {
    use serde_json::json;
    let max_uri = format!("https://example.org/{}", "é".repeat(246));
    assert_eq!(max_uri.len(), 512);
    for uri in [
        "https://example.org".to_string(),
        "https://cdn-1.example.org:8443/resources/pack.json?version=1&lang=en".to_string(),
        "https://xn--bcher-kva.example/pack.json".to_string(),
        max_uri.clone(),
    ] {
        let mut terms = fixture_terms("valid-uri", 50, 100);
        terms.manifest_uri = uri.clone();
        let mut state = State::new("creator.testnet");
        state
            .create(
                terms,
                "creator.testnet",
                "sunset.testnet",
                1,
                CAMPAIGN_STORAGE,
            )
            .unwrap();
        state.check_accounting().unwrap();
        let mut state = released_state();
        let before_size = state.size();
        execute(
            &mut state,
            "set_mirror",
            &json!({"token_id":"pack","mirror_uri":uri}),
            &context("creator.testnet", 1, 5),
        )
        .unwrap();
        assert_eq!(state.campaigns[0].stewardship.mirror(), uri);
        assert_eq!(state.security_deposits, 1);
        assert_eq!(state.size(), before_size);
        let oversized = format!("{max_uri}é");
        let before = borsh::to_vec(&state).unwrap();
        assert!(execute(
            &mut state,
            "set_mirror",
            &json!({"token_id":"pack","mirror_uri":oversized}),
            &context("creator.testnet", 1, 6)
        )
        .is_err());
        assert_eq!(borsh::to_vec(&state).unwrap(), before);
        state.check_accounting().unwrap();
    }
}

#[test]
fn stewardship_exists_only_after_release_and_mints_once_without_growth() {
    use serde_json::json;
    let mut state = active_state(50, 100);
    let ctx = context("viewer.testnet", 0, 4);
    assert!(
        execute(&mut state, "nft_token", &json!({"token_id":"pack"}), &ctx)
            .unwrap()
            .is_null()
    );
    state
        .contribute("pack", "buyer.testnet", 50, 50 + ACCOUNT_STORAGE, 3)
        .unwrap();
    let size = state.size();
    state.release("pack", &[7; 32], 4).unwrap();
    state.release("pack", &[7; 32], 5).unwrap();
    assert_eq!(state.size(), size);
    let token = execute(&mut state, "nft_token", &json!({"token_id":"pack"}), &ctx).unwrap();
    assert_eq!(token["owner_id"], "creator.testnet");
    assert_eq!(token["metadata"]["copies"], 1);
    assert_eq!(
        execute(&mut state, "nft_total_supply", &json!({}), &ctx).unwrap(),
        "1"
    );
    state.check_accounting().unwrap();
}

#[test]
fn stewardship_transfer_resets_mirror_without_registering_accounts_or_touching_money() {
    use serde_json::json;
    let mut state = released_state();
    let initial_size = state.size();
    let accounts = state.accounts.len();
    let creator_credit = state.account("creator.testnet").unwrap().credit;
    execute(
        &mut state,
        "set_mirror",
        &json!({"token_id":"pack","mirror_uri":"https://mirror.test/pack.json"}),
        &context("creator.testnet", 1, 5),
    )
    .unwrap();
    let recipient = "a".repeat(64);
    execute(
        &mut state,
        "nft_transfer",
        &json!({"token_id":"pack","receiver_id":recipient}),
        &context("creator.testnet", 1, 6),
    )
    .unwrap();
    assert_eq!(state.size(), initial_size);
    assert_eq!(state.accounts.len(), accounts);
    assert_eq!(
        state.account("creator.testnet").unwrap().credit,
        creator_credit
    );
    let token = execute(
        &mut state,
        "nft_token",
        &json!({"token_id":"pack"}),
        &context("viewer.testnet", 0, 7),
    )
    .unwrap();
    assert_eq!(token["owner_id"], recipient);
    let extra: serde_json::Value =
        serde_json::from_str(token["metadata"]["extra"].as_str().unwrap()).unwrap();
    assert_eq!(extra["mirror_uri"], "https://example.test/pack.json");
    assert_eq!(state.campaigns[0].escrow, 0);
    assert_eq!(
        execute(
            &mut state,
            "get_config",
            &json!({}),
            &context("viewer.testnet", 0, 7)
        )
        .unwrap()["security_deposits"],
        "2"
    );
    state.check_accounting().unwrap();
}

#[test]
fn stewardship_enumeration_metadata_and_optional_arguments_use_standard_shapes() {
    use serde_json::json;
    let mut state = released_state();
    let ctx = context("viewer.testnet", 0, 7);
    let metadata = execute(&mut state, "nft_metadata", &json!({}), &ctx).unwrap();
    assert_eq!(metadata["spec"], "nft-1.0.0");
    let tokens = execute(
        &mut state,
        "nft_tokens",
        &json!({"from_index":null,"limit":null}),
        &ctx,
    )
    .unwrap();
    assert_eq!(tokens.as_array().unwrap().len(), 1);
    assert_eq!(
        execute(
            &mut state,
            "nft_supply_for_owner",
            &json!({"account_id":"creator.testnet"}),
            &ctx
        )
        .unwrap(),
        "1"
    );
    assert_eq!(
        execute(
            &mut state,
            "nft_tokens_for_owner",
            &json!({"account_id":"creator.testnet","from_index":"1","limit":1}),
            &ctx
        )
        .unwrap(),
        json!([])
    );
    assert_eq!(
        execute(
            &mut state,
            "nft_tokens",
            &json!({"from_index":"340282366920938463463374607431768211455"}),
            &ctx
        )
        .unwrap(),
        json!([])
    );
    assert!(execute(
        &mut state,
        "nft_token",
        &json!({"token_id":"missing"}),
        &ctx
    )
    .unwrap()
    .is_null());
    assert!(execute(&mut state, "nft_token", &json!({"token_id":1}), &ctx).is_err());
    assert!(execute(&mut state, "nft_tokens", &json!({"from_index":1}), &ctx).is_err());
    assert!(execute(&mut state, "nft_tokens", &json!({"limit":0}), &ctx).is_err());
    assert!(execute(
        &mut state,
        "nft_tokens",
        &json!({"limit":1,"surprise":true}),
        &ctx
    )
    .is_err());
}

#[test]
fn stewardship_rejects_unauthorized_updates_deposits_and_invalid_arguments() {
    use serde_json::json;
    let mut state = released_state();
    let transfer = json!({"token_id":"pack","receiver_id":"next.testnet"});
    for (caller, deposit) in [
        ("attacker.testnet", 1),
        ("creator.testnet", 0),
        ("creator.testnet", 2),
    ] {
        assert!(execute(
            &mut state,
            "nft_transfer",
            &transfer,
            &context(caller, deposit, 5)
        )
        .is_err());
    }
    for args in [
        json!({"token_id":"pack","receiver_id":"INVALID"}),
        json!({"token_id":"pack","receiver_id":"next.testnet","memo":3}),
        json!({"token_id":"pack","receiver_id":"next.testnet","approval_id":"1"}),
        json!({"token_id":"pack","receiver_id":"creator.testnet"}),
    ] {
        assert!(execute(
            &mut state,
            "nft_transfer",
            &args,
            &context("creator.testnet", 1, 5)
        )
        .is_err());
    }
    assert!(execute(
        &mut state,
        "set_mirror",
        &json!({"token_id":"pack","mirror_uri":"https://evil.test/pack"}),
        &context("attacker.testnet", 1, 5)
    )
    .is_err());
    for uri in [
        "javascript:alert(1)",
        "https://",
        "https://mirror.test/\npack",
    ] {
        assert!(execute(
            &mut state,
            "set_mirror",
            &json!({"token_id":"pack","mirror_uri":uri}),
            &context("creator.testnet", 1, 5)
        )
        .is_err());
    }
    assert_eq!(
        state.account("creator.testnet").unwrap().contributions[0],
        0
    );
    state.check_accounting().unwrap();
}

#[test]
fn maximum_campaign_and_account_records_leave_stewardship_storage_prepaid() {
    use serde_json::json;
    let owner = "a".repeat(64);
    let mut state = State::new(&owner);
    for index in 0..MAX_CAMPAIGNS {
        let mut terms = fixture_terms(&format!("{index}{}", "p".repeat(63)), 99, 100);
        terms.title = "T".repeat(120);
        terms.reviewer = "r".repeat(64);
        terms.manifest_uri = format!("https://example.test/{}", "m".repeat(491));
        state
            .create(terms, &owner, "sunset.testnet", 1, CAMPAIGN_STORAGE)
            .unwrap();
    }
    let id = state.campaigns[0].terms.id.clone();
    let digest = state.campaigns[0].digest;
    state.approve(&id, &digest, &"r".repeat(64), 2).unwrap();
    for index in 0..99 {
        let account = format!("{index:064}");
        state
            .contribute(&id, &account, 1, 1 + ACCOUNT_STORAGE, 3)
            .unwrap();
    }
    let size = state.size();
    assert!(size < 65_536);
    state.release(&id, &[7; 32], 4).unwrap();
    execute(
        &mut state,
        "set_mirror",
        &json!({"token_id":id,"mirror_uri":format!("https://mirror.test/{}", "m".repeat(492))}),
        &context(&owner, 1, 5),
    )
    .unwrap();
    execute(
        &mut state,
        "nft_transfer",
        &json!({"token_id":id,"receiver_id":"next.testnet"}),
        &context(&owner, 1, 6),
    )
    .unwrap();
    assert_eq!(state.size(), size);
    assert_eq!(state.accounts.len(), MAX_ACCOUNTS);
    assert!(state.account("next.testnet").is_err());
    state.check_accounting().unwrap();
}
