import os
import json
import asyncio
import uuid
from flask import Flask, request
from dotenv import load_dotenv
from flask_cors import CORS
from livekit import api

# Load environment variables from a .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# This async function encapsulates all the necessary async LiveKit API calls
async def create_room_and_generate_token(room_name, participant_identity, participant_name, call_type):
    """
    Creates a LiveKit room if it doesn't exist and generates an access token for a participant.
    """
    livekit_url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")

    # Initialize the LiveKit API client
    livekit_api = api.LiveKitAPI(livekit_url, api_key, api_secret)

    # If no room name is provided by the client, generate a unique one
    if not room_name:
        room_name = "room-" + str(uuid.uuid4())[:8]
        print(f"No room name provided, creating a new room: {room_name}")
        try:
            # Create the room with the specified call_type in its metadata AND dispatch your specific agent
            await livekit_api.room.create_room(
                api.CreateRoomRequest(
                    name=room_name,
                    metadata=json.dumps({"call_type": call_type}),
                    # IMPORTANT: Dispatch your specific named agent
                    agents=[
                        api.RoomAgentDispatch(
                            agent_name="restaurant-video-agent",  # Must match your agent.py
                            metadata=json.dumps({"call_type": call_type})
                        )
                    ]
                )
            )
            print(f"Room '{room_name}' created with agent dispatch for call type: {call_type}")
        except Exception as e:
            # This might fail if the room already exists, which is not a critical error in this flow.
            print(f"Warning: Could not create room '{room_name}'. It may already exist. Error: {e}")
            pass

    # Create an access token for the participant
    access_token = api.AccessToken(api_key, api_secret)
    access_token.with_identity(participant_identity)
    access_token.with_name(participant_name)
    access_token.with_grants(
        api.VideoGrants(
            room_join=True,
            room=room_name
        )
    )

    # Close the API client session
    await livekit_api.aclose()

    # Return the generated JWT
    return access_token.to_jwt()

@app.route("/getToken")
def get_token():
    """
    Synchronous Flask route to handle token generation requests.
    """
    # Get parameters from the client's request
    participant_identity = request.args.get("name", "user_" + str(uuid.uuid4())[:4])
    room_name = request.args.get("room", None)
    call_type = request.args.get("type", "Voice Only")

    try:
        # Run the async function from this synchronous route to get the token
        jwt = asyncio.run(
            create_room_and_generate_token(
                room_name, participant_identity, participant_identity, call_type
            )
        )
        return jwt
    except Exception as e:
        print(f"Error generating token: {e}")
        return str(e), 500

if __name__ == "__main__":
    # Run the Flask app
    app.run(host="0.0.0.0", port=5001, debug=True)