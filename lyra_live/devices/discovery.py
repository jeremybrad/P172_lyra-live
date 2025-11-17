"""
MIDI device discovery and profile matching.

Scans for available MIDI devices and matches them to appropriate device profiles.
For MVP, always returns GenericKeyboardProfile.
"""

import mido
from typing import List
from lyra_live.devices.base import DeviceProfile
from lyra_live.devices.generic_keyboard import GenericKeyboardProfile


def list_midi_devices() -> List[str]:
    """Get all available MIDI input devices"""
    return mido.get_input_names()


def get_device_profile(device_name: str) -> DeviceProfile:
    """
    Match device name to appropriate profile.

    For MVP (Phase 1), always returns GenericKeyboardProfile.
    In Phase 2, this will check device_name against patterns for:
    - NativeS88Profile (for Komplete Kontrol S88)
    - LinnStrumentProfile (for LinnStrument)
    - MojoPedalsProfile (for Crumar MojoPedals)
    """
    # TODO Phase 2: Add device-specific profile matching
    # For now, always return generic profile
    return GenericKeyboardProfile(device_name)
