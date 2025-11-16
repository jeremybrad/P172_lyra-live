# Phase 1 MVP - Detailed Implementation Tasks

**Goal**: Basic interval recognition working on any MIDI keyboard via Ableton

**Time Estimate**: 2-3 hours of focused development

---

## Task Breakdown

### PART 1: Device Profile Foundation (30-45 min)

#### Task 1.1: Base Device Profile Abstract Class

**File**: `lyra_live/devices/base.py`

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Pattern
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
```

**Tests**: `tests/unit/test_device_base.py`
- Test pattern matching
- Test capabilities dataclass
#### Task 1.2: Generic Keyboard Profile

**File**: `lyra_live/devices/generic_keyboard.py`

```python
import mido
from lyra_live.devices.base import DeviceProfile, DeviceCapabilities, MIDIEvent
from typing import List, Optional

class GenericKeyboardProfile(DeviceProfile):
    """Fallback profile for any MIDI keyboard"""
    
    name_pattern = ".*"  # Matches anything
    capabilities = DeviceCapabilities()
    
    def __init__(self, device_name: str):
        self.device_name = device_name
        self.port = None
    
    def connect(self):
        """Open MIDI port"""
        self.port = mido.open_output(self.device_name)
    
    def send_note(self, pitch: int, velocity: int, duration_ms: int):
        """Send note via mido"""
        if not self.port:
            self.connect()
        msg = mido.Message('note_on', note=pitch, velocity=velocity)
        self.port.send(msg)
        # Note: duration handling will be in higher level
    
    def detect_input(self, timeout_ms: int = 5000) -> Optional[List[MIDIEvent]]:
        """Listen for MIDI input"""
        events = []
        with mido.open_input(self.device_name) as inport:
            for msg in inport.iter_pending():
                if msg.type == 'note_on':
                    events.append(MIDIEvent(
                        type='note_on',
                        pitch=msg.note,
                        velocity=msg.velocity
                    ))
        return events if events else None
```

**Tests**: `tests/unit/test_generic_keyboard.py`

#### Task 1.3: Device Discovery

**File**: `lyra_live/devices/discovery.py`

```python
import mido
from typing import List
from lyra_live.devices.base import DeviceProfile
from lyra_live.devices.generic_keyboard import GenericKeyboardProfile

def list_midi_devices() -> List[str]:
    """Get all available MIDI input devices"""
    return mido.get_input_names()

def get_device_profile(device_name: str) -> DeviceProfile:
    """Match device name to appropriate profile"""
    # For MVP, always return generic
    return GenericKeyboardProfile(device_name)
```

---

### PART 2: Exercise Engine (30-45 min)

#### Task 2.1: Core Exercise Data Structures

**File**: `lyra_live/ear_training/base.py`

```python
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class ExerciseType(Enum):
    INTERVAL = "interval"
    CHORD = "chord"
    MELODY = "melody"

@dataclass
class Note:
    """Abstract note representation"""
    pitch: int  # MIDI note number (0-127)
    duration_ms: int
    velocity: int = 80
    role: Optional[str] = None  # "root", "third", "fifth", etc.

@dataclass
class Exercise:
    """Base exercise structure"""
    id: str
    type: ExerciseType
    notes: List[Note]
    correct_response: List[Note]
    
@dataclass
class ExerciseResult:
    """Result of user's attempt"""
    exercise_id: str
    user_notes: List[Note]
    correct: bool
    feedback: str
```

#### Task 2.2: Interval Recognition Exercise

**File**: `lyra_live/ear_training/intervals.py`

```python
import random
from lyra_live.ear_training.base import Exercise, Note, ExerciseType
from typing import List

INTERVALS = {
    "unison": 0,
    "minor_second": 1,
    "major_second": 2,
    "minor_third": 3,
    "major_third": 4,
    "perfect_fourth": 5,
    "tritone": 6,
    "perfect_fifth": 7,
    "minor_sixth": 8,
    "major_sixth": 9,
    "minor_seventh": 10,
    "major_seventh": 11,
    "octave": 12,
}

