from enum import Enum
from typing import Any, Optional

from protocols.aave import get_aave_account_data


class TrustLevel(str, Enum):
    VERIFIED = "VERIFIED"
    CONSISTENT = "CONSISTENT"
    ESTIMATED = "ESTIMATED"
    DEGRADED = "DEGRADED"
    REFUSED = "REFUSED"


class ValueLayer(str, Enum):
    RAW = "RAW"
    DERIVED = "DERIVED"
    ESTIMATED = "ESTIMATED"

class StateOrigin(str, Enum):
    NONE = "NONE"
    OBSERVED = "OBSERVED"
    MARKET = "MARKET"
    SYSTEM = "SYSTEM"

def _build_observed(value: Any, trust: TrustLevel, layer: ValueLayer, reason: Optional[str] = None) -> dict:
    return {
        "value": value,
        "trust": trust.value,
        "layer": layer.value,
        "reason": reason,
    }


def _derive_trust(*observed_values: dict) -> TrustLevel:
    trusts = [v.get("trust") for v in observed_values]

    if any(t == TrustLevel.REFUSED.value for t in trusts):
        return TrustLevel.REFUSED
    if any(t == TrustLevel.DEGRADED.value for t in trusts):
        return TrustLevel.DEGRADED
    return TrustLevel.CONSISTENT


def _estimate_trust(*observed_values: dict) -> TrustLevel:
    trusts = [v.get("trust") for v in observed_values]

    if any(t == TrustLevel.REFUSED.value for t in trusts):
        return TrustLevel.REFUSED
    if any(t == TrustLevel.DEGRADED.value for t in trusts):
        return TrustLevel.DEGRADED
    return TrustLevel.ESTIMATED


def _make_raw(
    value: Any,
    *,
    primary: Optional[str],
    secondary: Optional[str],
    missing_reason: Optional[str] = None,
) -> dict:
    if primary != "ok" and secondary != "ok":
        return _build_observed(
            value=None,
            trust=TrustLevel.REFUSED,
            layer=ValueLayer.RAW,
            reason="both sources unavailable",
        )

    if value is None:
        if primary != "ok" or secondary != "ok":
            return _build_observed(
                value=None,
                trust=TrustLevel.DEGRADED,
                layer=ValueLayer.RAW,
                reason=missing_reason or "raw value missing under degraded source state",
            )

        return _build_observed(
            value=None,
            trust=TrustLevel.REFUSED,
            layer=ValueLayer.RAW,
            reason=missing_reason or "raw value missing",
        )

    if primary != "ok" or secondary != "ok":
        return _build_observed(
            value=value,
            trust=TrustLevel.DEGRADED,
            layer=ValueLayer.RAW,
            reason="one source degraded",
        )

    return _build_observed(
        value=value,
        trust=TrustLevel.VERIFIED,
        layer=ValueLayer.RAW,
    )


def _compute_no_position(collateral_base: dict, debt_base: dict) -> dict:
    trust = _derive_trust(collateral_base, debt_base)

    if trust == TrustLevel.REFUSED:
        return _build_observed(
            value=None,
            trust=TrustLevel.REFUSED,
            layer=ValueLayer.DERIVED,
            reason="cannot determine no_position",
        )

    collateral = collateral_base.get("value")
    debt = debt_base.get("value")

    if collateral is None or debt is None:
        return _build_observed(
            value=None,
            trust=TrustLevel.DEGRADED if trust == TrustLevel.DEGRADED else TrustLevel.REFUSED,
            layer=ValueLayer.DERIVED,
            reason="missing collateral/debt for no_position",
        )

    value = collateral == 0 and debt == 0

    return _build_observed(
        value=value,
        trust=trust,
        layer=ValueLayer.DERIVED,
    )


