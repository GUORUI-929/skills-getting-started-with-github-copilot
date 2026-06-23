import copy

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
_initial_activities = copy.deepcopy(activities)


def setup_function():
    activities.clear()
    activities.update(copy.deepcopy(_initial_activities))


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_for_activity_success():
    email = "newstudent@mergington.edu"
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_activity_duplicate_returns_400():
    existing_email = "michael@mergington.edu"
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": existing_email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for an activity"


def test_signup_for_activity_unknown_activity_returns_404():
    response = client.post(
        "/activities/Unknown Activity/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_from_activity_success():
    email = "john@mergington.edu"
    response = client.delete(
        "/activities/Gym Class/unregister",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Gym Class"}
    assert email not in activities["Gym Class"]["participants"]


def test_unregister_from_activity_unknown_activity_returns_404():
    response = client.delete(
        "/activities/Unknown Activity/unregister",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_from_activity_missing_participant_returns_404():
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "missing@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in activity"