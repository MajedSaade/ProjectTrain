import uuid

from flask import Flask, jsonify, render_template_string, request

from app.game import XOGame

_games: dict[str, XOGame] = {}

INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>XO Game</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 420px; margin: 2rem auto; text-align: center; }
    h1 { margin-bottom: 0.25rem; }
    #status { min-height: 1.5rem; margin: 1rem 0; font-weight: 600; }
    #board { display: grid; grid-template-columns: repeat(3, 100px); gap: 8px; justify-content: center; }
    button.cell {
      width: 100px; height: 100px; font-size: 2.5rem; font-weight: bold;
      border: 2px solid #333; background: #f8f8f8; cursor: pointer;
    }
    button.cell:disabled { cursor: not-allowed; opacity: 0.85; }
    #reset { margin-top: 1rem; padding: 0.6rem 1.2rem; font-size: 1rem; cursor: pointer; }
  </style>
</head>
<body>
  <h1>XO Game</h1>
  <p>Tic-tac-toe in your CI/CD sandbox</p>
  <div id="status">Loading...</div>
  <div id="board"></div>
  <button id="reset" type="button">New Game</button>
  <script>
    let gameId = null;

    async function api(path, options = {}) {
      const response = await fetch(path, {
        headers: { "Content-Type": "application/json" },
        ...options,
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Request failed");
      return data;
    }

    function render(state) {
      const status = document.getElementById("status");
      const board = document.getElementById("board");
      board.innerHTML = "";

      if (state.winner) status.textContent = `Player ${state.winner} wins!`;
      else if (state.is_draw) status.textContent = "Draw!";
      else status.textContent = `Player ${state.current_player}'s turn`;

      state.board.forEach((cell, index) => {
        const button = document.createElement("button");
        button.className = "cell";
        button.textContent = cell || "";
        button.disabled = state.is_over || cell !== null;
        button.addEventListener("click", () => move(index));
        board.appendChild(button);
      });
    }

    async function newGame() {
      const state = await api("/api/games", { method: "POST" });
      gameId = state.game_id;
      render(state);
    }

    async function move(position) {
      const state = await api(`/api/games/${gameId}/move`, {
        method: "POST",
        body: JSON.stringify({ position }),
      });
      render(state);
    }

    document.getElementById("reset").addEventListener("click", newGame);
    newGame();
  </script>
</body>
</html>
"""


def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/")
    def root():
        return render_template_string(INDEX_HTML)

    @app.route("/health")
    def health():
        return jsonify(status="ok", service="xo-game"), 200

    @app.post("/api/games")
    def create_game():
        game_id = str(uuid.uuid4())
        _games[game_id] = XOGame()
        return jsonify(game_id=game_id, **_games[game_id].state()), 201

    @app.get("/api/games/<game_id>")
    def get_game(game_id: str):
        game = _games.get(game_id)
        if game is None:
            return jsonify(error="Game not found"), 404
        return jsonify(game_id=game_id, **game.state()), 200

    @app.post("/api/games/<game_id>/move")
    def play_move(game_id: str):
        game = _games.get(game_id)
        if game is None:
            return jsonify(error="Game not found"), 404

        payload = request.get_json(silent=True) or {}
        position = payload.get("position")
        if position is None:
            return jsonify(error="position is required"), 400

        try:
            state = game.play(int(position))
        except (TypeError, ValueError) as exc:
            return jsonify(error=str(exc)), 400

        return jsonify(game_id=game_id, **state), 200

    return app
