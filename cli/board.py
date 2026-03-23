from observer.engine import observe_wallet

def main():
    wallet = "0x0000000000000000000000000000000000000000"
    result = observe_wallet(wallet)

    print("[UEH OBSERVER BOARD]")
    print(f"Protocol: {result['protocol']}")
    print(f"Wallet: {result['wallet']}")
    print(f"HF: {result['health_factor']}")
    print(f"Collateral: {result['collateral_usd']}")
    print(f"Debt: {result['debt_usd']}")

if __name__ == "__main__":
    main()