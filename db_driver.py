# Import standard logging module
import logging

# Import OS module for environment variable access
import os

# Load environment variables from a .env file
from dotenv import load_dotenv

# MongoDB client and error classes
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Typing helper for optional return values
from typing import Optional

# ---------- Load .env file and initialize MongoDB URI ----------

# Load environment variables from the .env file into the environment
load_dotenv()

# Retrieve MongoDB URI from environment variables
MONGO_URI = os.getenv("MONGO_URI")

# ---------- Logger Setup ----------

# Create logger with the name "data_base"
logger = logging.getLogger("data_base")

# Configure basic logging level to INFO
logging.basicConfig(level=logging.ERROR)

# ---------- MongoDB Connection Setup ----------

try:
    # Initialize MongoDB client with the URI
    client = MongoClient(MONGO_URI)

    # Access the 'restaurant' database (was 'auto_service' earlier)
    db = client["restaurant"]

    # Access the 'reservations' collection within the 'restaurant' database
    reservations_collection = db["reservations"]

    # Log successful connection
    logger.info("MongoDB connection initialized successfully")

except PyMongoError as e:
    # Log and raise any connection error
    logger.error(f"Error connecting to MongoDB: {e}")
    raise

# ---------- Reservation Database Driver Class ----------

class DatabaseDriver:
    def __init__(self):
        # Initialize the collection reference to use in other methods
        self.collection = reservations_collection

    # Create a new reservation in the MongoDB collection
    def create_reservation(self, name: str, phone: str, date: str, time: str, guests: int) -> Optional[dict]:
        reservation = {
            "name": name,
            "phone": phone,
            "date": date,
            "time": time,
            "guests": guests
        }
        try:
            # Insert the reservation document into the MongoDB collection
            self.collection.insert_one(reservation)

            # Log the successful creation
            logger.info(f"Reservation created for phone: {phone}")

            # Return the reservation data
            return reservation

        except PyMongoError as e:
            # Log and return None in case of error
            logger.error(f"Error creating reservation: {e}")
            return None

    # Retrieve a reservation document by phone number
    def get_reservation_by_phone(self, phone: str) -> Optional[dict]:
        try:
            # Search for a reservation with the matching phone number
            reservation = self.collection.find_one({"phone": phone})

            # Log the result of the search
            if reservation:
                logger.info(f"Reservation found: {phone}")
            else:
                logger.info(f"Reservation not found: {phone}")

            # Return the reservation if found, else None
            return reservation

        except PyMongoError as e:
            # Log and return None if there's an error during fetch
            logger.error(f"Error fetching reservation: {e}")
            return None