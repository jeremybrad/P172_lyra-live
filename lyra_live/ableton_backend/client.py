"""
Ableton MCP HTTP Client.

High-level wrapper around P050 Ableton MCP Server for ear training exercises.
Provides methods to play exercises via Ableton Live and capture MIDI input.

Note: This is a stub for MVP. Actual P050 API endpoints need to be verified
and may differ from these implementations.
"""

import requests
from typing import Dict, Any, List
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
