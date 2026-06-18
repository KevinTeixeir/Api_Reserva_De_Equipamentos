def test_create_equipment(client):

    response = client.post(
        "/equipments",
        json={
            "name": "Notebook Dell",
            "category": "notebook",
            "serial_number": "ABC123",
        },
    )

    assert response.status_code == 201