class IntervalExercise:
    """Generate interval recognition exercises"""
    
    @staticmethod
    def generate(interval_type: str, root_note: int = 60) -> Exercise:
        """Create interval exercise"""
        semitones = INTERVALS[interval_type]
        notes = [
            Note(pitch=root_note, duration_ms=1000),
            Note(pitch=root_note + semitones, duration_ms=1000)
        ]
        return Exercise(
            id=f"interval_{interval_type}_{root_note}",
            type=ExerciseType.INTERVAL,
            notes=notes,
            correct_response=notes  # User should play same interval
        )
    
    @staticmethod
    def generate_random() -> Exercise:
        """Generate random interval exercise"""
        interval_type = random.choice(list(INTERVALS.keys()))
        root_note = random.randint(48, 72)  # C3 to C5
        return IntervalExercise.generate(interval_type, root_note)
```

**Tests**: `tests/unit/test_intervals.py`

#### Task 2.3: Validation Logic

**File**: `lyra_live/ear_training/validator.py`

```python
from lyra_live.ear_training.base import Note, ExerciseResult
from typing import List

class ExerciseValidator:
    """Validate user responses"""
    
    @staticmethod
    def validate_interval(expected: List[Note], actual: List[Note]) -> ExerciseResult:
        """Check if user played correct interval"""
        if len(actual) != 2:
            return ExerciseResult(
                exercise_id="",
                user_notes=actual,
                correct=False,
                feedback="Expected 2 notes, got {}".format(len(actual))
            )
        
        # Calculate intervals
        expected_interval = expected[1].pitch - expected[0].pitch
        actual_interval = actual[1].pitch - actual[0].pitch
        
        correct = (expected_interval == actual_interval)
        feedback = "Correct!" if correct else f"Expected interval of {expected_interval} semitones, got {actual_interval}"
        
        return ExerciseResult(
            exercise_id="",
            user_notes=actual,
            correct=correct,
            feedback=feedback
        )
```

---

### PART 3: Ableton Backend (30-45 min)

#### Task 3.1: P050 MCP HTTP Client

**File**: `lyra_live/ableton_backend/client.py`

```python
import requests
from typing import Dict, Any
from lyra_live.ear_training.base import Exercise, Note

class AbletonMCPClient:
    """HTTP client for P050 Ableton MCP Server"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
    
    def health_check(self) -> bool:
        """Check if P050 server is reachable"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def create_session(self) -> str:
        """Create new Ableton Live session"""
        # TODO: Verify P050 API endpoint
        response = requests.post(f"{self.base_url}/session/create")
        return response.json()["session_id"]
    
    def play_exercise(self, exercise: Exercise):
        """Play exercise notes via Ableton"""
        # TODO: Convert exercise to MIDI clip
        # TODO: Trigger playback via P050
        pass
    
    def capture_input(self, timeout_s: int = 10) -> List[Note]:
        """Capture MIDI input from device"""
        # TODO: Record MIDI via P050
        pass
```

**Note**: Actual P050 API endpoints need verification—stub for now

---

### PART 4: Session Orchestration (30 min)

#### Task 4.1: Session Manager

**File**: `lyra_live/sessions/manager.py`

```python
from lyra_live.devices.base import DeviceProfile
from lyra_live.ear_training.base import Exercise, ExerciseResult
from lyra_live.ear_training.intervals import IntervalExercise
from lyra_live.ear_training.validator import ExerciseValidator
from lyra_live.ableton_backend.client import AbletonMCPClient

class SessionManager:
    """Orchestrate practice sessions"""
    
    def __init__(self, device: DeviceProfile, ableton_client: AbletonMCPClient):
        self.device = device
        self.ableton = ableton_client
    
    def run_interval_drill(self, num_exercises: int = 10):
        """Run interval recognition drill"""
        results = []
        
        for i in range(num_exercises):
            # Generate exercise
            exercise = IntervalExercise.generate_random()
            
            # Play via Ableton
            print(f"\nExercise {i+1}/{num_exercises}: Listen...")
            self.ableton.play_exercise(exercise)
            
            # Get user response
            print("Now play the interval:")
            user_notes = self.device.detect_input(timeout_ms=10000)
            
            # Validate
            result = ExerciseValidator.validate_interval(
                exercise.correct_response,
                user_notes
            )
            print(result.feedback)
            results.append(result)
        
        # Summary
        correct_count = sum(1 for r in results if r.correct)
        print(f"\nSession complete: {correct_count}/{num_exercises} correct")
