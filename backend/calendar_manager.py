import os
import requests

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
        url = "https://api.cal.com/v2/schedules"

        print("=" * 50)
        print("CAL_API_KEY EXISTS:", bool(CAL_API_KEY))
        print("EVENT_TYPE_ID:", CAL_EVENT_TYPE_ID)
        print("URL:", url)
        print("HEADERS:", HEADERS)
        print("=" * 50)

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        print("CAL STATUS:", response.status_code)
        print("CAL RESPONSE:", response.text)

        if response.status_code != 200:
            return []

        data = response.json()

        slots = []

        schedules = data.get("data", [])

        print("TOTAL SCHEDULES:", len(schedules))

        for schedule in schedules:

            availability = schedule.get("availability", [])

            print("AVAILABILITY RAW:", availability)

            for day in availability:

                if not isinstance(day, list):
                    continue

                for slot in day:

                    if not isinstance(slot, dict):
                        continue

                    start = slot.get("start")

                    if start:
                        slots.append(start)

        print("PARSED SLOTS:", slots)

        return slots[:5]

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

        print("BOOK PAYLOAD:", payload)

        response = requests.post(
            "https://api.cal.com/v2/bookings",
            headers=HEADERS,
            json=payload,
            timeout=30
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