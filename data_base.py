# Import the logging module to track actions for debugging or monitoring
import logging

# Import database functions for reservation operations
from data_base import create_reservation, find_reservation_by_phone, delete_reservation

# Create a logger specific to the restaurant API module
logger = logging.getLogger("restaurant-api")

# Define a class that acts as an interface between the assistant and the database
class RestaurantAPI:
    def __init__(self):
        # No initialization needed for now
        pass

    # Create a new reservation in the database
    async def create_reservation(self, name: str, phone: str, date: str, time: str, guests: int):
        # Log the reservation creation request
        logger.info(f"Creating reservation for {name} on {date} at {time} for {guests} guests")
        
        # Call the database function to store the reservation
        create_reservation(name, phone, date, time, guests)
        
        # Return a confirmation message
        return f"Perfect! Reservation made for {name} on {date} at {time} for {guests} guests."

    # Look up a reservation using the guest's phone number
    async def check_reservation(self, phone: str):
        # Log the lookup attempt
        logger.info(f"Checking reservation for phone number {phone}")
        
        # Search for reservation in the database
        result = find_reservation_by_phone(phone)
        
        # Return reservation details if found
        if result:
            return (
                f"Reservation found: {result['name']} on {result['date']} at {result['time']} "
                f"for {result['guests']} guests."
            )
        else:
            # Inform user if no reservation is found
            return "No reservation found for that phone number."

    # Cancel an existing reservation by phone number
    async def cancel_reservation(self, phone: str):
        # Log the cancellation attempt
        logger.info(f"Canceling reservation for phone number {phone}")
        
        # Attempt to delete the reservation
        success = delete_reservation(phone)
        
        # Return appropriate message based on result
        return "Reservation cancelled." if success else "No reservation found to cancel."
