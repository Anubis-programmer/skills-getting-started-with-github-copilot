"""
Tests for Mergington High School extracurricular activities API
Using AAA (Arrange-Act-Assert) pattern
"""

from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Test suite for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self):
        # Arrange
        expected_keys = {"Chess Club", "Programming Class", "Gym Class", 
                        "Basketball Team", "Tennis Club", "Drama Club", 
                        "Art Studio", "Debate Team", "Science Club"}
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert set(activities.keys()) == expected_keys
    
    def test_get_activities_returns_correct_structure(self):
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in activities.items():
            assert set(activity_data.keys()) == required_fields
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self):
        # Arrange
        test_email = "test.student@mergington.edu"
        activity_name = "Chess Club"
        initial_participant_count = len(client.get("/activities").json()[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        updated_activities = client.get("/activities").json()
        assert test_email in updated_activities[activity_name]["participants"]
        assert len(updated_activities[activity_name]["participants"]) == initial_participant_count + 1
    
    def test_signup_duplicate_participant_error(self):
        # Arrange
        test_email = "duplicate.test@mergington.edu"
        activity_name = "Programming Class"
        
        # Sign up once (should succeed)
        client.post(f"/activities/{activity_name}/signup", params={"email": test_email})
        
        # Act - Try to sign up again
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_invalid_activity_error(self):
        # Arrange
        test_email = "test@mergington.edu"
        invalid_activity = "Nonexistent Club"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_activity_full_error(self):
        # Arrange
        activity_name = "Debate Team"  # Has max_participants: 10
        activities = client.get("/activities").json()
        
        # Fill up the activity
        test_emails = [f"student{i}@mergington.edu" for i in range(10)]
        for email in test_emails:
            client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        # Act - Try to sign up when full
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "extra.student@mergington.edu"}
        )
        
        # Assert
        assert response.status_code == 400
        assert "full" in response.json()["detail"]


class TestRemoveParticipant:
    """Test suite for DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_remove_participant_success(self):
        # Arrange
        test_email = "remove.test@mergington.edu"
        activity_name = "Tennis Club"
        
        # Sign up the participant
        client.post(f"/activities/{activity_name}/signup", params={"email": test_email})
        activities = client.get("/activities").json()
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{test_email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        
        # Verify participant was removed
        updated_activities = client.get("/activities").json()
        assert test_email not in updated_activities[activity_name]["participants"]
        assert len(updated_activities[activity_name]["participants"]) == initial_count - 1
    
    def test_remove_participant_not_found_error(self):
        # Arrange
        nonexistent_email = "notinactivity@mergington.edu"
        activity_name = "Art Studio"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{nonexistent_email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
    
    def test_remove_participant_activity_not_found_error(self):
        # Arrange
        test_email = "test@mergington.edu"
        invalid_activity = "Fake Club"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/participants/{test_email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
