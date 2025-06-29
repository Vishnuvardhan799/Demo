# Import logging for logging debug/info/error messages
import logging

# Import MongoClient to connect to MongoDB
from pymongo import MongoClient

# Import error class to handle MongoDB exceptions
from pymongo.errors import PyMongoError

# Used to load environment variables from a .env file
import os
from dotenv import load_dotenv

# Load environment variables (like MONGO_URI) from the .env file
load_dotenv()

# Load the MongoDB URI string from the environment
MONGO_URI = os.getenv("MONGO_URI")

# Setup a logger for the database module
logger = logging.getLogger("data_base")
logging.basicConfig(level=logging.INFO)

# ---------- MongoDB Connection ----------

try:
    # Create a client to connect to MongoDB Atlas using the URI
    client = MongoClient(MONGO_URI)

    # Select the database (it will be created if it doesn't exist)
    db = client["restaurant_db"]

    # Select the collection (like a table in SQL). This will store reservations.
    reservations = db["reservations"]

    logger.info("Database initialized successfully")

except PyMongoError as e:
    # Handle errors like wrong URI, network issue, auth failure
    logger.error(f"Error connecting to MongoDB: {e}")
    raise  # Stop the program if DB connection fails

# ---------- Function: Create Reservation ----------

def create_reservation(name: str, phone: str, date: str, time: str, guests: int) -> str:
    """
    Inserts a reservation document into the MongoDB 'reservations' collection.
    """
    try:
        # Create a dictionary (document) with all reservation details
        reservation = {
            "name": name,
            "phone": phone,
            "date": date,
            "time": time,
            "guests": guests
        }

        # Insert the reservation document into the collection
        reservations.insert_one(reservation)

        logger.info(f"Reservation created for {name}")

        # Return a user-friendly confirmation message
        return f"Thanks {name}, your reservation for {guests} guests on {date} at {time} has been confirmed."

    except PyMongoError as e:
        # Handle insertion errors
        logger.error(f"Error creating reservation: {e}")
        return "Sorry, something went wrong while creating your reservation."

# ---------- Function: Find Reservation By Phone ----------

def find_reservation_by_phone(phone: str):
    """
    Retrieves a reservation document from the collection using the phone number.
    Returns None if not found or if there's an error.
    """
    try:
        # Search for the first matching document with the given phone number
        return reservations.find_one({"phone": phone})
    except PyMongoError as e:
        # Log and handle any MongoDB error
        logger.error(f"Error finding reservation: {e}")
        return None

# ---------- Function: Delete Reservation ----------

def delete_reservation(phone: str) -> str:
    """
    Deletes a reservation document based on the phone number.
    Returns a confirmation or error message.
    """
    try:
        # Try to delete the first document with the given phone number
        result = reservations.delete_one({"phone": phone})

        # Check if any document was actually deleted
        if result.deleted_count > 0:
            logger.info(f"Reservation deleted for phone: {phone}")
            return "Your reservation has been successfully canceled."
        else:
            # No match found
            return "No reservation found with that phone number."

    except PyMongoError as e:
        # Handle deletion errors
        logger.error(f"Error deleting reservation: {e}")
        return "Sorry, something went wrong while trying to delete your reservation."
