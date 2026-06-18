from datetime import datetime, timedelta

from tests.test_reservations import create_user


def test_reservation_pagination(client):
    user_id = create_user(client)

    for i in range(5):
        equipment = client.post(
            "/equipments",
            json={
                "name": f"Projetor {i}",
                "category": "video",
                "serial_number": f"PRJ00{i}",
            },
        ).json()

        start = datetime.utcnow() + timedelta(days=i + 1)
        end = start + timedelta(hours=1)

        client.post(
            "/reservations",
            json={
                "user_id": user_id,
                "equipment_id": equipment["id"],
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "purpose": f"Reserva {i}",
            },
        )

    response = client.get(
        "/reservations?limit=2&offset=0"
    )

    assert response.status_code == 200
    assert len(response.json()["items"]) == 2