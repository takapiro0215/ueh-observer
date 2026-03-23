from protocols.aave import get_aave_account_data

def observe_wallet(wallet_address: str) -> dict:
    data = get_aave_account_data(wallet_address)

    hf = data["health_factor"]
    primary = data["primary_source"]
    secondary = data["secondary_source"]

    # REFUSAL condition
    if primary != "ok" and secondary != "ok":
        data["status"] = "REFUSAL"
        data["liq_distance_pct"] = None
        data["health_factor"] = None
        data["collateral_usd"] = None
        data["debt_usd"] = None
        return data

    # DEGRADED condition
    if primary != "ok" or secondary != "ok":
        status = "DEGRADED"
    elif hf is None:
        status = "UNKNOWN"
    elif hf < 1.2:
        status = "BOUNDARY_APPROACHING"
    elif hf < 1.5:
        status = "WATCH"
    else:
        status = "STABLE"

    if hf is None:
        liq_distance = None
    else:
        liq_distance = round((hf - 1.0) * 100, 2)

    data["status"] = status
    data["liq_distance_pct"] = liq_distance
    return data