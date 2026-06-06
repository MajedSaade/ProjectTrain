import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "xo-game"


def test_root_returns_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "XO Game" in response.get_data(as_text=True)


def test_create_and_play_game(client):
    create_response = client.post("/api/games")
    assert create_response.status_code == 201

    data = create_response.get_json()
    game_id = data["game_id"]
    assert data["current_player"] == "X"

    move_response = client.post(
        f"/api/games/{game_id}/move",
        json={"position": 4},
    )
    assert move_response.status_code == 200
    move_data = move_response.get_json()
    assert move_data["board"][4] == "X"
    assert move_data["current_player"] == "O"


def test_rejects_invalid_move(client):
    create_response = client.post("/api/games")
    game_id = create_response.get_json()["game_id"]

    response = client.post(
        f"/api/games/{game_id}/move",
        json={"position": 99},
    )
    assert response.status_code == 400
    assert "between 0 and 8" in response.get_json()["error"]
