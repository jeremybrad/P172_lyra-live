"""
Generic MIDI keyboard profile - fallback for any standard MIDI device.

This profile uses mido to communicate with any MIDI device that doesn't
have a specialized profile. It provides basic note input/output without
device-specific features like light guides or MPE.
"""

import mido
import time
from lyra_live.devices.base import DeviceProfile, DeviceCapabilities, MIDIEvent
from typing import List, Optional


class GenericKeyboardProfile(DeviceProfile):
    """Fallback profile for any MIDI keyboard"""

    name_pattern = ".*"  # Matches anything
    capabilities = DeviceCapabilities()

    def __init__(self, device_name: str):
        self.device_name = device_name
        self.output_port = None
        self.input_port = None

    def connect(self):
        """Open MIDI output port"""
        if not self.output_port:
            try:
                self.output_port = mido.open_output(self.device_name)
            except (IOError, OSError) as e:
                print(f"Warning: Could not open output port for {self.device_name}: {e}")

    def send_note(self, pitch: int, velocity: int, duration_ms: int):
        """Send note via mido"""
        if not self.output_port:
            self.connect()

        if self.output_port:
            # Send note on
            msg_on = mido.Message('note_on', note=pitch, velocity=velocity)
            self.output_port.send(msg_on)

            # Wait for duration (in practice, Ableton handles this)
            # This is here for completeness but may not be used in MVP
            if duration_ms > 0:
                time.sleep(duration_ms / 1000.0)
                msg_off = mido.Message('note_off', note=pitch, velocity=0)
                self.output_port.send(msg_off)

    def detect_input(self, timeout_ms: int = 5000) -> Optional[List[MIDIEvent]]:
        """Listen for MIDI input from device"""
        events = []
        start_time = time.time() * 1000  # Convert to milliseconds

        try:
            with mido.open_input(self.device_name) as inport:
                while True:
                    # Check timeout
                    current_time = time.time() * 1000
                    if current_time - start_time > timeout_ms:
                        break

                    # Check for messages (non-blocking)
                    for msg in inport.iter_pending():
                        if msg.type == 'note_on' and msg.velocity > 0:
                            events.append(MIDIEvent(
                                type='note_on',
                                pitch=msg.note,
                                velocity=msg.velocity,
                                timestamp_ms=int(current_time)
                            ))
                        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                            events.append(MIDIEvent(
                                type='note_off',
                                pitch=msg.note,
                                velocity=0,
                                timestamp_ms=int(current_time)
                            ))

                    # If we have note events, wait a bit for any additional notes
                    # (in case user plays multiple notes for an interval/chord)
                    if events:
                        time.sleep(0.5)  # Wait 500ms for additional notes
                        # Check one more time for any additional notes
                        for msg in inport.iter_pending():
                            if msg.type == 'note_on' and msg.velocity > 0:
                                events.append(MIDIEvent(
                                    type='note_on',
                                    pitch=msg.note,
                                    velocity=msg.velocity,
                                    timestamp_ms=int(time.time() * 1000)
                                ))
                        break

                    # Small sleep to avoid busy waiting
                    time.sleep(0.01)

        except (IOError, OSError) as e:
            print(f"Warning: Could not open input port for {self.device_name}: {e}")
            return None

        return events if events else None

    def close(self):
        """Close MIDI ports"""
        if self.output_port:
            self.output_port.close()
        if self.input_port:
            self.input_port.close()
