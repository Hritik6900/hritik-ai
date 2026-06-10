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

```
    response = requests.get(
        "https://api.cal.com/v2/slots/available",
        headers=HEADERS,
        params={
            "eventTypeId": CAL_EVENT_TYPE_ID,
            "startTime": start_time.isoformat(),
            "endTime": end_time.isoformat()
        }
    )

    print("CAL STATUS:", response.status_code)
    print("CAL RESPONSE:", response.text)

    data = response.json()
    slots = []

    if data.get("status") == "success":
        slot_data = data.get("data", {})

        for date_key, date_slots in slot_data.items():
            for slot in date_slots:
                if isinstance(slot, dict):
                    slots.append(slot.get("start"))
                else:
                    slots.append(slot)

    return slots[:3]

except Exception as e:
    print("Availability Error:", str(e))
    return []
```

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

```
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
```
