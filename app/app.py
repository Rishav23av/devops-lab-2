import os

from flask import Flask, jsonify
from redis import Redis
from redis.exceptions import RedisError


def create_app():
    app = Flask(__name__)
    app.config.update(
        APP_VERSION=os.getenv("APP_VERSION", "2.0.0"),
        APP_MESSAGE=os.getenv("APP_MESSAGE", "Rishav's containerized DevOps app"),
    )
    redis_url = os.getenv("REDIS_URL")
    counter = Redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2) if redis_url else None
    app.extensions["counter"] = counter

    @app.get("/")
    def home():
        return jsonify(
            message=app.config["APP_MESSAGE"],
            name="Rishav",
            roll_no="2301730245",
            version=app.config["APP_VERSION"],
        )

    @app.get("/health")
    def health():
        return jsonify(status="UP", version=app.config["APP_VERSION"])

    @app.get("/visits")
    def visits():
        counter = app.extensions["counter"]
        if counter is None:
            return jsonify(error="Redis is not configured"), 503
        try:
            count = counter.incr("lab2:visits")
        except RedisError:
            return jsonify(error="Redis is unavailable"), 503
        return jsonify(visits=count)

    return app


app = create_app()
