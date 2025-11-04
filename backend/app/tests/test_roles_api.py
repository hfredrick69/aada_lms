"""Test roles API endpoints"""


def test_list_roles(client):
    """Test GET /roles"""
    response = client.get("/roles")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_role(client, admin_token):
    """Test POST /roles"""
    data = {
        "name": "TestRole",
        "description": "Test role description"
    }
    response = client.post("/roles", json=data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 201
    assert response.json()["name"] == "TestRole"


def test_create_duplicate_role(client, admin_token):
    """Test creating duplicate role fails"""
    data = {"name": "Admin", "description": "Duplicate"}
    response = client.post("/roles", json=data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 400


def test_delete_role(client, admin_token, db):
    """Test DELETE /roles/{role_id}"""
    from app.db.models.role import Role
    from uuid import uuid4

    # Create temp role to delete
    temp_role = Role(id=uuid4(), name="DeleteMe", description="Temporary")
    db.add(temp_role)
    db.commit()

    response = client.delete(f"/roles/{temp_role.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 204
