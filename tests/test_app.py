from unittest.mock import Mock

import pytest
from redis.exceptions import ConnectionError

from app.app import create_app


@pytest.fixture
def app(monkeypatch):
    monkeypatch.delenv("REDIS_URL", raising=False)
    app = create_app()
    app.config["TESTING"] = True
    return app


def test_home(app):
    response = app.test_client().get("/")
    assert response.status_code == 200
    assert response.json["roll_no"] == "2301730245"


def test_health(app):
    response = app.test_client().get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "UP"


def test_version_and_message_come_from_environment(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "2.0.1")
    monkeypatch.setenv("APP_MESSAGE", "Running on Kubernetes")
    response = create_app().test_client().get("/")
    assert response.json["version"] == "2.0.1"
    assert response.json["message"] == "Running on Kubernetes"


def test_visit_count(app):
    counter = Mock()
    counter.incr.return_value = 7
    app.extensions["counter"] = counter
    response = app.test_client().get("/visits")
    assert response.status_code == 200
    assert response.json == {"visits": 7}
    counter.incr.assert_called_once_with("lab2:visits")


def test_missing_redis(app):
    assert app.test_client().get("/visits").status_code == 503


def test_redis_connection_failure(app):
    counter = Mock()
    counter.incr.side_effect = ConnectionError("offline")
    app.extensions["counter"] = counter
    response = app.test_client().get("/visits")
    assert response.status_code == 503
    assert response.json["error"] == "Redis is unavailable"
