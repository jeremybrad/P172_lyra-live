"""
Base device profile abstract class for all MIDI devices.

Defines the interface that all device profiles must implement,
along with common data structures for device capabilities and MIDI events.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
import re


@dataclass
class DeviceCapabilities:
    """What can this device do?"""
    has_lights: bool = False
    has_aftertouch: bool = False
    is_mpe: bool = False
    note_range: tuple[int, int] = (21, 108)  # A0 to C8


@dataclass
class MIDIEvent:
    """Incoming MIDI event"""
    type: str  # "note_on", "note_off", "cc"
    pitch: Optional[int] = None
    velocity: Optional[int] = None
    timestamp_ms: int = 0


class DeviceProfile(ABC):
    """Abstract base class for all MIDI device profiles"""

    name_pattern: str  # Regex to match device name
    capabilities: DeviceCapabilities

    @abstractmethod
    def send_note(self, pitch: int, velocity: int, duration_ms: int):
        """Send MIDI note to device"""
        pass

    @abstractmethod
    def detect_input(self, timeout_ms: int = 5000) -> Optional[List[MIDIEvent]]:
        """Listen for MIDI input from device"""
        pass

    def matches(self, device_name: str) -> bool:
        """Check if this profile matches the device name"""
        return bool(re.match(self.name_pattern, device_name, re.IGNORECASE))
