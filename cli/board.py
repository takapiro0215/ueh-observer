import sys
from observer.engine import observe_wallet

def is_valid_wallet(wallet: str) -> bool:
    return wallet.startswith("0x") and len(wallet) == 42

def main():
    if len(sys.argv) > 1:
        wallet = sys.argv[1]
    else:
        wallet = "0x0000000000000000000000000000000000000000"

    if not is_valid_wallet(wallet):
        print("[UEH OBSERVER BOARD]")
        print("Status: REFUSAL")
        print("Reason: invalid wallet address format")
        return

    result = observe_wallet(wallet)

    print("[UEH OBSERVER BOARD]")
    print(f"Protocol: {result['protocol']}")
    print(f"Wallet: {result['wallet']}")
    print()

    print(f"HF: {result['health_factor']}")
    print(f"Liq Distance: {result['liq_distance_pct']}%")
    print(f"Status: {result['status']}")

    if result["status"] == "REFUSAL":
        print("Reason: inconsistent or unavailable sources")

    print()

    print(f"Collateral: {result['collateral_usd']}")
    print(f"Debt: {result['debt_usd']}")
    print()

    print(f"Block: {result['block_number']}")
    print(f"Lag: {result['lag_blocks']}")
    print(f"Source: primary({result['primary_source']}) / secondary({result['secondary_source']})")

if __name__ == "__main__":
    main()