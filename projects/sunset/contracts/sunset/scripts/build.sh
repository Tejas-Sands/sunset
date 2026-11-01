#!/usr/bin/env bash
set -euo pipefail
contract_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
contract_target_dir="${CARGO_TARGET_DIR:-/tmp/sunset-cargo-target}"
contract_sysroot="$(rustc --print sysroot)"
contract_sysroot="$(cd -- "$contract_sysroot" && pwd -P)"
contract_rustc="$contract_sysroot/bin/rustc"
contract_rustc_version="$("$contract_rustc" --version)"
if [[ "$contract_rustc_version" != "rustc 1.96.0 "* ]]; then
  printf 'SUNSET requires installed rustc 1.96.0; found %s\n' "$contract_rustc_version" >&2
  exit 1
fi
contract_cargo_home="${CARGO_HOME:-${HOME:?HOME or CARGO_HOME must be set}/.cargo}"
contract_cargo_home="$(cd -- "$contract_cargo_home" && pwd -P)"
contract_rustflags=(
  "--remap-path-prefix=$contract_dir=/sunset-contract"
  "--remap-path-prefix=$contract_cargo_home=/cargo-cache"
  "--remap-path-prefix=$contract_sysroot=/rust-toolchain"
)
# Cargo's unit-separator encoding preserves paths containing spaces. These
# canonical flags replace ambient RUSTFLAGS/CARGO_ENCODED_RUSTFLAGS for this build.
printf -v contract_encoded_flags '%s\x1f' "${contract_rustflags[@]}"
contract_encoded_flags="${contract_encoded_flags%$'\x1f'}"
RUSTC="$contract_rustc" CARGO_HOME="$contract_cargo_home" CARGO_ENCODED_RUSTFLAGS="$contract_encoded_flags" CARGO_TARGET_DIR="$contract_target_dir" \
  cargo build --locked --offline --release --target wasm32-unknown-unknown --manifest-path "$contract_dir/Cargo.toml"
mkdir -p "$contract_dir/res"
cp "$contract_target_dir/wasm32-unknown-unknown/release/sunset_contract.wasm" "$contract_dir/res/sunset_contract.wasm"
sha256sum "$contract_dir/res/sunset_contract.wasm"
