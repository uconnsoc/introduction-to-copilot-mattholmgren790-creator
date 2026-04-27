import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data():
    response = client.get("/activities")

    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()


def test_signup_for_activity_adds_participant():
    response = client.post(
        "/activities/Chess%20Club/signup?email=test.student@mergington.edu"
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up test.student@mergington.edu for Chess Club"
    }
    assert "test.student@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_bad_request():
    email = "michael@mergington.edu"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_from_activity():
    email = "michael@mergington.edu"
    response = client.delete(
        f"/activities/Chess%20Club/signup?email={email}"
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Removed michael@mergington.edu from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_remove_nonexistent_participant_returns_not_found():
    email = "notfound@mergington.edu"
    response = client.delete(
        f"/activities/Chess%20Club/signup?email={email}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"
