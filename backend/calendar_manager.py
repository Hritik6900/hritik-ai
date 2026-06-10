import os
import requests
from datetime import datetime

CAL_API_KEY = os.getenv("CAL_API_KEY")
CAL_USERNAME = os.getenv("CAL_USERNAME")
CAL_EVENT_TYPE_ID = os.getenv("CAL_EVENT_TYPE_ID")

HEADERS = {
    "Authorization": f"Bearer {CAL_API_KEY}",
    "Content-Type": "application/json"
}


def get_availability():
    try:
        start = datetime.utcnow().isoformat() + "Z"

        url = (
            f"https://api.cal.com/v2/slots"
            f"?eventTypeId={CAL_EVENT_TYPE_ID}"
            f"&start={start}"
        )

        response = requests.get(url, headers=HEADERS)

        data = response.json()

        slots = []

        if "data" in data:
            for day in data["data"]:
                for slot in data["data"][day]:
                    slots.append(slot["start"])

        return slots[:3]

    except Exception as e:
        print("Availability Error:", e)
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