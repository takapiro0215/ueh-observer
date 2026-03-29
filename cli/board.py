import sys

import observer.engine as engine


def is_valid_wallet(wallet: str) -> bool:
    return wallet.startswith("0x") and len(wallet) == 42


def _safe_get(mapping: dict, key: str, default=None):
    if not isinstance(mapping, dict):
        return default
    return mapping.get(key, default)


def _fmt_value(value):
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def _fmt_percent(value):
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.2f}%"
    return f"{value}%"


def _fmt_trust(result: dict, field: str) -> str:
    trust = _safe_get(result.get("trust_map", {}), field, "N/A")
    return f"[{trust}]"


def _fmt_layer(result: dict, field: str) -> str:
    layer = _safe_get(result.get("layer_map", {}), field, "N/A")
    return f"({layer})"


def _fmt_reason(result: dict, field: str) -> str:
    reason = _safe_get(result.get("trust_reason_map", {}), field)
    if reason:
        return f" - {reason}"
    return ""


def _line(label: str, value_text: str, trust_text: str, layer_text: str, reason_text: str = "") -> str:
    return f"{label:<20}: {value_text:<18} {trust_text} {layer_text}{reason_text}"


def _render_field(result: dict, label: str, field: str, formatter=None) -> str:
    value = result.get(field)
    value_text = formatter(value) if formatter else _fmt_value(value)
    trust_text = _fmt_trust(result, field)
    layer_text = _fmt_layer(result, field)
    reason_text = _fmt_reason(result, field)
    return _line(label, value_text, trust_text, layer_text, reason_text)


def _status_note(status: str) -> str:
    notes = {
        "NO_POSITION": "No active debt position. Observer sees no borrow-based risk state.",
        "STABLE": "Position is inside the currently observable protocol-safe operating range.",
        "WATCH": "Near the protocol safety boundary.",
        "BOUNDARY_APPROACHING": "Approaching liquidation boundary.",
        "DEGRADED": "Observation is degraded due to incomplete source integrity.",
        "REFUSAL": "Observer refused unsafe interpretation due to source failure or inconsistency.",
    }
    return notes.get(status, "")


def main():
    if len(sys.argv) > 1:
        wallet = sys.argv[1]
    else:
        wallet = "0x0000000000000000000000000000000000000000"

    if not is_valid_wallet(wallet):
        print("[UEH OBSERVER BOARD]")
        print("[STATUS: REFUSAL]")
        print()
        print("Reason: invalid wallet address format")
        return

    result = engine.observe_wallet(wallet)

    status = result.get("status", "REFUSAL")

    print("[UEH OBSERVER BOARD]")
    print(f"[STATUS: {status}] {_fmt_trust(result, 'status')} {_fmt_layer(result, 'status')}")
    status_reason = _fmt_reason(result, "status")
    if status_reason:
        print(f"Status Detail{status_reason}")
    print()

    print(f"Protocol: {result.get('protocol')}")
    print(f"Wallet: {result.get('wallet')}")
    print()

    print("[Raw]")
    print(_render_field(result, "Collateral Base", "collateral_base"))
    print(_render_field(result, "Debt Base", "debt_base"))
    print(_render_field(result, "Health Factor", "health_factor"))
    print()

    print("[Derived]")
    print(_render_field(result, "Status", "status"))
    print(_render_field(result, "Liq Distance", "liq_distance_pct", _fmt_percent))
    print(_render_field(result, "No Position", "no_position"))
    print()

    print("[Estimated]")
    print(_render_field(result, "Collateral est USD", "collateral_est_usd"))
    print(_render_field(result, "Debt est USD", "debt_est_usd"))
    print()

    note = _status_note(status)
    if note:
        print(f"Status Note: {note}")
        print()

    if status == "REFUSAL":
        print("Reason: inconsistent or unavailable sources")
        if result.get("error_message"):
            print(f"Error: {result['error_message']}")
        print()

    print("Note:")
    print("Raw       = protocol-returned values")
    print("Derived   = Observer interpretation from upstream values")
    print("Estimated = provisional convenience values, not protocol truth")
    print()

    print(f"Block: {result.get('block_number')}")
    print(f"Lag: {result.get('lag_blocks')}")
    print(
        f"Source: primary({result.get('primary_source')}) / "
        f"secondary({result.get('secondary_source')})"
    )

    if result.get("error_message"):
        print(f"Error Message: {result['error_message']}")


if __name__ == "__main__":
    main()