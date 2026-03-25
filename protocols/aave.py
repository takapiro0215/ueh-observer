from web3 import Web3

RPC_URL = "https://eth.llamarpc.com"
AAVE_V3_POOL = "0x87870Bca3F3fD6335C3f4ce8392D69350B4fA4E2"

POOL_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "user", "type": "address"}],
        "name": "getUserAccountData",
        "outputs": [
            {"internalType": "uint256", "name": "totalCollateralBase", "type": "uint256"},
            {"internalType": "uint256", "name": "totalDebtBase", "type": "uint256"},
            {"internalType": "uint256", "name": "availableBorrowsBase", "type": "uint256"},
            {"internalType": "uint256", "name": "currentLiquidationThreshold", "type": "uint256"},
            {"internalType": "uint256", "name": "ltv", "type": "uint256"},
            {"internalType": "uint256", "name": "healthFactor", "type": "uint256"},
        ],
        "stateMutability": "view",
        "type": "function",
    }
]

w3 = Web3(Web3.HTTPProvider(RPC_URL))
pool = w3.eth.contract(
    address=Web3.to_checksum_address(AAVE_V3_POOL),
    abi=POOL_ABI,
)


def get_aave_account_data(wallet_address: str) -> dict:
    try:
        wallet = Web3.to_checksum_address(wallet_address)
        block_number = w3.eth.block_number
        account_data = pool.functions.getUserAccountData(wallet).call()

        total_collateral_base = account_data[0]
        total_debt_base = account_data[1]
        health_factor_raw = account_data[5]

        if health_factor_raw == 0:
            health_factor = None
        else:
            health_factor = health_factor_raw / 10**18

        collateral_base = float(total_collateral_base)
        debt_base = float(total_debt_base)

        return {
            "protocol": "Aave v3",
            "wallet": wallet,
            "health_factor": round(health_factor, 4) if health_factor is not None else None,
            "collateral_base": collateral_base,
            "debt_base": debt_base,
            "block_number": block_number,
            "lag_blocks": 0,
            "primary_source": "ok",
            "secondary_source": "ok",
            "error_message": None,
        }

    except Exception as e:
        return {
            "protocol": "Aave v3",
            "wallet": wallet_address,
            "health_factor": None,
            "collateral_base": None,
            "debt_base": None,
            "block_number": None,
            "lag_blocks": None,
            "primary_source": "error",
            "secondary_source": "error",
            "error_message": f"{type(e).__name__}: {e}",
        }