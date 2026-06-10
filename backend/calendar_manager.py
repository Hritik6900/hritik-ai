import os
import requests
from datetime import datetime, timedelta, timezone

CAL_API_KEY = os.getenv("CAL_API_KEY")
CAL_USERNAME = os.getenv("CAL_USERNAME")
CAL_EVENT_TYPE_ID = os.getenv("CAL_EVENT_TYPE_ID")

HEADERS = {
    "Authorization": f"Bearer {CAL_API_KEY}",
    "Content-Type": "application/json",
    "cal-api-version": "2024-09-04"
}


def get_availability():
    try:
        start_time = datetime.now(timezone.utc)
        end_time = start_time + timedelta(days=7)

        response = requests.get(
            "https://api.cal.com/v2/slots/available",
            headers=HEADERS,
            params={
                "eventTypeId": int(CAL_EVENT_TYPE_ID),
                "startTime": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "endTime": end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        )

        print("CAL STATUS:", response.status_code)
        print("CAL RESPONSE:", response.text)

        if response.status_code != 200:
            return []

        data = response.json()
        slots = []

        if data.get("status") == "success":
            slot_data = data.get("data", {})

            if isinstance(slot_data, dict):
                for _, date_slots in slot_data.items():
                    if isinstance(date_slots, list):
                        for slot in date_slots:
                            if isinstance(slot, dict):
                                start = slot.get("start")
                                if start:
                                    slots.append(start)
                            elif isinstance(slot, str):
                                slots.append(slot)

        print("PARSED SLOTS:", slots)
        return slots[:3]

    except Exception as e:
        print("Availability Error:", str(e))
        return []


def book_slot(name, email, slot, purpose="Interview"):
    try:
        payload = {
            "eventTypeId": int(CAL_EVENT_TYPE_ID),
            "start": slot,
            "responses": {
                "name": name,
                "email": email
            },
            "metadata": {
                "purpose": purpose
            },
            "timeZone": "Asia/Kolkata",
            "language": "en"
        }

        response = requests.post(
            "https://api.cal.com/v2/bookings",
            headers=HEADERS,
            json=payload
        )

        print("BOOK STATUS:", response.status_code)
        print("BOOK RESPONSE:", response.text)

        data = response.json()

        if response.status_code in [200, 201]:
            booking = data.get("data", {})
            return {
                "success": True,
                "booking_id": str(booking.get("id")),
                "message": "Interview booked successfully."
            }

        return {
            "success": False,
            "error": str(data)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }