def get_aave_account_data(wallet_address: str) -> dict:
    return {
        "protocol": "Aave v3",
        "wallet": wallet_address,
        "health_factor": 1.25,
        "collateral_usd": 12000.0,
        "debt_usd": 8000.0,
    }