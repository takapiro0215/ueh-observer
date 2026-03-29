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

It is a meaning layer over protocol state.

It separates:

- Raw protocol data
- Derived observer meaning
- Estimated convenience values

And attaches explicit trust semantics to each.

---

## Current Implementation (Aave v3 Observer)

The current implementation connects to Aave v3 (Ethereum) and derives observer states from live on-chain data via:

`getUserAccountData()`

Instead of exposing raw protocol values directly, Observer transforms them into interpretable state representations.

---

## Observer States

- `NO_POSITION`
- `STABLE`
- `WATCH`
- `BOUNDARY_APPROACHING`
- `DEGRADED`
- `REFUSAL`

### NO_POSITION
Represents absence of borrow positions.

This does NOT mean "safe".  
It means liquidation risk is not applicable.

In this state:
- Health Factor is not meaningful
- Liquidation Distance is not meaningful

### STABLE
Position is within a protocol-safe operating range.

This state is directly observable, but Observer does not currently assert whether it was reached by fresh user action or maintained through later market movement.

### WATCH
Represents a low-health region near the protocol safety boundary.

Important:

- WATCH is empirically observable
- Aave may restrict additional borrowing into this region
- However, an already-open position can move into WATCH through market dynamics

Examples:
- collateral price movement
- debt growth
- interest accrual

Therefore:

> WATCH is treated as a market-driven reachable state.

### BOUNDARY_APPROACHING

Represents a deeper boundary-near region with lower health factor.

This state is:

- semantically defined
- not yet empirically observed
- expected to be primarily market-driven

Important:

- Under current protocol constraints, this state may not be directly reachable through additional borrow actions
- It is expected to be reached through post-position market dynamics, such as:
  - collateral price decline
  - debt growth over time
  - interest accrual

Therefore:

> BOUNDARY_APPROACHING is treated as a market-driven boundary state,
> and may be observable rather than actively reachable.

This distinction is important for interpreting boundary behavior:

- `WATCH` can be approached through user action or market movement
- `BOUNDARY_APPROACHING` may require market-driven deterioration to be observed

### DEGRADED
Observation is possible but data quality is reduced.

Causes may include:
- partial source failure
- lag inconsistencies
- missing upstream values

### REFUSAL
Observer intentionally refuses to produce output.

Triggered when:
- sources are inconsistent
- required data is missing
- interpretation would be unsafe

Refusal is a design feature, not an error.

---

## State Origin

Observer distinguishes not only state, but also the semantic origin of that state.

Possible values:

- `NONE`
- `OBSERVED`
- `MARKET`
- `SYSTEM`

### NONE
No active borrow position exists, so state-transition origin is not applicable.

Typical mapping:
- `NO_POSITION`

### OBSERVED
The state is directly observed, but the transition path is not asserted.

Typical mapping:
- `STABLE`

This is intentionally conservative.
Observer does not currently claim whether the position was created by immediate user action or remained stable through later market evolution.

### MARKET
The state is interpreted as reached through post-position market dynamics.

Typical mapping:
- `WATCH`
- `BOUNDARY_APPROACHING`

This reflects the current verified understanding that boundary-near states may be observed after position creation due to market movement, rather than direct borrowing into that exact state.

### SYSTEM
The state meaning depends on source/system condition rather than protocol-market behavior.

Typical mapping:
- `DEGRADED`
- `REFUSAL`

---

## State Transition Model

Observer distinguishes between:

- User-constrained protocol transitions
- Market-driven state evolution

Key principle:

> The protocol restricts transitions, not states.

Example:

- A user may be prevented from borrowing into a lower-HF boundary region
- But a live position can later drift into that region through market movement

This distinction is important for interpreting `WATCH` and future `BOUNDARY_APPROACHING` observations.

---

## Data Representation

Observer separates data into three layers:

### Raw (Protocol)
Direct values returned from protocol:

- `collateral_base`
- `debt_base`
- `health_factor`

These are:
- protocol-native values
- closest to protocol truth
- not normalized to USD

### Derived (Observer Meaning)
Values computed deterministically from Raw values:

