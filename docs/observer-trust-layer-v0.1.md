# Observer Trust Layer v0.1

## Purpose

UEH Observer is not a data display tool.

It is a **meaning layer over protocol state**.

To preserve meaning, Observer must explicitly distinguish:

- what is protocol truth
- what is interpretation
- what is approximation
- what cannot be safely known

This document defines how trust is represented and propagated.

---

## Core Principle

Trust is not accuracy.

Trust expresses:

> how safely a value can be treated as reality inside Observer.

This includes not only values, but also the **interpretation path**.

---

## Layer Separation

Observer separates data into three semantic layers.

### Raw (Protocol)

Values directly returned from protocol or primary source.

Examples:

- collateral_base
- debt_base
- health_factor

Properties:

- closest to protocol truth
- no interpretation beyond normalization
- may still be unusable in context

---

### Derived (Observer Meaning)

Values deterministically computed from Raw values.

Examples:

- status
- state_origin
- liq_distance_pct
- no_position

Properties:

- logically explainable
- reproducible
- dependent on upstream integrity

---

### Estimated (Convenience)

Values produced through approximation or mapping.

Examples:

- collateral_est_usd
- debt_est_usd

Properties:

- useful for human interpretation
- not protocol truth
- explicitly marked

---

## Trust Levels

### VERIFIED

Definition:
Directly confirmed by protocol data or trusted primary source.

Typical targets:
- Raw fields from protocol

Meaning:
Can be treated as protocol truth within current observation window.

---

### CONSISTENT

Definition:
Deterministically derived from upstream values using fixed rules.

Typical targets:
- status
- state_origin
- liq_distance_pct

Meaning:
Not protocol-returned, but logically consistent.

---

### ESTIMATED

Definition:
Produced via approximation or inferred mapping.

Typical targets:
- estimated USD values

Meaning:
Helpful but not authoritative.

---

### DEGRADED

Definition:
Value exists, but trust is reduced due to incomplete or inconsistent inputs.

Typical causes:
- partial source failure
- missing upstream values
- inconsistent state

Meaning:
Should be interpreted with caution.

---

### REFUSED

Definition:
Observer intentionally withholds value due to unsafe interpretation.

Typical causes:
- missing critical data
- contradictory sources
- full source failure

Meaning:
Observer refuses to fabricate certainty.

---

## Trust Propagation

Trust is attached to the **interpretation path**, not only the value.

Example:
health_factor (VERIFIED)
↓
status (CONSISTENT)
↓
state_origin (CONSISTENT)


If `health_factor` becomes DEGRADED:

- downstream values must not remain CONSISTENT

---

## Minimum Propagation Rules (v0.1)

Observer currently applies the following minimum rules:

- REFUSED propagates downstream  
- DEGRADED weakens downstream trust  
- ESTIMATED never upgrades to VERIFIED  

These rules are intentionally minimal and may be extended in future versions.

---

### Rules

1. Raw values can be:
   - VERIFIED
   - DEGRADED
   - REFUSED

2. Derived values:
   - CONSISTENT if required inputs are strong
   - DEGRADED if any required input is degraded
   - REFUSED if any required input is missing or refused

3. Estimated values:
   - at best ESTIMATED
   - never VERIFIED

4. Weakest dependency wins

5. REFUSED is terminal

---

## Meaning vs Value

Not all protocol-returned values are meaningful.

Example:

- health_factor when no_position = True

Observer behavior:

- suppress value
- mark as REFUSED
- provide reason

---

## State Model Integration

Observer states:

- NO_POSITION
- STABLE
- WATCH
- BOUNDARY_APPROACHING
- DEGRADED
- REFUSAL

---

### Important Distinction

> Protocol restricts transitions, not states.

This leads to two different mechanisms:

- User-driven transitions (borrow, repay)
- Market-driven evolution (price, interest)

---

## State Origin

Observer introduces `state_origin` to capture how a state is interpreted.

### Values

- NONE
- OBSERVED
- MARKET
- SYSTEM

---

### NONE

No active borrow position.

Mapping:
- NO_POSITION

---

### OBSERVED

State is directly observed, but transition path is not asserted.

Mapping:
- STABLE

---

### MARKET

State is interpreted as reached through market dynamics.

Mapping:
- WATCH
- BOUNDARY_APPROACHING

Interpretation:

> boundary-near states are typically reached after position creation,
> not directly through borrowing

---

### SYSTEM

State meaning depends on system condition.

Mapping:
- DEGRADED
- REFUSAL

---

## Example (Observed)
Health Factor : 1.4968 [VERIFIED] (RAW)
Status : WATCH [CONSISTENT] (DERIVED)
State Origin : MARKET [CONSISTENT] (DERIVED)
Liq Distance : 49.68% [CONSISTENT] (DERIVED)


---

## Display Policy

### VERIFIED / CONSISTENT
Display normally.

### ESTIMATED
Display with explicit labeling.

### DEGRADED
Display with warning and reason.

### REFUSED
Do not fabricate values.
Display N/A with reason.

---

## Current Limitations (v0.1)

Not yet implemented:

- multi-source quorum validation
- oracle reconciliation
- time-based freshness scoring
- historical consistency tracking
- state transition history tracking

---

## v0.1 Summary

Observer trust structure:

- Raw → protocol truth candidate
- Derived → deterministic meaning
- Estimated → convenience approximation

Trust levels:

- VERIFIED
- CONSISTENT
- ESTIMATED
- DEGRADED
- REFUSED

Additional dimension:

- state_origin for semantic interpretation of state transitions

---

## Final Principle

Observer must never collapse:

- protocol truth
- interpretation
- approximation

into a single layer.

Preserving this separation is the foundation of reliable observation.

### Source Instability Note

During live observation, RPC access occasionally returned HTTP 429
from `https://eth.llamarpc.com/`, causing REFUSAL state despite a valid live position.

This does not invalidate the observer meaning model.
It indicates a source-layer resilience issue to be addressed separately.