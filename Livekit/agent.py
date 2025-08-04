# Import future annotations for forward type references
from __future__ import annotations

# Load environment variables from .env file
from dotenv import load_dotenv

# Import necessary modules from LiveKit for building voice agents
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, RoomOutputOptions, WorkerOptions, cli, function_tool, RunContext

# Import additional plugins (Google LLM + noise cancellation)
from livekit.plugins import cartesia, deepgram, google, noise_cancellation, tavus

# Import prompt instructions and templates
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION, LOOKUP_RESERVATION_MESSAGE

# Import custom modules for database and knowledge base access
from db_driver import DatabaseDriver
from kb import get_kb_answer

# Import required standard libraries
import enum, os, logging, re, json
import dateparser

# Load environment variables
load_dotenv()

# Setup logger for user data
logger = logging.getLogger("user-data")
logger.setLevel(logging.ERROR)
logging.getLogger("websockets").setLevel(logging.ERROR)

# Instantiate database driver
DB = DatabaseDriver()

# Enum class to represent fields of a reservation
class ReservationDetails(enum.Enum):
    NAME = "name"
    PHONE = "phone"
    DATE = "date"
    TIME = "time"
    GUESTS = "guests"

# Custom Agent for handling restaurant reservations
class RestaurantAgent(Agent):
    def __init__(self) -> None:
        # Initialize the base Agent with general instruction
        super().__init__(instructions=AGENT_INSTRUCTION)
        # Internal dictionary to store reservation data
        self._reservation: dict[ReservationDetails, str] = {
            ReservationDetails.NAME: "",
            ReservationDetails.PHONE: "",
            ReservationDetails.DATE: "",
            ReservationDetails.TIME: "",
            ReservationDetails.GUESTS: ""
        }

    # Check if a reservation exists (based on phone number)
    def has_reservation(self):
        return self._reservation[ReservationDetails.PHONE] != ""

    # Convert reservation dictionary into a readable string
    def get_reservation_str(self):
        def format_phone_number(phone: str) -> str:
            # Format phone number as XXX-XXX-XXXX for clarity
            if len(phone) == 10:
                return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"
            return phone # Return original if not 10 digits

        return "\n".join(f"{k.value}: {format_phone_number(v) if k == ReservationDetails.PHONE else v}" for k, v in self._reservation.items())

    # Tool to look up a reservation by phone number
    @function_tool()
    async def lookup_reservation(self, context: RunContext, phone: str) -> str:
        result = DB.get_reservation_by_phone(phone)
        if not result:
            return "Reservation not found"
        # Populate internal reservation state
        self._reservation = {
            ReservationDetails.NAME: result["name"],
            ReservationDetails.PHONE: result["phone"],
            ReservationDetails.DATE: result["date"],
            ReservationDetails.TIME: result["time"],
            ReservationDetails.GUESTS: str(result["guests"]),
        }
        return f"Found reservation:\n{self.get_reservation_str()}"

    # Tool to check for table availability
    @function_tool()
    async def check_availability(self, context: RunContext, date: str, time: str) -> str:
        # Validate and parse date and time from user input
        parsed_date = dateparser.parse(date)
        if not parsed_date:
            return "I'm sorry, I could not understand the date you provided. Please try again."
        
        requested_time_dt = dateparser.parse(time)
        if not requested_time_dt:
            return "I'm sorry, I could not understand the time you provided. Please try again."

        day_of_week = parsed_date.strftime('%A')

        # Get restaurant hours from the knowledge base
        timings_str = get_kb_answer(f"What are the restaurant's hours on {day_of_week}s?")
        
        # Define the mapping from specific days to the day ranges in the KB
        day_map = {
            "Monday": "Monday to Thursday",
            "Tuesday": "Monday to Thursday",
            "Wednesday": "Monday to Thursday",
            "Thursday": "Monday to Thursday",
            "Friday": "Friday – Saturday",
            "Saturday": "Friday – Saturday",
            "Sunday": "Sunday",
        }
        day_key = day_map.get(day_of_week)

        day_hours_str = None
        if day_key:
            for line in timings_str.split('\n'):
                if day_key in line:
                    day_hours_str = line
                    break
        
        if day_hours_str:
            # Extract opening and closing times using regex
            time_matches = re.findall(r'(\d{1,2}:\d{2}\s*[AP]M)', day_hours_str)
            if len(time_matches) == 2:
                open_time_str, close_time_str = time_matches
                open_time_dt = dateparser.parse(open_time_str)
                close_time_dt = dateparser.parse(close_time_str)

                # Check if the requested time is within the opening hours
                if not (open_time_dt <= requested_time_dt <= close_time_dt):
                    return f"I'm sorry, the restaurant is not open at {time} on {day_of_week}. The hours are from {open_time_str} to {close_time_str}."
                else:
                    return f"The restaurant is open at {time} on {day_of_week}, {date}. You can proceed with the booking."
            else:
                return "I can proceed with the booking, but I could not verify the opening hours."
        else:
            return f"I can proceed with the booking for {day_of_week}, {date}, but I could not find specific hours for that day."

    # Tool to create a new reservation and update internal state
    @function_tool()
    async def create_reservation(self, context: RunContext, name: str, phone: str, date: str, time: str, guests: int) -> str:
        
        parsed_date = dateparser.parse(date)
        if parsed_date:
            date = parsed_date.strftime("%Y-%m-%d")

        result = DB.create_reservation(name, phone, date, time, guests)
        self._reservation = {
            ReservationDetails.NAME: result["name"],
            ReservationDetails.PHONE: result["phone"],
            ReservationDetails.DATE: result["date"],
            ReservationDetails.TIME: result["time"],
            ReservationDetails.GUESTS: str(result["guests"])
        }
        return f"Reservation created:\n{self.get_reservation_str()}"

    # Tool to get current reservation details if available
    @function_tool()
    async def get_reservation_details(self, context: RunContext) -> str:
        if not self.has_reservation():
            return "No reservation information available."
        return f"Current reservation details:\n{self.get_reservation_str()}"

    # Tool to answer general restaurant-related questions using KB
    @function_tool()
    async def answer_restaurant_question(self, context: RunContext, question: str) -> str:
        try:
            return get_kb_answer(question)
        except Exception as e:
            logger.error("Error getting KB answer: %s", e)
            return "Sorry, I had trouble finding an answer to that."

