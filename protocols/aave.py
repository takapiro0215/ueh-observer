def get_aave_account_data(wallet_address: str) -> dict:
    wallet = wallet_address.lower()

    if wallet == "0x1111111111111111111111111111111111111111":
        health_factor = 1.25
        collateral_usd = 12000.0
        debt_usd = 8000.0

    elif wallet == "0x3333333333333333333333333333333333333333":
        health_factor = 1.10
        collateral_usd = 10000.0
        debt_usd = 9000.0

    else:
        health_factor = 1.75
        collateral_usd = 15000.0
        debt_usd = 7000.0

    return {
        "protocol": "Aave v3",
        "wallet": wallet_address,
        "health_factor": health_factor,
        "collateral_usd": collateral_usd,
        "debt_usd": debt_usd,
        "block_number": 19283746,
        "lag_blocks": 0,
        "primary_source": "ok",
        "secondary_source": "ok",
    }