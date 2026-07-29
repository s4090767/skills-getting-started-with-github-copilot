import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


ORIGINAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture
def client():
    app_module.activities = copy.deepcopy(ORIGINAL_ACTIVITIES)
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities_response.json()[activity_name]["participants"]


def test_duplicate_signup_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_unregister_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Act
    unregister_response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    activities_response = client.get("/activities")

    # Assert
    assert unregister_response.status_code == 200
    assert "Unregistered" in unregister_response.json()["message"]
    assert email not in activities_response.json()[activity_name]["participants"]
