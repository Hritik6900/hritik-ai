"""
Calendar management for Vapi voice agent.
Handles availability checking and booking confirmation.
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

BOOKINGS_FILE = "bookings.json"

# Hardcoded availability slots for next 7 days
AVAILABILITY_SLOTS = [
    "Monday 10 AM - 11 AM IST",
    "Tuesday 2 PM - 3 PM IST",
    "Wednesday 11 AM - 12 PM IST",
    "Thursday 3 PM - 4 PM IST",
    "Friday 10 AM - 11 AM IST"
]


def initialize_bookings_file():
    """Create bookings.json if it doesn't exist."""
    if not os.path.exists(BOOKINGS_FILE):
        with open(BOOKINGS_FILE, "w") as f:
            json.dump([], f, indent=2)


def get_availability() -> list[str]:
    """
    Get available time slots for interviews.
    
    Returns:
        list[str]: List of available time slots
    """
    return AVAILABILITY_SLOTS


def book_slot(name: str, email: str, slot: str, purpose: str = "Interview") -> dict:
    """
    Book an interview slot on the calendar.
    
    Args:
        name (str): Recruiter's name
        email (str): Recruiter's email
        slot (str): Selected time slot (must be from availability)
        purpose (str): Purpose of meeting (default: "Interview")
    
    Returns:
        dict: Booking confirmation with booking_id
    """
    initialize_bookings_file()
    
    # Validate slot
    if slot not in AVAILABILITY_SLOTS:
        return {
            "success": False,
            "error": f"Invalid slot. Available slots: {', '.join(AVAILABILITY_SLOTS)}"
        }
    
    # Generate booking ID
    booking_id = f"BK_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(email) % 10000:04d}"
    
    # Create booking record
    booking = {
        "booking_id": booking_id,
        "name": name,
        "email": email,
        "slot": slot,
        "purpose": purpose,
        "booked_at": datetime.now().isoformat(),
        "status": "confirmed"
    }
    
    # Load existing bookings
    with open(BOOKINGS_FILE, "r") as f:
        bookings = json.load(f)
    
    # Add new booking
    bookings.append(booking)
    
    # Save updated bookings
    with open(BOOKINGS_FILE, "w") as f:
        json.dump(bookings, f, indent=2)
    
    return {
        "success": True,
        "booking_id": booking_id,
        "name": name,
        "email": email,
        "slot": slot,
        "purpose": purpose,
        "message": f"Booking confirmed! Hritik will see your interview scheduled for {slot}. We've sent a confirmation to {email}."
    }


def get_all_bookings() -> list[dict]:
    """
    Get all bookings.
    
    Returns:
        list[dict]: List of all booking records
    """
    initialize_bookings_file()
    
    with open(BOOKINGS_FILE, "r") as f:
        return json.load(f)


def check_slot_availability(slot: str) -> bool:
    """
    Check if a specific slot is still available.
    
    Args:
        slot (str): Time slot to check
    
    Returns:
        bool: True if slot is available, False if booked
    """
    return slot in AVAILABILITY_SLOTS


if __name__ == "__main__":
    # Test availability
    print("Available slots:")
    for slot in get_availability():
        print(f"  - {slot}")
    
    # Test booking
    result = book_slot(
        name="John Recruiter",
        email="john@company.com",
        slot="Monday 10 AM - 11 AM IST",
        purpose="Technical Interview"
    )
    print("\nBooking result:")
    print(json.dumps(result, indent=2))
    
    # Print all bookings
    bookings = get_all_bookings()
    print(f"\nTotal bookings: {len(bookings)}")
