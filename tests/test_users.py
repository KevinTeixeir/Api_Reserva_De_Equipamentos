def test_create_user(client):

    response = client.post(
        "/users",
        json={
            "name": "Paula",
            "email": "paula@email.com",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "paula@email.com"