from protocols.aave import get_aave_account_data


def observe_wallet(wallet_address: str) -> dict:
    data = get_aave_account_data(wallet_address)

    hf = data.get("health_factor")
    primary = data.get("primary_source")
    secondary = data.get("secondary_source")
    debt = data.get("debt_base", 0)
    collateral = data.get("collateral_base", 0)

    if primary != "ok" and secondary != "ok":
        return {
            "status": "REFUSAL",
            "protocol": data.get("protocol", "Aave v3"),
            "wallet": data.get("wallet", wallet_address),
            "health_factor": None,
            "liq_distance_pct": None,
            "collateral_base": None,
            "debt_base": None,
            "block_number": data.get("block_number"),
            "lag_blocks": data.get("lag_blocks"),
            "primary_source": primary,
            "secondary_source": secondary,
        }

    if debt == 0:
        return {
            "status": "NO_POSITION",
            "protocol": data.get("protocol", "Aave v3"),
            "wallet": data.get("wallet", wallet_address),
            "health_factor": None,
            "liq_distance_pct": None,
            "collateral_base": collateral,
            "debt_base": debt,
            "block_number": data.get("block_number"),
            "lag_blocks": data.get("lag_blocks"),
            "primary_source": primary,
            "secondary_source": secondary,
        }

    if primary != "ok" or secondary != "ok":
        status = "DEGRADED"
    elif hf is None:
        status = "DEGRADED"
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

    return {
        "status": status,
        "protocol": data.get("protocol", "Aave v3"),
        "wallet": data.get("wallet", wallet_address),
        "health_factor": hf,
        "liq_distance_pct": liq_distance,
        "collateral_base": collateral,
        "debt_base": debt,
        "block_number": data.get("block_number"),
        "lag_blocks": data.get("lag_blocks"),
        "primary_source": primary,
        "secondary_source": secondary,
    }


__all__ = ["observe_wallet"]