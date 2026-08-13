from fastapi.testclient import TestClient
from src.main import app
import pytest


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides.clear()

    