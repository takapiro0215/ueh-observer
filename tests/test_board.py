from observer.domain.models import ObserverState
from observer.domain.status import ObserverStatus
from observer.ui.board import render_board


def test_board_renders_na_for_no_position_metrics():
    state = ObserverState(
        status=ObserverStatus.NO_POSITION,
        total_collateral=1000.0,
        total_debt=0.0,
        health_factor=None,
        liq_distance=None,
        message="No active borrow position",
    )

    board = render_board(state)

    assert "[STATUS] NO_POSITION" in board
    assert "Health Factor: N/A" in board
    assert "Liq Distance: N/A" in board
    assert "No active borrow position" in board