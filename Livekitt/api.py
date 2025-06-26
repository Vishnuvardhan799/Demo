# Import logging module for debug/info logs
import logging

# Import database functions for reservation management
from data_base import create_reservation, find_reservation_by_phone, delete_reservation

# Set up a logger for this module
logger = logging.getLogger("restaurant-api")

# API class that abstracts reservation operations
class RestaurantAPI:
    def __init__(self):
        # Constructor currently doesn't need to initialize anything
        pass

    # Asynchronously create a reservation and log the operation
    async def create_reservation(self, name: str, phone: str, date: str, time: str, guests: int):
        logger.info(f"Creating reservation for {name} on {date} at {time} for {guests} guests")
        create_reservation(name, phone, date, time, guests)  # Call the database layer to store reservation
        return f"Perfect! Reservation made for {name} on {date} at {time} for {guests} guests."

    # Asynchronously check for an existing reservation by phone number
    async def check_reservation(self, phone: str):
        logger.info(f"Checking reservation for phone number {phone}")
        result = find_reservation_by_phone(phone)  # Query the database
        if result:
            # Return reservation details if found
            return (
                f"Reservation found: {result['name']} on {result['date']} at {result['time']} "
                f"for {result['guests']} guests."
            )
        else:
            # Inform user if no reservation found
            return "No reservation found for that phone number."

    # Asynchronously cancel a reservation by phone number
    async def cancel_reservation(self, phone: str):
        logger.info(f"Canceling reservation for phone number {phone}")
        success = delete_reservation(phone)  # Attempt to delete the reservation
        return "Reservation cancelled." if success else "No reservation found to cancel."