def _compute_status(no_position: dict, health_factor: dict) -> dict:
    trust = _derive_trust(no_position, health_factor)

    if trust == TrustLevel.REFUSED:
        return _build_observed(
            value="REFUSAL",
            trust=TrustLevel.REFUSED,
            layer=ValueLayer.DERIVED,
            reason="cannot determine status",
        )

    if trust == TrustLevel.DEGRADED:
        return _build_observed(
            value="DEGRADED",
            trust=TrustLevel.DEGRADED,
            layer=ValueLayer.DERIVED,
            reason="upstream degraded",
        )

    if no_position.get("value") is True:
        return _build_observed(
            value="NO_POSITION",
            trust=TrustLevel.CONSISTENT,
            layer=ValueLayer.DERIVED,
        )

    hf = health_factor.get("value")
    if hf is None:
        return _build_observed(
            value="DEGRADED",
            trust=TrustLevel.DEGRADED,
            layer=ValueLayer.DERIVED,
            reason="health_factor missing",
        )

    if hf < 1.2:
        status = "BOUNDARY_APPROACHING"
    elif hf < 1.5:
        status = "WATCH"
    else:
        status = "STABLE"

    return _build_observed(
        value=status,
        trust=TrustLevel.CONSISTENT,
        layer=ValueLayer.DERIVED,
    )

def _compute_state_origin(status: dict) -> dict:
    status_value = status.get("value")
    status_trust = status.get("trust")

    if status_trust == TrustLevel.REFUSED.value:
        return _build_observed(
            value=StateOrigin.SYSTEM.value,
            trust=TrustLevel.REFUSED,
            layer=ValueLayer.DERIVED,
            reason="state origin unavailable because status is refused",
        )

    if status_trust == TrustLevel.DEGRADED.value:
        return _build_observed(
            value=StateOrigin.SYSTEM.value,
            trust=TrustLevel.DEGRADED,
            layer=ValueLayer.DERIVED,
            reason="state origin degraded because status is degraded",
        )

    if status_value == "NO_POSITION":
        return _build_observed(
            value=StateOrigin.NONE.value,
            trust=TrustLevel.CONSISTENT,
            layer=ValueLayer.DERIVED,
            reason="no active borrow position",
        )

    if status_value == "STABLE":
        return _build_observed(
            value=StateOrigin.OBSERVED.value,
            trust=TrustLevel.CONSISTENT,
            layer=ValueLayer.DERIVED,
            reason="state is observed but direct transition path is not asserted",
        )

    if status_value in {"WATCH", "BOUNDARY_APPROACHING"}:
        return _build_observed(
            value=StateOrigin.MARKET.value,
            trust=TrustLevel.CONSISTENT,
            layer=ValueLayer.DERIVED,
            reason="boundary-near state is interpreted as market-driven",
        )

    return _build_observed(
        value=StateOrigin.SYSTEM.value,
        trust=TrustLevel.DEGRADED,
        layer=ValueLayer.DERIVED,
        reason="unknown status for state origin",
    )

def _compute_liq_distance_pct(health_factor: dict, no_position: dict) -> dict:
    no_pos_value = no_position.get("value")

    if no_pos_value is True:
        return _build_observed(
            value=None,
            trust=TrustLevel.REFUSED,
            layer=ValueLayer.DERIVED,
            reason="liq distance is not meaningful in NO_POSITION state",
        )

    trust = _derive_trust(health_factor)

    if trust == TrustLevel.REFUSED:
        return _build_observed(
            value=None,
            trust=TrustLevel.REFUSED,
            layer=ValueLayer.DERIVED,
            reason="cannot compute liq distance",
        )

    hf = health_factor.get("value")
    if hf is None:
        return _build_observed(
            value=None,
            trust=TrustLevel.DEGRADED,
            layer=ValueLayer.DERIVED,
            reason="health_factor missing",
        )

    value = round(max((hf - 1.0) * 100, 0.0), 2)

    return _build_observed(
        value=value,
        trust=trust,
        layer=ValueLayer.DERIVED,
    )

def _compute_est_usd(base_value: dict) -> dict:
    trust = _estimate_trust(base_value)

    if trust == TrustLevel.REFUSED:
        return _build_observed(
            value=None,
            trust=TrustLevel.REFUSED,
            layer=ValueLayer.ESTIMATED,
            reason="cannot estimate usd",
        )

    value = base_value.get("value")
    if value is None:
        return _build_observed(
            value=None,
            trust=TrustLevel.DEGRADED if trust == TrustLevel.DEGRADED else TrustLevel.REFUSED,
            layer=ValueLayer.ESTIMATED,
            reason="base value missing",
        )

    # Phase 1:
    # estimated USD is currently aligned with Aave base reference values.
    # This is provisional and intentionally labeled as estimate only.
    return _build_observed(
        value=value,
        trust=trust,
        layer=ValueLayer.ESTIMATED,
    )


