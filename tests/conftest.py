import pytest
from fastapi.testclient import TestClient

from old_main import app, get_current_user


@pytest.fixture
def client():
    """
    Stellt einen TestClient zur Verfügung und setzt standardmäßig
    den aktuellen Benutzer auf user_id = 1.
    """
    # Dependency Override für Auth
    app.dependency_overrides[get_current_user] = lambda: 1
    with TestClient(app) as c:
        yield c
    # Nach dem Test wieder aufräumen
    app.dependency_overrides.clear()
