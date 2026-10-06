import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "activities",
        {
            "Test Activity": {
                "description": "An activity for API tests",
                "schedule": "Mondays at 3:00 PM",
                "max_participants": 5,
                "participants": ["existing@example.com"],
            }
        },
    )
    return TestClient(app_module.app)


def test_get_activities_returns_activity_details(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == {
        "Test Activity": {
            "description": "An activity for API tests",
            "schedule": "Mondays at 3:00 PM",
            "max_participants": 5,
            "participants": ["existing@example.com"],
        }
    }


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Test%20Activity/signup",
        params={"email": "new@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up new@example.com for Test Activity"
    }
    assert app_module.activities["Test Activity"]["participants"] == [
        "existing@example.com",
        "new@example.com",
    ]


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        "/activities/Test%20Activity/signup",
        params={"email": "existing@example.com"},
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Student is already signed up"}


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown%20Activity/signup",
        params={"email": "new@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client):
    response = client.delete(
        "/activities/Test%20Activity/signup",
        params={"email": "existing@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered existing@example.com from Test Activity"
    }
    assert app_module.activities["Test Activity"]["participants"] == []


def test_unregister_rejects_participant_not_signed_up(client):
    response = client.delete(
        "/activities/Test%20Activity/signup",
        params={"email": "unknown@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up"}


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown%20Activity/signup",
        params={"email": "existing@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}