def observe_wallet(wallet_address: str) -> dict:
    data = get_aave_account_data(wallet_address)

    primary = data.get("primary_source")
    secondary = data.get("secondary_source")

    protocol = data.get("protocol", "Aave v3")
    wallet = data.get("wallet", wallet_address)
    block_number = data.get("block_number")
    lag_blocks = data.get("lag_blocks")
    error_message = data.get("error_message")

    collateral_base = _make_raw(
        data.get("collateral_base", 0),
        primary=primary,
        secondary=secondary,
        missing_reason="collateral_base missing",
    )
    debt_base = _make_raw(
        data.get("debt_base", 0),
        primary=primary,
        secondary=secondary,
        missing_reason="debt_base missing",
    )
    health_factor = _make_raw(
        data.get("health_factor"),
        primary=primary,
        secondary=secondary,
        missing_reason="health_factor missing",
    )

    no_position = _compute_no_position(collateral_base, debt_base)
    status = _compute_status(no_position, health_factor)
    state_origin = _compute_state_origin(status)

    if no_position.get("value") is True:
        display_health_factor = _build_observed(
            value=None,
            trust=TrustLevel.REFUSED,
            layer=ValueLayer.DERIVED,
            reason="health factor is not meaningful in NO_POSITION state",
        )
        liq_distance_pct = _build_observed(
            value=None,
            trust=TrustLevel.REFUSED,
            layer=ValueLayer.DERIVED,
            reason="liq distance is not meaningful in NO_POSITION state",
        )
    else:
        display_health_factor = health_factor
        liq_distance_pct = _compute_liq_distance_pct(health_factor, no_position)

    collateral_est_usd = _compute_est_usd(collateral_base)
    debt_est_usd = _compute_est_usd(debt_base)

    return {
        # Core identity / source metadata
        "protocol": protocol,
        "wallet": wallet,
        "block_number": block_number,
        "lag_blocks": lag_blocks,
        "primary_source": primary,
        "secondary_source": secondary,
        "error_message": error_message,

        # Backward-compatible flat fields
        "status": status["value"],
        "health_factor": display_health_factor["value"],
        "liq_distance_pct": liq_distance_pct["value"],
        "collateral_base": collateral_base["value"],
        "debt_base": debt_base["value"],
        "collateral_est_usd": collateral_est_usd["value"],
        "debt_est_usd": debt_est_usd["value"],
        "state_origin": state_origin["value"],

        # Additional derived flat field
        "no_position": no_position["value"],
        "state_origin": state_origin["value"],

        # Trust / layer maps for board and future UI
        "trust_map": {
            "status": status["trust"],
            "health_factor": display_health_factor["trust"],
            "liq_distance_pct": liq_distance_pct["trust"],
            "collateral_base": collateral_base["trust"],
            "debt_base": debt_base["trust"],
            "collateral_est_usd": collateral_est_usd["trust"],
            "debt_est_usd": debt_est_usd["trust"],
            "no_position": no_position["trust"],
            "state_origin": state_origin["trust"],
        },
        
        "layer_map": {
            "status": status["layer"],
            "state_origin": state_origin["layer"],
            "health_factor": display_health_factor["layer"],
            "liq_distance_pct": liq_distance_pct["layer"],
            "collateral_base": collateral_base["layer"],
            "debt_base": debt_base["layer"],
            "collateral_est_usd": collateral_est_usd["layer"],
            "debt_est_usd": debt_est_usd["layer"],
            "no_position": no_position["layer"],
        },

        "trust_reason_map": {
            "status": status["reason"],
            "health_factor": display_health_factor["reason"],
            "liq_distance_pct": liq_distance_pct["reason"],
            "collateral_base": collateral_base["reason"],
            "debt_base": debt_base["reason"],
            "collateral_est_usd": collateral_est_usd["reason"],
            "debt_est_usd": debt_est_usd["reason"],
            "no_position": no_position["reason"],
            "state_origin": state_origin["reason"],            
        },

        # Optional nested detail for future use
        "observed": {
            "raw": {
                "collateral_base": collateral_base,
                "debt_base": debt_base,
                "health_factor": health_factor,
            },
            "derived": {
                "status": status,
                "health_factor": display_health_factor,
                "liq_distance_pct": liq_distance_pct,
                "no_position": no_position,
                "state_origin": state_origin,          
            },
            "estimated": {
                "collateral_est_usd": collateral_est_usd,
                "debt_est_usd": debt_est_usd,
            },
        },
    }

__all__ = ["observe_wallet"]