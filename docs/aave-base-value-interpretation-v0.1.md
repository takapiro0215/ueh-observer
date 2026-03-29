# Aave Base Value Interpretation v0.1

## Background

Aave v3 exposes aggregated account data via `getUserAccountData()`.

Key outputs include:

- `totalCollateralBase`
- `totalDebtBase`
- `healthFactor`

These values are returned in Aave's internal **market reference currency**.

They are:

- not raw token balances
- not directly denominated in USD
- not tied to a single asset price feed

Instead, they represent protocol-level normalized values used internally for risk calculations.

---

## Problem Statement

While `totalCollateralBase` and `totalDebtBase` are meaningful for protocol-level evaluation,
they are easily misinterpreted as USD-equivalent values when displayed directly.

This creates a tension:

- Raw values are correct but unintuitive
- USD-like values are intuitive but potentially misleading

The Observer must resolve this without compromising accuracy.

---

## Design Principle

> Raw values must remain authoritative.  
> Interpreted values must remain explicitly non-authoritative.

The system must never collapse these two layers into a single representation.

---

## Current Implementation Decision

The Observer exposes two parallel representations:

### 1. Raw Layer (Authoritative)

```text
collateral_base
debt_base

・Directly derived from Aave protocol state
・No transformation applied
・Considered the highest-trust representation

2. Interpretation Layer (Provisional)
    collateral_est_usd
    debt_est_usd

・Currently aligned with base values (no external conversion)
・Introduced as a structural placeholder for future valuation logic
・Explicitly marked as provisional

Trust Separation

Layer           Source          Trust Level         Notes
Base	        Aave protocol	High	            Raw reference values
Estimated USD	Observer layer	Low	Provisional     interpretation

The two layers must never be conflated.

UI Representation Rules

The CLI board must follow:

1.Display base values first
2.Display estimated values second
3.Clearly label estimated values as provisional
4.Include explanatory note

Example:
Collateral Base: 11802351761.0
Debt Base: 0.0

Collateral (est USD): 11802351761.0
Debt (est USD): 0.0

Note: base values are raw Aave reference units. Estimated USD values are provisional and should be treated as reference only.

Known Limitations
・Estimated USD values are not true USD conversions
・No price oracle or external data source is used
・Base units may vary depending on Aave market configuration
・Large values (e.g., zero-address) may appear counterintuitive

Future Direction
The following steps are required before upgrading est USD:

1. Reference Currency Clarification

・Identify Aave base currency definition
・Confirm scaling and decimals

2. Normalization Layer

・Determine whether base values require scaling adjustment
・Validate consistency across markets

3. Optional Pricing Integration

・Evaluate using Aave oracle or external price feeds
・Ensure separation from raw trust layer

4. Trust Upgrade Path

・Define criteria for promoting est USD from provisional to defined interpretation
・Introduce explicit trust metadata if needed

Key Principle

The Observer does not convert values blindly.
It exposes the boundary between raw state and interpretation.

Summary

・Aave base values are protocol-normalized reference values
・They are preserved as the authoritative observation layer
・Estimated USD values are introduced structurally, not semantically
・Trust separation is explicit and intentional
・Future upgrades will not compromise raw state integrity
・HF = 1.5 represents the protocol-enforced safety boundary.