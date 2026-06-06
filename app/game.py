from __future__ import annotations

from copy import deepcopy
from typing import Literal

Player = Literal["X", "O"]
Cell = Player | None

WIN_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


class XOGame:
    def __init__(self) -> None:
        self.board: list[Cell] = [None] * 9
        self.current_player: Player = "X"
        self.winner: Player | None = None
        self.is_draw = False

    def state(self) -> dict:
        return {
            "board": deepcopy(self.board),
            "current_player": self.current_player,
            "winner": self.winner,
            "is_draw": self.is_draw,
            "is_over": self.winner is not None or self.is_draw,
        }

    def play(self, position: int) -> dict:
        if self.winner is not None or self.is_draw:
            raise ValueError("Game is already over")

        if not 0 <= position <= 8:
            raise ValueError("Position must be between 0 and 8")

        if self.board[position] is not None:
            raise ValueError("Cell is already taken")

        self.board[position] = self.current_player

        if self._has_winner(self.current_player):
            self.winner = self.current_player
        elif all(cell is not None for cell in self.board):
            self.is_draw = True
        else:
            self.current_player = "O" if self.current_player == "X" else "X"

        return self.state()

    def _has_winner(self, player: Player) -> bool:
        return any(
            self.board[a] == self.board[b] == self.board[c] == player
            for a, b, c in WIN_LINES
        )
