"""
Ableton MCP HTTP Client.

High-level wrapper around P050 Ableton MCP Server for ear training exercises.
Provides methods to play exercises via Ableton Live and capture MIDI input.

Note: This is a stub for MVP. Actual P050 API endpoints need to be verified
and may differ from these implementations.
"""

import requests
from typing import Dict, Any, List, Optional
from pathlib import Path
from lyra_live.ear_training.base import Exercise, Note


class AbletonMCPClient:
    """HTTP client for P050 Ableton MCP Server"""

    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        Initialize Ableton MCP client.

        Args:
            base_url: Base URL of P050 MCP server (default: http://localhost:8080)
        """
        self.base_url = base_url
        self.session_id = None

    def health_check(self) -> bool:
        """
        Check if P050 server is reachable.

        Returns:
            True if server is healthy, False otherwise
        """
        try:
            # Try a simple GET request to the base URL or a known health endpoint
            # Note: Actual P050 health endpoint may differ
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            # Also try just connecting to the base URL
            try:
                response = requests.get(self.base_url, timeout=2)
                return response.status_code in [200, 404]  # 404 is ok, means server is up
            except requests.exceptions.RequestException:
                return False

    def create_session(self) -> str:
        """
        Create new Ableton Live session for ear training.

        TODO: Verify actual P050 API endpoint for session creation.
        This is a stub implementation.

        Returns:
            Session ID string
        """
        # TODO Phase 1.5: Implement actual P050 session creation
        # For now, return a placeholder session ID
        self.session_id = "lyra_session_001"
        return self.session_id

    def play_exercise(self, exercise: Exercise):
        """
        Play exercise notes via Ableton Live.

        TODO: Convert exercise to MIDI clip data and send to P050.
        This is a stub implementation.

        Args:
            exercise: Exercise to play
        """
        # TODO Phase 1.5: Implement actual MIDI clip creation and playback via P050
        # For now, this is a placeholder that would:
        # 1. Convert exercise.notes to MIDI clip format
        # 2. Create clip in Ableton via P050 API
        # 3. Trigger playback
        print(f"[Ableton Backend] Would play exercise: {exercise.id}")
        print(f"  Notes: {[f'{n.pitch}' for n in exercise.notes]}")
        pass

    def capture_input(self, timeout_s: int = 10) -> List[Note]:
        """
        Capture MIDI input from device via Ableton.

        TODO: Implement MIDI recording via P050.
        This is a stub implementation.

        Args:
            timeout_s: How long to wait for input (seconds)

        Returns:
            List of captured Note objects
        """
        # TODO Phase 1.5: Implement actual MIDI recording via P050
        # For now, return empty list (device profiles handle input directly)
        return []

    def cleanup_session(self):
        """
        Clean up Ableton session after practice.

        TODO: Implement cleanup via P050 API.
        """
        # TODO Phase 1.5: Remove created tracks/clips via P050
        pass

    # ===== PHASE 4: STANDARDS & IMPROVISATION SUPPORT =====

    def create_standard_session(
        self,
        midi_path: Path,
        tempo: int,
        time_signature: tuple,
        chorus_count: int
    ) -> str:
        """
        Create an Ableton session for practicing a jazz standard.

        Sets up backing track, tempo, time signature, and loop length.

        Args:
            midi_path: Path to standard MIDI file
            tempo: Tempo in BPM
            time_signature: Time signature tuple (e.g., (4, 4))
            chorus_count: Number of choruses to loop

        Returns:
            Session ID

        TODO: Implement via P050 API
        """
        print(f"[Ableton Backend] Creating standard session:")
        print(f"  MIDI: {midi_path.name}")
        print(f"  Tempo: {tempo} BPM")
        print(f"  Time signature: {time_signature[0]}/{time_signature[1]}")
        print(f"  Choruses: {chorus_count}")

        # TODO Phase 4: Implementation steps:
        # 1. Load MIDI file into Ableton
        # 2. Set global tempo
        # 3. Set time signature
        # 4. Calculate loop length based on chorus_count
        # 5. Set loop markers
        # 6. Return session ID

        self.session_id = f"standard_session_{midi_path.stem}"
        return self.session_id

    def arm_solo_track(self, track_name: str = "Solo", input_device: Optional[str] = None) -> bool:
        """
        Arm a MIDI track for recording improvisation.

        Args:
            track_name: Name of the track to arm
            input_device: MIDI input device name (optional)

        Returns:
            True if successful

        TODO: Implement via P050 API
        """
        print(f"[Ableton Backend] Arming solo track: {track_name}")
        if input_device:
            print(f"  Input device: {input_device}")

        # TODO Phase 4: Implementation steps:
        # 1. Find or create MIDI track named track_name
        # 2. Set MIDI input routing to input_device (if specified)
        # 3. Arm the track for recording
        # 4. Set monitoring to "In"

        return True

    def start_playback_and_capture(self, duration_bars: int) -> Dict[str, Any]:
        """
        Start playback and begin MIDI capture.

        Args:
            duration_bars: How many bars to record

        Returns:
            Dict with capture session info

        TODO: Implement via P050 API
        """
        print(f"[Ableton Backend] Starting playback and capture for {duration_bars} bars")

        # TODO Phase 4: Implementation steps:
        # 1. Start transport (play)
        # 2. Begin recording on armed track
        # 3. Return capture session ID

        return {
            'capture_id': 'capture_001',
            'start_time': 0,
            'duration_bars': duration_bars
        }

    def stop_and_retrieve_solo(self) -> List[Dict[str, Any]]:
        """
        Stop playback/recording and retrieve captured MIDI notes.

        Returns:
            List of MIDI note dictionaries with keys:
                - pitch (int)
                - velocity (int)
                - time_ms (int)
                - duration_ms (int)

        TODO: Implement via P050 API
        """
        print(f"[Ableton Backend] Stopping playback and retrieving solo MIDI")

        # TODO Phase 4: Implementation steps:
        # 1. Stop transport
        # 2. Stop recording
        # 3. Extract MIDI notes from recorded clip
        # 4. Convert to list of note dicts with timing info
        # 5. Return note data

        # For now, return empty list (actual capture happens via device profiles)
        return []

    def play_standard(self, midi_path: Path, loop: bool = True) -> bool:
        """
        Just play a standard's backing track (no capture).

        Args:
            midi_path: Path to MIDI file
            loop: Whether to loop the track

        Returns:
            True if playback started successfully

        TODO: Implement via P050 API
        """
        print(f"[Ableton Backend] Playing standard: {midi_path.name}")
        print(f"  Loop: {loop}")

        # TODO Phase 4: Implementation steps:
        # 1. Load MIDI file
        # 2. Set loop on/off
        # 3. Start playback
        # 4. Return success status

        return True
