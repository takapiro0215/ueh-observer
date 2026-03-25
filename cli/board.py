import sys
import observer.engine as engine


def is_valid_wallet(wallet: str) -> bool:
    return wallet.startswith("0x") and len(wallet) == 42


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

    print("[UEH OBSERVER BOARD]")
    print(f"[STATUS: {result['status']}]")
    print()

    print(f"Protocol: {result['protocol']}")
    print(f"Wallet: {result['wallet']}")
    print()

    if result["status"] == "REFUSAL":
        print("Reason: inconsistent or unavailable sources")
        if result.get("error_message"):
            print(f"Error: {result['error_message']}")
        print()
        
    elif result["status"] == "NO_POSITION":
        print("HF: N/A")
        print("Liq Distance: N/A")
        print()
        print(f"Collateral Base: {result['collateral_base']}")
        print(f"Debt Base: {result['debt_base']}")
        print()
        print("Note: collateral/debt values are Aave base units, not direct USD.")
        print()

    else:
        print(f"HF: {result['health_factor']}")
        print(f"Liq Distance: {result['liq_distance_pct']}%")
        print()
        print(f"Collateral Base: {result['collateral_base']}")
        print(f"Debt Base: {result['debt_base']}")
        print()
        print("Note: collateral/debt values are Aave base units, not direct USD.")
        print()

    print(f"Block: {result['block_number']}")
    print(f"Lag: {result['lag_blocks']}")
    print(
        f"Source: primary({result['primary_source']}) / "
        f"secondary({result['secondary_source']})"
    )


if __name__ == "__main__":
    main()