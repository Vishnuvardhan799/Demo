import { useState, useCallback, useEffect } from "react";
import {
  LiveKitRoom,
  RoomAudioRenderer,
  useTracks,
  useParticipants,
  ParticipantTile,
} from "@livekit/components-react";
import "@livekit/components-styles";
import SimpleVoiceAssistant from "./SimpleVoiceAssistant";
import { Track } from "livekit-client";

const LiveKitModal = ({ setShowSupport, callType }) => {
  const [isSubmittingName, setIsSubmittingName] = useState(true);
  const [name, setName] = useState("");
  const [token, setToken] = useState(null);

  const getToken = useCallback(
    async (userName) => {
      try {
        const response = await fetch(
          `/api/getToken?name=${encodeURIComponent(
            userName
          )}&type=${encodeURIComponent(callType)}`
        );
        const token = await response.text();
        setToken(token);
        setIsSubmittingName(false);
      } catch (error) {
        console.error(error);
      }
    },
    [callType]
  );

  const handleNameSubmit = (e) => {
    e.preventDefault();
    if (name.trim()) {
      getToken(name);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="support-room">
          {isSubmittingName ? (
            <form onSubmit={handleNameSubmit} className="name-form">
              <h2>Enter your name to join {callType}</h2>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                required
              />
              <button type="submit">Connect</button>
              <button
                type="button"
                className="cancel-button"
                onClick={() => setShowSupport(false)}
              >
                Cancel
              </button>
            </form>
          ) : token ? (
            <LiveKitRoom
              serverUrl={import.meta.env.VITE_LIVEKIT_URL}
              token={token}
              connect={true}
              video={false} // User does not send video
              audio={true}
              onDisconnected={() => {
                setShowSupport(false);
                setIsSubmittingName(true);
              }}
            >
              {callType === "Voice + Avatar" ? (
                <AvatarUIAgent />
              ) : (
                <>
                  <RoomAudioRenderer />
                  <SimpleVoiceAssistant />
                </>
              )}
            </LiveKitRoom>
          ) : null}
        </div>
      </div>
    </div>
  );
};

// --- UI for the Voice + Avatar Experience ---
function AvatarUIAgent() {
  const participants = useParticipants();
  const cameraTracks = useTracks([Track.Source.Camera]);

  useEffect(() => {
    console.log(' All participants:', participants.map(p => ({
      identity: p.identity,
      name: p.name,
      trackCount: p.tracks.size
    })));

    console.log(' All camera tracks:', cameraTracks.map(t => ({
      participantIdentity: t.participant.identity,
      trackSid: t.track?.sid
    })));

    const agent = participants.find(p => p.identity === 'tavus-avatar-agent');
    console.log(' Found tavus-avatar-agent:', agent);

    const agentTrack = cameraTracks.find(t => 
      t.participant.identity === 'tavus-avatar-agent'
    );
    console.log(' Found agent video track:', agentTrack);
  }, [participants, cameraTracks]);

  // Find agent's video track
  const agentTrackRef = cameraTracks.find(
    (trackRef) => trackRef.participant.identity === "tavus-avatar-agent"
  );

  return (
    <div className="avatar-view">
      <div className="agent-video-container">
        {agentTrackRef ? (
          <ParticipantTile trackRef={agentTrackRef} />
        ) : (
          <div className="agent-placeholder">
            <p>Waiting for agent to connect...</p>
            <p>Debug: {participants.length} participants found</p>
          </div>
        )}
      </div>
      <div className="voice-assistant-container">
        <SimpleVoiceAssistant />
      </div>
    </div>
  );
}

export default LiveKitModal;
