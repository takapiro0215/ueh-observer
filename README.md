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

## Core Philosophy
- Boundary over prediction
- Refusal over uncertainty
- Observability over automation
- Survivability over convenience

## Key Features (MVP)
- High-precision board-style CLI output
- Trust & Accuracy metadata (block, lag, source)
- Refusal-based reliability model
- Non-custodial read-only architecture

## Current Implementation (Aave v3 Observer)

The current implementation connects to Aave v3 (Ethereum) and derives observer states from live on-chain data via `getUserAccountData()`.

The system transforms protocol state into interpretable observer states instead of displaying raw values.

### Observer States

- `STABLE`
- `WATCH`
- `BOUNDARY_APPROACHING`
- `DEGRADED`
- `REFUSAL`
- `NO_POSITION`

#### NO_POSITION
Represents absence of borrow positions.  
This is not "safe" — it means liquidation observation is not applicable.

#### REFUSAL
Triggered when data sources are inconsistent or unavailable.  
Observer intentionally refuses to produce misleading output.

#### DEGRADED
Observation is possible but data quality or consistency is reduced.

## Data Representation

- `Collateral Base` / `Debt Base` are **Aave base units**
- They are **NOT direct USD values**
- Conversion is intentionally not applied at this stage to preserve raw accuracy

## How to Run

From project root:

```bash
python -m cli.board
python -m cli.board 0xYourWalletAddressHere

Example Output
Example using a wallet with no borrow position:

[UEH OBSERVER BOARD]
[STATUS: NO_POSITION]

Protocol: Aave v3
Wallet: 0x0000000000000000000000000000000000000000

HF: N/A
Liq Distance: N/A

Collateral Base: 11802351761.0
Debt Base: 0.0

Note: collateral/debt values are Aave base units, not direct USD.

Block: 24733342
Lag: 0
Source: primary(ok) / secondary(ok)

Design Direction

UEH Observer is not a dashboard.

It is designed as a meaning layer over protocol state, where:

raw values are transformed into interpretable states

uncertainty is explicitly surfaced via refusal

observation is prioritized over action

Future direction includes:

Multi-protocol observation

Cross-protocol state aggregation

Observer as a reusable infrastructure layer

Status

Early-stage infrastructure implementation (Observer Layer of UEH)

Documentation

Technical specifications and contracts:

Trust & Accuracy Contract

CLI Output Specification

Observer Meaning Model

Full Specification (DOCX)

## Verification Status

- NO_POSITION state: verified using zero-address and empty wallets
- Borrow-position state: pending

Borrow-position state verification remains pending until a reproducible Aave v3 wallet with active debt is prepared.