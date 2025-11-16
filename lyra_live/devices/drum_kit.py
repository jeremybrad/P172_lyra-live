"""
Drum kit device profiles for electronic drums.

Provides device profiles for electronic drum kits with MIDI output,
mapping MIDI notes to logical drum parts (kick, snare, toms, cymbals).
"""

from lyra_live.devices.base import DeviceProfile, DeviceCapabilities, MIDIEvent
from typing import List, Optional, Dict
import time


# Standard drum MIDI note mappings (General MIDI percussion)
GENERAL_MIDI_DRUM_MAP = {
    35: "kick_acoustic",
    36: "kick",
    38: "snare",
    40: "snare_rimshot",
    42: "hihat_closed",
    44: "hihat_pedal",
    46: "hihat_open",
    41: "tom_low",
    43: "tom_low_floor",
    45: "tom_mid",
    47: "tom_mid_high",
    48: "tom_high",
    49: "crash_1",
    51: "ride",
    55: "crash_splash",
    57: "crash_2",
}


class DrumKitProfile(DeviceProfile):
    """
    Generic drum kit profile for electronic drums.

    Maps MIDI notes from drum pads to logical drum parts.
    Subclass this for specific drum kits with custom mappings.
    """

    name_pattern = ".*Drum.*|.*Kit.*"
    capabilities = DeviceCapabilities(
        has_lights=False,
        has_aftertouch=False,
        is_mpe=False,
        note_range=(0, 127)
    )

    def __init__(self, device_name: str, note_mapping: Dict[int, str] = None):
        """
        Initialize drum kit profile.

        Args:
            device_name: Name of the MIDI device
            note_mapping: Optional custom mapping of MIDI notes to drum part names
                         Defaults to General MIDI drum map
        """
        self.device_name = device_name
        self.note_mapping = note_mapping or GENERAL_MIDI_DRUM_MAP
        self.output_port = None
        self.input_port = None

        # Reverse mapping for looking up MIDI notes by drum part name
        self.part_to_note = {v: k for k, v in self.note_mapping.items()}

    def get_drum_part(self, midi_note: int) -> Optional[str]:
        """Get drum part name for a MIDI note."""
        return self.note_mapping.get(midi_note)

    def get_midi_note(self, drum_part: str) -> Optional[int]:
        """Get MIDI note for a drum part name."""
        return self.part_to_note.get(drum_part)

    def send_note(self, pitch: int, velocity: int, duration_ms: int):
        """
        Send MIDI note to drum kit (trigger pad).

        Args:
            pitch: MIDI note number (drum pad)
            velocity: Hit velocity (0-127)
            duration_ms: Not used for drums (hits are instantaneous)
        """
        # Drum kits don't typically need output (we're listening to them)
        # But this is here for completeness
        pass

    def detect_input(self, timeout_ms: int = 5000) -> Optional[List[MIDIEvent]]:
        """
        Listen for drum hits from the kit.

        Returns MIDI events with precise timestamps for rhythm evaluation.

        Args:
            timeout_ms: How long to listen for hits

        Returns:
            List of MIDIEvent objects with drum hits, or None if no hits detected
        """
        events = []
        start_time = time.time() * 1000  # Milliseconds

        try:
            import mido
            with mido.open_input(self.device_name) as inport:
                while True:
                    current_time = time.time() * 1000
                    if current_time - start_time > timeout_ms:
                        break

                    # Check for messages (non-blocking)
                    for msg in inport.iter_pending():
                        if msg.type == 'note_on' and msg.velocity > 0:
                            # Record drum hit with precise timestamp
                            drum_part = self.get_drum_part(msg.note)
                            events.append(MIDIEvent(
                                type='note_on',
                                pitch=msg.note,
                                velocity=msg.velocity,
                                timestamp_ms=int(current_time)
                            ))

                    # Small sleep to avoid busy waiting
                    time.sleep(0.001)  # 1ms poll rate for precision

        except (IOError, OSError) as e:
            print(f"Warning: Could not open drum kit input: {e}")
            return None

        return events if events else None

    def close(self):
        """Close MIDI ports."""
        if self.output_port:
            self.output_port.close()
        if self.input_port:
            self.input_port.close()


class DonnerDrumKitProfile(DrumKitProfile):
    """
    Profile for Donner electronic drum kits.

    Provides specific mapping for a typical 5-piece Donner kit:
    - Kick drum
    - Snare
    - 3 toms
    - Hi-hat (with pedal)
    - Crash cymbal
    - Ride cymbal
    """

    name_pattern = ".*Donner.*"

    def __init__(self, device_name: str):
        """Initialize Donner drum kit with standard mapping."""

        # Donner kits typically use General MIDI drum mapping
        # But we can customize if needed
        donner_mapping = {
            36: "kick",           # Bass drum
            38: "snare",          # Snare
            42: "hihat_closed",   # Closed hi-hat
            46: "hihat_open",     # Open hi-hat
            48: "tom_high",       # High tom
            45: "tom_mid",        # Mid tom
            43: "tom_floor",      # Floor tom
            49: "crash",          # Crash cymbal
            51: "ride",           # Ride cymbal
        }

        super().__init__(device_name, note_mapping=donner_mapping)

        # Update capabilities for Donner
        self.capabilities = DeviceCapabilities(
            has_lights=False,
            has_aftertouch=False,
            is_mpe=False,
            note_range=(36, 51)  # Range of Donner pads
        )