- `status`
- `state_origin`
- `liq_distance_pct`
- `no_position`

These are:
- Observer-side interpretations
- deterministic and explainable
- dependent on upstream integrity

### Estimated (Convenience)
Values computed as convenience approximations:

- `collateral_est_usd`
- `debt_est_usd`

These are:
- not protocol truth
- provisional
- explicitly labeled as estimated

---

## Trust Model (v0.1)

Each value is annotated with a trust level:

- `VERIFIED`   → directly from protocol
- `CONSISTENT` → deterministically derived
- `ESTIMATED`  → approximate value
- `DEGRADED`   → partially unreliable
- `REFUSED`    → intentionally withheld

Key principle:

> Trust applies to the interpretation path, not only to the value itself.

This prevents Observer from collapsing protocol fact, semantic interpretation, and convenience approximation into a single layer.

---

## CLI Output

The board displays:

- Value
- Trust level
- Layer (`RAW` / `DERIVED` / `ESTIMATED`)

Example:

```text
Health Factor   : 1.4968      [VERIFIED] (RAW)
Status          : WATCH       [CONSISTENT] (DERIVED)
State Origin    : MARKET      [CONSISTENT] (DERIVED)
Liq Distance    : 49.68%      [CONSISTENT] (DERIVED)

Important Notes
・Base values are not direct USD values
・Estimated values are not authoritative
・Some protocol-returned values may be intentionally suppressed when not meaningful
・Example: health_factor is not displayed as meaningful in NO_POSITION

How to Run
From project root:

    python -m cli.board
    python -m cli.board 0xYourWalletAddressHere

Example Output

[UEH OBSERVER BOARD]
[STATUS: WATCH] [CONSISTENT] (DERIVED)

Protocol: Aave v3
Wallet: 0x...

[Raw]
Collateral Base     : 2402755968.00      [VERIFIED] (RAW)
Debt Base           : 1332359448.00      [VERIFIED] (RAW)
Health Factor       : 1.4968             [VERIFIED] (RAW)

[Derived]
Status              : WATCH              [CONSISTENT] (DERIVED)
State Origin        : MARKET             [CONSISTENT] (DERIVED)
Liq Distance        : 49.68%             [CONSISTENT] (DERIVED)
No Position         : False              [CONSISTENT] (DERIVED)

[Estimated]
Collateral est USD  : 2402755968.00      [ESTIMATED] (ESTIMATED)
Debt est USD        : 1332359448.00      [ESTIMATED] (ESTIMATED)

Design Direction

UEH Observer is not a dashboard.

It is:

・a semantic layer over protocol state
・a boundary-aware observer
・a trust-explicit system
・a state-origin-aware observer model

Future direction includes:

・Multi-protocol observation
・Cross-protocol aggregation
・Observer as reusable infrastructure layer
・Stronger trust propagation rules
・Richer boundary verification

## Verification Status

・NO_POSITION: verified
・STABLE: verified
・WATCH: empirically observed
・WATCH as market-driven boundary-near state: confirmed
・BOUNDARY_APPROACHING: semantically defined, not yet empirically observed
・REFUSAL / DEGRADED: verified through source-failure handling

Market-Driven Reachability

Observer distinguishes between:

・user-driven reachable states
・market-driven reachable states

Important observation:
Not all states defined in the model are directly reachable through user actions.

In particular:

・WATCH may be approached through both user actions and market dynamics
・BOUNDARY_APPROACHING is expected to be primarily market-driven

Under protocol constraints:

・additional borrowing may be restricted before reaching deeper boundary regions
・therefore, certain states may only be observed through post-position deterioration

This leads to a key distinction:

・Some states are reachable
・Some states are observable only

Observer explicitly preserves this distinction.

Summary
UEH Observer has progressed through the following stages:
Working Observer
→ Meaningful Observer
→ Reality-aligned Observer

Current status:

・State model: aligned with protocol behavior
・Trust model: explicitly defined and propagated
・State origin: integrated into interpretation
・Boundary semantics: defined and partially verified

Current focus:

Formalizing trust, state origin, and boundary meaning under real market conditions.