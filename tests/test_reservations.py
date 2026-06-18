from datetime import datetime, timedelta


def create_user(client):
    response = client.post(
        "/users",
        json={
            "name": "Paula",
            "email": "paula@email.com",
        },
    )

    return response.json()["id"]


def create_equipment(client):
    response = client.post(
        "/equipments",
        json={
            "name": "Projetor",
            "category": "video",
            "serial_number": "PRJ001",
        },
    )

    return response.json()["id"]


def test_create_reservation(client):
    user_id = create_user(client)
    equipment_id = create_equipment(client)

    start = datetime.utcnow()
    end = start + timedelta(hours=2)

    response = client.post(
        "/reservations",
        json={
            "user_id": user_id,
            "equipment_id": equipment_id,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "purpose": "Apresentação",
        },
    )

    assert response.status_code == 201


def test_reservation_conflict(client):
    user_id = create_user(client)
    equipment_id = create_equipment(client)

    start = datetime.utcnow()
    end = start + timedelta(hours=2)

    payload = {
        "user_id": user_id,
        "equipment_id": equipment_id,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "purpose": "Evento",
    }

    client.post("/reservations", json=payload)

    response = client.post(
        "/reservations",
        json=payload,
    )

    assert response.status_code == 409
    assert response.json()["error"] == "RESERVATION_CONFLICT"


def test_suspended_user_cannot_reserve(client):
    user = client.post(
        "/users",
        json={
            "name": "Maria",
            "email": "maria@email.com",
        },
    ).json()

    client.patch(
        f"/users/{user['id']}/status",
        json={"status": "suspended"},
    )

    equipment_id = create_equipment(client)

    start = datetime.utcnow()
    end = start + timedelta(hours=2)

    response = client.post(
        "/reservations",
        json={
            "user_id": user["id"],
            "equipment_id": equipment_id,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "purpose": "Evento",
        },
    )

    assert response.status_code == 403


def test_reservation_limit(client):
    user_id = create_user(client)
    equipment_ids = []

    for i in range(4):
        response = client.post(
            "/equipments",
            json={
                "name": f"Equipamento {i}",
                "category": "teste",
                "serial_number": f"SERIAL{i}",
            },
        )

        equipment_ids.append(response.json()["id"])

    for i in range(3):
        start = datetime.utcnow() + timedelta(days=i + 1)
        end = start + timedelta(hours=1)

        client.post(
            "/reservations",
            json={
                "user_id": user_id,
                "equipment_id": equipment_ids[i],
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "purpose": "Teste",
            },
        )

    start = datetime.utcnow() + timedelta(days=10)
    end = start + timedelta(hours=1)

    response = client.post(
        "/reservations",
        json={
            "user_id": user_id,
            "equipment_id": equipment_ids[3],
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "purpose": "Teste",
        },
    )

    assert response.status_code == 409
    
    
def test_unavailable_equipment_cannot_be_reserved(client):
    user_id = create_user(client)
    equipment = client.post(
        "/equipments",
        json={
                "name": "Notebook",
                "category": "TI",
                "serial_number": "NOTE999",
            },
        ).json()

    client.patch(
        f"/equipments/{equipment['id']}/status",
        json={"status": "unavailable"},
    )

    start = datetime.utcnow()
    end = start + timedelta(hours=2)

    response = client.post(
        "/reservations",
        json={
            "user_id": user_id,
            "equipment_id": equipment["id"],
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "purpose": "Teste",
        },
    )

    assert response.status_code == 409
    assert response.json()["error"] == "EQUIPMENT_UNAVAILABLE"
    
    