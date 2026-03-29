# UEH Observer

## Overview
UEH Observer is the Observer Layer of the UEH (Universal Exchange Adapters) design philosophy.

UEH Observer is a read-only observer infrastructure designed to visualize DeFi risk boundaries and on-chain state with verifiable accuracy.

This system does NOT:
- Execute transactions
- Provide financial advice
- Optimize positions
- Act as a trading bot

It only exposes state, boundaries, and trust metadata.

---

## Core Philosophy

- Boundary over prediction  
- Refusal over uncertainty  
- Observability over automation  
- Survivability over convenience  

---

## Core Concept

UEH Observer is not a dashboard.

It is a **meaning layer over protocol state**.

It separates:

- Raw protocol data  
- Derived observer meaning  
- Estimated convenience values  

And attaches explicit trust semantics to each.

---

## Current Implementation (Aave v3 Observer)

The current implementation connects to Aave v3 (Ethereum) and derives observer states from live on-chain data via:

getUserAccountData()

Instead of exposing raw protocol values directly,  
Observer transforms them into **interpretable state representations**.

---

## Observer States

- `NO_POSITION`
- `STABLE`
- `WATCH`
- `BOUNDARY_APPROACHING`
- `DEGRADED`
- `REFUSAL`

---

### NO_POSITION
Represents absence of borrow positions.

This does NOT mean "safe".  
It means liquidation risk is not applicable.

In this state:
- Health Factor is not meaningful
- Liquidation Distance is not meaningful

---

### STABLE
Position is within a protocol-safe operating range.

This state is:
- reachable via user actions (borrow/supply)
- maintained under stable conditions

---

### WATCH
Represents a **low-health region near the protocol safety boundary**.

Important:

- WATCH is **empirically observable**
- It is typically **not reached directly via borrow actions**
- It is reached through **market dynamics**, such as:
  - price movement
  - interest accrual

Therefore:

> WATCH is a **market-driven reachable state**, not purely user-driven.

---

### BOUNDARY_APPROACHING
Represents a deeper boundary-near region (lower HF threshold).

- Semantically valid
- Not yet fully empirically confirmed in current verification
- Expected to behave similarly to WATCH under stronger stress

---

### DEGRADED
Observation is possible but data quality is reduced.

Causes may include:
- partial source failure
- lag inconsistencies
- missing upstream values

---

### REFUSAL
Observer intentionally refuses to produce output.

Triggered when:
- sources are inconsistent
- required data is missing
- interpretation would be unsafe

> Refusal is a design feature, not an error.

---

## State Transition Model

Observer distinguishes between:

- **User-driven transitions** (borrow, repay, supply)
- **Market-driven transitions** (price, interest)

Key principle:

> The protocol restricts transitions, not states.

Example:

- User cannot borrow into unsafe HF range
- But market movement can push HF into WATCH

---

## Data Representation

Observer separates data into three layers:

### Raw (Protocol)
Direct values returned from protocol:

- collateral_base  
- debt_base  
- health_factor  

These are:
- protocol-native units
- not normalized to USD

---

### Derived (Observer Meaning)

- status  
- liq_distance_pct  
- no_position  

These are:
- deterministic interpretations of Raw values
- logically consistent transformations

---

### Estimated (Convenience)

- collateral_est_usd  
- debt_est_usd  

These are:
- approximations
- not protocol truth
- explicitly marked as estimated

---

## Trust Model (v0.1)

Each value is annotated with a trust level:

- `VERIFIED` → directly from protocol  
- `CONSISTENT` → derived deterministically  
- `ESTIMATED` → approximation  
- `DEGRADED` → partially unreliable  
- `REFUSED` → intentionally not provided  

Key principle:

> Trust applies to the interpretation path, not just the value.

---

## CLI Output

The board displays:

- Value
- Trust level
- Layer (RAW / DERIVED / ESTIMATED)

Example:

Health Factor : 1.49 [VERIFIED] (RAW)
Status : WATCH [CONSISTENT] (DERIVED)
Liq Distance : 49.15% [CONSISTENT] (DERIVED)


---

## Important Notes

- Base values are **not USD**
- Estimated values are **not authoritative**
- Some protocol-returned values may be **suppressed** if not meaningful (e.g., HF in NO_POSITION)

---

## How to Run

From project root:

```bash
python -m cli.board
python -m cli.board 0xYourWalletAddressHere

Example Output

[UEH OBSERVER BOARD]
[STATUS: WATCH] [CONSISTENT] (DERIVED)

Protocol: Aave v3
Wallet: 0x...

[Raw]
Collateral Base     : 2394164743.00      [VERIFIED] (RAW)
Debt Base           : 1332355049.00      [VERIFIED] (RAW)
Health Factor       : 1.49               [VERIFIED] (RAW)

[Derived]
Status              : WATCH              [CONSISTENT] (DERIVED)
Liq Distance        : 49.15%             [CONSISTENT] (DERIVED)

[Estimated]
Collateral est USD  : 2394164743.00      [ESTIMATED] (ESTIMATED)

Design Direction

UEH Observer is not a dashboard.
It is:

・a semantic layer over protocol state
・a boundary-aware observer
・a trust-explicit system

Future direction includes:

・Multi-protocol observation
・Cross-protocol aggregation
・Observer as infrastructure layer

Verification Status

・NO_POSITION state: verified
・STABLE state: verified
・WATCH state: empirically observed (market-driven transition confirmed)
・BOUNDARY_APPROACHING: not yet fully verified

Summary
UEH Observer has reached:

Working Observer
→ Meaningful Observer
→ Reality-aligned Observer

Current focus:
Formalizing trust, boundaries, and meaning across protocol and market behavior


---

## 今回のREADMEのポイント

今回の更新で特に重要なのはこの3つです：

### ① WATCHの再定義（最重要）
- 到達可能
- ただし **市場経由**

---

### ② 「遷移 vs 状態」の分離
```text
Protocol controls transitions
Market determines state evolution