from livekit.rtc.participant import PublishTranscriptionError


# Entry point for the agent application
stt = deepgram.STT()
llm = google.LLM()
tts = deepgram.TTS()

async def entrypoint(ctx: agents.JobContext):
    """
    This is the entrypoint for the agent. It is called when a new job is created.
    """
    # Initialize logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Connect to the room
    await ctx.connect()
    logging.info(f"Agent connected to room: {ctx.room.name}")

    # Safely parse room metadata to determine the call type
    call_type = "Voice Only"
    try:
        if ctx.room.metadata:
            metadata = json.loads(ctx.room.metadata)
            call_type = metadata.get("call_type", "Voice Only")
            logging.info(f"Call type determined from metadata: {call_type}")
        else:
            logging.warning("No room metadata found, defaulting to Voice Only.")
    except json.JSONDecodeError:
        logging.error("Failed to parse room metadata, defaulting to Voice Only.")

    # Initialize the agent session
    session = AgentSession(stt=stt, llm=llm, tts=tts)
    agent = RestaurantAgent()

    # Determine how to start the session based on the call type
    if call_type == "Voice + Avatar":
        logging.info("Voice + Avatar call detected, attempting to initialize Tavus.")
        tavus_api_key = os.getenv("TAVUS_API_KEY")
        if tavus_api_key:
            try:
                avatar = tavus.AvatarSession(
                    api_key=tavus_api_key,
                    replica_id="r6ca16dbe104",
                    persona_id="pa5f2854bea3",
                )
                # Start the session with audio disabled since Tavus will handle it
                await session.start(
                    room=ctx.room,
                    agent=agent,
                    room_input_options=RoomInputOptions(
                        noise_cancellation=noise_cancellation.BVC()
                    ),
                    room_output_options=RoomOutputOptions(
                        audio_enabled=False
                    ),
                )
                # Start the avatar, which takes over video and audio publishing
                await avatar.start(session, room=ctx.room)
                logging.info("Tavus AvatarSession started successfully.")
            except Exception as e:
                logging.error(f"Failed to initialize Tavus, falling back to voice-only. Error: {e}")
                # If Tavus fails, restart the session with audio enabled
                await session.start(
                    room=ctx.room,
                    agent=agent,
                    room_input_options=RoomInputOptions(
                        noise_cancellation=noise_cancellation.BVC()
                    ),
                    room_output_options=RoomOutputOptions(
                        audio_enabled=True
                    ),
                )
        else:
            # Fallback for avatar call if Tavus API key is missing
            logging.warning("TAVUS_API_KEY not set. Starting a voice-only session for the avatar call.")
            await session.start(
                room=ctx.room,
                agent=agent,
                room_input_options=RoomInputOptions(
                    noise_cancellation=noise_cancellation.BVC()
                ),
                room_output_options=RoomOutputOptions(
                    audio_enabled=True
                ),
            )
    else:
        # Standard voice call
        logging.info("Voice-only call detected, starting a regular agent session.")
        await session.start(
            room=ctx.room,
            agent=agent,
            room_input_options=RoomInputOptions(
                noise_cancellation=noise_cancellation.BVC()
            ),
            room_output_options=RoomOutputOptions(
                audio_enabled=True
            ),
        )

    # Generate the initial greeting
    await session.generate_reply(instructions=SESSION_INSTRUCTION)

    # Define the user message handler
    @session.on("user_message")
    def on_user(msg):
        import asyncio
        asyncio.create_task(handle_user(msg))

    async def handle_user(msg):
        try:
            if agent.has_reservation():
                await session.generate_reply()
            else:
                await session.generate_reply(instructions=LOOKUP_RESERVATION_MESSAGE(msg.content))
        except (PublishTranscriptionError, ConnectionError) as e:
            logging.warning(f"Connection lost while generating reply: {e}")
            await session.stop()
        except Exception as e:
            logging.error(f"An unexpected error occurred in handle_user: {e}", exc_info=True)
            await session.stop()

if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        agent_name="restaurant-video-agent"  # This must match the dispatch name
    ))