from datetime import datetime, timedelta


def create_user(client):
    response = client.post(
        "/users",
        json={
            "name": "Maria",
            "email": "maria@email.com",
        },
    )

    return response.json()["id"]


def create_equipment(client):
    response = client.post(
        "/equipments",
        json={
            "name": "Notebook",
            "category": "TI",
            "serial_number": "NOTE001",
        },
    )

    return response.json()["id"]


def test_valid_status_transition(client):
    user_id = create_user(client)
    equipment_id = create_equipment(client)

    start = datetime.utcnow()
    end = start + timedelta(hours=1)

    reservation = client.post(
        "/reservations",
        json={
            "user_id": user_id,
            "equipment_id": equipment_id,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "purpose": "Teste",
        },
    ).json()

    response = client.patch(
        f"/reservations/{reservation['id']}/status",
        json={"status": "confirmed"},
    )

    assert response.status_code == 200


def test_invalid_transition(client):
    user_id = create_user(client)
    equipment_id = create_equipment(client)

    start = datetime.utcnow()
    end = start + timedelta(hours=1)

    reservation = client.post(
        "/reservations",
        json={
            "user_id": user_id,
            "equipment_id": equipment_id,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "purpose": "Teste",
        },
    ).json()

    response = client.patch(
        f"/reservations/{reservation['id']}/status",
        json={"status": "completed"},
    )

    assert response.status_code == 422
    
def test_update_nonexistent_reservation(client):
        response = client.patch(
        "/reservations/999/status",
        json={"status": "confirmed"},
    )

        assert response.status_code == 404
    
def test_terminal_state_transition(client):
        user_id = create_user(client)
        equipment_id = create_equipment(client)

        start = datetime.utcnow()
        end = start + timedelta(hours=1)

        reservation = client.post(
            "/reservations",
            json={
                "user_id": user_id,
                "equipment_id": equipment_id,
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "purpose": "Teste",
        },
    ).json()

        client.patch(
        f"/reservations/{reservation['id']}/status",
        json={"status": "canceled"},
    )

        response = client.patch(
        f"/reservations/{reservation['id']}/status",
        json={"status": "confirmed"},
    )

        assert response.status_code == 409
        assert response.json()["error"] == "TERMINAL_STATE"