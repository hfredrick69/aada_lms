"""Test users API endpoints"""
from uuid import uuid4


def test_list_users(client, admin_token):
    """Test GET /users"""
    response = client.get("/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_user(client, admin_token):
    """Test POST /users"""
    data = {
        "email": "newuser@aada.edu",
        "password": "securepass123",
        "first_name": "New",
        "last_name": "User"
    }
    response = client.post("/users", json=data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    assert response.json()["email"] == "newuser@aada.edu"


def test_create_duplicate_user(client, admin_token, test_user):
    """Test creating user with duplicate email fails"""
    data = {
        "email": test_user.email,
        "password": "password",
        "first_name": "Dupe",
        "last_name": "User"
    }
    response = client.post("/users", json=data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 400


def test_get_user(client, admin_token, test_user):
    """Test GET /users/{user_id}"""
    response = client.get(f"/users/{test_user.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["id"] == str(test_user.id)


def test_update_user(client, admin_token, test_user):
    """Test PUT /users/{user_id}"""
    data = {"first_name": "Updated", "status": "inactive"}
    response = client.put(f"/users/{test_user.id}", json=data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json()["first_name"] == "Updated"


def test_delete_user(client, admin_token, db):
    """Test DELETE /users/{user_id}"""
    from app.db.models.user import User
    from app.core.security import hash_password

    # Create temp user to delete
    temp_user = User(
        id=uuid4(),
        email="deleteme@aada.edu",
        password_hash=hash_password("password"),
        first_name="Delete",
        last_name="Me"
    )
    db.add(temp_user)
    db.commit()

    response = client.delete(f"/users/{temp_user.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 204
