# Load environment variables from a .env file
from dotenv import load_dotenv

# Import necessary modules from LiveKit
from livekit import agents
from livekit.agents import AgentSession, RoomInputOptions
from livekit.plugins import noise_cancellation
from livekit.plugins import google

# Import instruction prompts and custom Restaurant API
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from api import RestaurantAPI

# Load the environment variables
load_dotenv()

# Initialize the restaurant API to handle reservations
restaurant_api = RestaurantAPI()

# Define the custom assistant class, inheriting from LiveKit's Agent
class Assistant(agents.Agent):
    def __init__(self) -> None:
        # Initialize the agent with voice and behavior settings
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
                voice="Aoede",  # Voice used by the assistant
                temperature=0.8,  # Controls randomness of responses
            ),
        )

    # Define how the assistant responds to user input
    async def generate_response(self, session, user_input):
        # Check if the user wants to create a reservation
        if "create reservation" in user_input.lower():
            # Ask for user's name
            await session.generate_reply(instructions="Sure, I can help with that. Could you please provide your name?")
            name = await session.wait_for_response()
            
            # Ask for phone number
            await session.generate_reply(instructions="Thank you. Could you please provide your phone number?")
            phone = await session.wait_for_response()
            
            # Ask for reservation date
            await session.generate_reply(instructions="Thanks. When would you like to make the reservation? (Date)")
            date = await session.wait_for_response()
            
            # Ask for reservation time
            await session.generate_reply(instructions="What time would you like to visit?")
            time = await session.wait_for_response()
            
            # Ask for guest count
            await session.generate_reply(instructions="How many guests will be joining you?")
            guests = await session.wait_for_response()
            
            # Call the Restaurant API to create the reservation
            result = await restaurant_api.create_reservation(
                name=name,
                phone=phone,
                date=date,
                time=time,
                guests=int(guests)  # Convert guest input to integer
            )
            
            # Return the result to the user
            await session.generate_reply(response=result)
        else:
            # Handle unrecognized requests
            await session.generate_reply(response="I'm sorry, I didn't understand your request.")

# Entrypoint function to start the session
async def entrypoint(ctx: agents.JobContext):
    # Create a new session for the agent
    session = AgentSession()
    
    # Start the session with video and noise cancellation enabled
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),  # Use BVC noise cancellation plugin
        ),
    )

    # Connect to the room context
    await ctx.connect()

    # Send the initial session instructions to the user
    await session.generate_reply(
        instructions=SESSION_INSTRUCTION,
    )

# Entry point when the script is run directly
if __name__ == "__main__":
    # Run the app with the entrypoint function
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
