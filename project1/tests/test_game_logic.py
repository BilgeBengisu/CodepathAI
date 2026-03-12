import ast
from pathlib import Path

from logic_utils import check_guess, get_range_for_difficulty, update_score


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_ROOT / "app.py"


def _load_app_ast():
    return ast.parse(APP_PATH.read_text(encoding="utf-8"))


def test_winning_guess():
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"
    assert "Correct" in message


def test_bugfix_hint_direction_when_guess_is_too_high():
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"
    assert "LOWER" in message


def test_bugfix_hint_direction_when_guess_is_too_low():
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message


def test_bugfix_string_secret_still_allows_win():
    # Protect against mixed int/string state glitches.
    outcome, _ = check_guess(50, "50")
    assert outcome == "Win"


def test_bugfix_string_secret_uses_numeric_comparison_for_high_guess():
    # A guess of 100 against secret 50 should be "Too High" even if secret is a string.
    outcome, _ = check_guess(100, "50")
    assert outcome == "Too High"


def test_bugfix_string_secret_uses_numeric_comparison_for_low_guess():
    outcome, _ = check_guess(25, "50")
    assert outcome == "Too Low"


def test_bugfix_difficulty_level_logic_ranges():
    assert get_range_for_difficulty("Easy") == (1, 20)
    assert get_range_for_difficulty("Normal") == (1, 100)
    assert get_range_for_difficulty("Hard") == (1, 50)
    assert get_range_for_difficulty("Unknown") == (1, 100)


def test_bugfix_update_score_win_rewards_fewer_attempts():
    assert update_score(current_score=0, outcome="Win", attempt_number=1) == 90
    assert update_score(current_score=0, outcome="Win", attempt_number=8) == 20


def test_bugfix_update_score_win_has_minimum_points_floor():
    assert update_score(current_score=0, outcome="Win", attempt_number=20) == 10


def test_bugfix_update_score_penalizes_non_winning_guesses_consistently():
    assert update_score(current_score=50, outcome="Too High", attempt_number=2) == 45
    assert update_score(current_score=50, outcome="Too Low", attempt_number=2) == 45


def test_bugfix_new_game_after_win_or_loss_resets_blocking_state():
    tree = _load_app_ast()
    new_game_if = next(
        (
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.If)
            and isinstance(node.test, ast.Name)
            and node.test.id == "new_game"
        ),
        None,
    )
    assert new_game_if is not None

    assigned = {}
    for stmt in new_game_if.body:
        if not isinstance(stmt, ast.Assign):
            continue
        for target in stmt.targets:
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Attribute)
                and isinstance(target.value.value, ast.Name)
                and target.value.value.id == "st"
                and target.value.attr == "session_state"
            ):
                assigned[target.attr] = stmt.value

    assert isinstance(assigned.get("attempts"), ast.Constant)
    assert assigned["attempts"].value == 0
    assert isinstance(assigned.get("score"), ast.Constant)
    assert assigned["score"].value == 0
    assert isinstance(assigned.get("status"), ast.Constant)
    assert assigned["status"].value == "playing"
    assert isinstance(assigned.get("history"), ast.List)
    assert assigned["history"].elts == []

    secret_value = assigned.get("secret")
    assert isinstance(secret_value, ast.Call)
    assert isinstance(secret_value.func, ast.Attribute)
    assert isinstance(secret_value.func.value, ast.Name)
    assert secret_value.func.value.id == "random"
    assert secret_value.func.attr == "randint"
    assert len(secret_value.args) == 2
    assert isinstance(secret_value.args[0], ast.Name)
    assert isinstance(secret_value.args[1], ast.Name)
    assert secret_value.args[0].id == "low"
    assert secret_value.args[1].id == "high"
