#!/usr/bin/env bash
set -euo pipefail
contract_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
contract_target_dir="${CARGO_TARGET_DIR:-/tmp/sunset-cargo-target}"
CARGO_TARGET_DIR="$contract_target_dir" cargo build --locked --offline --release --target wasm32-unknown-unknown --manifest-path "$contract_dir/Cargo.toml"
mkdir -p "$contract_dir/res"
cp "$contract_target_dir/wasm32-unknown-unknown/release/sunset_contract.wasm" "$contract_dir/res/sunset_contract.wasm"
sha256sum "$contract_dir/res/sunset_contract.wasm"
