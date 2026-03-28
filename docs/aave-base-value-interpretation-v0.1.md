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