```

---

### PART 5: CLI & Testing (30 min)

#### Task 5.1: CLI Entry Point

**File**: `lyra_live/cli.py`

```python
import click
from lyra_live.devices.discovery import list_midi_devices, get_device_profile
from lyra_live.sessions.manager import SessionManager
from lyra_live.ableton_backend.client import AbletonMCPClient

@click.group()
def cli():
    """Lyra Live - Intelligent Ear Training"""
    pass

@cli.command()
def list_devices():
    """List available MIDI devices"""
    devices = list_midi_devices()
    click.echo("\nAvailable MIDI Devices:")
    for i, device in enumerate(devices, 1):
        click.echo(f"  {i}. {device}")

@cli.command()
@click.option('--device', default=None, help='MIDI device name')
@click.option('--num-exercises', default=10, help='Number of exercises')
def practice_intervals(device, num_exercises):
    """Run interval recognition drill"""
    # Check Ableton connection
    ableton = AbletonMCPClient()
    if not ableton.health_check():
        click.echo("Error: P050 Ableton MCP server not reachable")
        click.echo("Make sure it's running on localhost:8080")
        return
    
    # Select device
    if not device:
        devices = list_midi_devices()
        if not devices:
            click.echo("No MIDI devices found")
            return
        device = devices[0]  # Use first device
        click.echo(f"Using device: {device}")
    
    # Get profile and run session
    profile = get_device_profile(device)
    manager = SessionManager(profile, ableton)
    manager.run_interval_drill(num_exercises)

if __name__ == '__main__':
    cli()
```

**Usage**:
```bash
# List devices
python -m lyra_live.cli list-devices

# Run interval drill
python -m lyra_live.cli practice-intervals --device "Generic Keyboard" --num-exercises 5
```

#### Task 5.2: Unit Tests

**File**: `tests/unit/test_intervals.py`

```python
import pytest
from lyra_live.ear_training.intervals import IntervalExercise, INTERVALS
from lyra_live.ear_training.base import ExerciseType

def test_interval_generation():
    """Test interval exercise generation"""
    exercise = IntervalExercise.generate("perfect_fifth", root_note=60)
    assert exercise.type == ExerciseType.INTERVAL
    assert len(exercise.notes) == 2
    assert exercise.notes[0].pitch == 60
    assert exercise.notes[1].pitch == 67  # 60 + 7 semitones

def test_random_interval():
    """Test random interval generation"""
    exercise = IntervalExercise.generate_random()
    assert len(exercise.notes) == 2
    assert 48 <= exercise.notes[0].pitch <= 72
```

**File**: `tests/unit/test_validator.py`

```python
from lyra_live.ear_training.base import Note
from lyra_live.ear_training.validator import ExerciseValidator

def test_correct_interval():
    """Test validation with correct interval"""
    expected = [Note(60, 1000), Note(67, 1000)]  # Perfect fifth
    actual = [Note(48, 1000), Note(55, 1000)]    # Same interval, different octave
    result = ExerciseValidator.validate_interval(expected, actual)
    assert result.correct

def test_incorrect_interval():
    """Test validation with wrong interval"""
    expected = [Note(60, 1000), Note(67, 1000)]  # Perfect fifth
    actual = [Note(60, 1000), Note(64, 1000)]    # Major third
    result = ExerciseValidator.validate_interval(expected, actual)
    assert not result.correct
```

---

## Dependencies (requirements.txt)

```
mido>=1.3.0
python-rtmidi>=1.5.0
requests>=2.31.0
click>=8.1.0
pytest>=7.4.0
pyyaml>=6.0
```

---

## MVP Completion Checklist

- [ ] Base device profile abstract class implemented
- [ ] Generic keyboard profile working with mido
- [ ] Device discovery lists available MIDI devices
- [ ] Exercise data structures defined
- [ ] Interval exercise generator works
- [ ] Validation logic compares intervals correctly
- [ ] Ableton MCP client stubbed (health check works)
- [ ] Session manager orchestrates exercise flow
- [ ] CLI can list devices
- [ ] CLI can run interval drill
- [ ] Unit tests pass
- [ ] README documents setup and usage

---

**Next**: Once MVP works, Phase 2 adds S88/LinnStrument profiles and Beatles melodies!