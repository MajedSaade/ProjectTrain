import pytest

from app.game import XOGame


def test_new_game_starts_with_x():
    game = XOGame()
    state = game.state()

    assert state["board"] == [None] * 9
    assert state["current_player"] == "X"
    assert state["winner"] is None
    assert state["is_draw"] is False
    assert state["is_over"] is False


def test_play_alternates_players():
    game = XOGame()
    game.play(0)
    assert game.current_player == "O"
    game.play(1)
    assert game.current_player == "X"


def test_x_wins_top_row():
    game = XOGame()
    moves = [0, 3, 1, 4, 2]
    for move in moves:
        game.play(move)

    state = game.state()
    assert state["winner"] == "X"
    assert state["is_over"] is True


def test_draw_game():
    game = XOGame()
    moves = [0, 1, 2, 3, 4, 8, 5, 6, 7]
    for move in moves:
        game.play(move)

    state = game.state()
    assert state["winner"] is None
    assert state["is_draw"] is True
    assert state["is_over"] is True


def test_rejects_occupied_cell():
    game = XOGame()
    game.play(4)

    with pytest.raises(ValueError, match="already taken"):
        game.play(4)


def test_rejects_move_after_game_over():
    game = XOGame()
    for move in [0, 3, 1, 4, 2]:
        game.play(move)

    with pytest.raises(ValueError, match="already over"):
        game.play(8)
