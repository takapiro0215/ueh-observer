from protocols.aave import get_aave_account_data

def observe_wallet(wallet_address: str) -> dict:
    data = get_aave_account_data(wallet_address)
    return data