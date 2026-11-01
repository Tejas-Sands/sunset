"""Reproduce illustrative research cash flows, not contract behavior or demand."""

from decimal import Decimal
from pathlib import Path
import argparse
import csv
import io


SCENARIOS = (
    ("zero_orders_expire", "8", "0.8", "0.2", 0, "underfunded_expired"),
    ("five_orders_expire", "8", "0.8", "0.2", 5, "underfunded_expired"),
    ("nine_orders_expire", "8", "0.8", "0.2", 9, "underfunded_expired"),
    ("fully_funded_before_release", "8", "0.8", "0.2", 10, "awaiting_release"),
    ("ten_orders_release", "8", "0.8", "0.2", 10, "released"),
    ("ten_orders_miss_release", "8", "0.8", "0.2", 10, "release_expired"),
    ("partial_final_release", "7.5", "0.8", "0.2", 10, "released"),
    ("partial_final_miss_release", "7.5", "0.8", "0.2", 10, "release_expired"),
    ("smaller_buyout_allocation", "8", "0.4", "0.2", 20, "released"),
    ("very_small_buyout_allocation", "8", "0.1", "0.2", 80, "released"),
)


def scenario(name, target_text, buyout_text, service_text, count, outcome):
    target, buyout, service = map(Decimal, (target_text, buyout_text, service_text))
    assert target > 0 and buyout > 0 and service >= 0 and count >= 0
    assert outcome in {"released", "awaiting_release", "underfunded_expired", "release_expired"}
    collected = Decimal(0)
    for _ in range(count):
        assert collected < target, "This model does not accept orders after the cap."
        collected += min(buyout, target - collected)
    if outcome == "underfunded_expired":
        assert collected < target
    else:
        assert collected == target
    deposits = count * (buyout + service)
    earned = count * service
    change = deposits - earned - collected
    creator = collected if outcome == "released" else Decimal(0)
    refund = collected if outcome.endswith("expired") else Decimal(0)
    escrow = collected if outcome == "awaiting_release" else Decimal(0)
    assert deposits == earned + change + creator + refund + escrow
    return {
        "scenario": name,
        "target": target,
        "max_buyout_per_order": buyout,
        "service_per_order": service,
        "accepted_orders": count,
        "outcome": outcome,
        "economic_deposits": deposits,
        "buyout_collected": collected,
        "service_earned": earned,
        "buyer_change": change,
        "creator_credit": creator,
        "buyout_refund_entitlement": refund,
        "buyout_escrow": escrow,
    }


def csv_text():
    rows = [scenario(*values) for values in SCENARIOS]
    by_name = {row["scenario"]: row for row in rows}
    assert by_name["five_orders_expire"]["buyout_refund_entitlement"] == Decimal("4")
    assert by_name["ten_orders_release"]["creator_credit"] == Decimal("8")
    assert by_name["ten_orders_miss_release"]["creator_credit"] == 0
    assert by_name["partial_final_release"]["buyer_change"] == Decimal("0.5")
    assert by_name["fully_funded_before_release"]["buyout_escrow"] == Decimal("8")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: format(value, "f") if isinstance(value, Decimal) else value
                         for key, value in row.items()})
    return output.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the saved CSV without rewriting it")
    arguments = parser.parse_args()
    destination = Path(__file__).with_name("economic_scenarios.csv")
    expected = csv_text()
    if arguments.check:
        assert destination.read_text() == expected, "Scenario CSV differs; regenerate and review."
        print(f"Verified {len(SCENARIOS)} illustrative scenarios and their accounting identities.")
    else:
        destination.write_text(expected)
        print(f"Wrote {len(SCENARIOS)} illustrative scenarios to {destination.name}.")


if __name__ == "__main__":
    main()
