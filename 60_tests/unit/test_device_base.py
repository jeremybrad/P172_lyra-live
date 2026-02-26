"""
Unit tests for device profile base classes and data structures.
"""

import pytest
from lyra_live.devices.base import DeviceCapabilities, MIDIEvent, DeviceProfile


def test_device_capabilities_defaults():
    """Test default device capabilities"""
    caps = DeviceCapabilities()

    assert caps.has_lights is False
    assert caps.has_aftertouch is False
    assert caps.is_mpe is False
    assert caps.note_range == (21, 108)


def test_device_capabilities_custom():
    """Test custom device capabilities"""
    caps = DeviceCapabilities(
        has_lights=True,
        has_aftertouch=True,
        is_mpe=False,
        note_range=(36, 96)
    )

    assert caps.has_lights is True
    assert caps.has_aftertouch is True
    assert caps.is_mpe is False
    assert caps.note_range == (36, 96)


def test_midi_event_note_on():
    """Test MIDI note_on event"""
    event = MIDIEvent(type='note_on', pitch=60, velocity=80, timestamp_ms=1000)

    assert event.type == 'note_on'
    assert event.pitch == 60
    assert event.velocity == 80
    assert event.timestamp_ms == 1000


def test_midi_event_note_off():
    """Test MIDI note_off event"""
    event = MIDIEvent(type='note_off', pitch=60, velocity=0, timestamp_ms=2000)

    assert event.type == 'note_off'
    assert event.pitch == 60
    assert event.velocity == 0


def test_midi_event_defaults():
    """Test MIDI event with defaults"""
    event = MIDIEvent(type='cc')

    assert event.type == 'cc'
    assert event.pitch is None
    assert event.velocity is None
    assert event.timestamp_ms == 0
