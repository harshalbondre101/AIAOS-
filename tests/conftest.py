import os

import pytest

from app.main import create_app


@pytest.fixture(scope="session")
def app():
    app, _ = create_app()
    app.config.update({
        "TESTING": True
    })

    yield app


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture(scope="session")
def runner(app):
    return app.test_cli_runner()
