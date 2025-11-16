# Claude Code Web - Development Setup Guide

**Project**: P172 - Lyra Live  
**Phase**: Phase 1 MVP  
**Time Budget**: Efficient use of Claude Code Web credit

---

## 🎯 Quick Context

You're building an intelligent ear training platform that knows about Jeremy's actual MIDI hardware (S88 keyboard, LinnStrument, MojoPedals) and orchestrates practice sessions through his existing Ableton MCP server (P050).

**Key Goal**: Get Phase 1 MVP working—basic interval recognition on any MIDI device.

**Critical**: This project sits ON TOP of P050—don't modify that codebase. Treat it as a service.

---

## 📋 Before You Start

### Documents to Read First
1. **PRD.md** - Complete product vision (read sections 1-4 minimum)
2. **ARCHITECTURE.md** - System design overview
3. **PHASE1_TASKS.md** - Your detailed implementation roadmap

### Key Concepts to Understand
- **Device Profiles**: Each MIDI device (S88, LinnStrument, etc.) has unique capabilities
- **P050 Ableton MCP**: Existing HTTP server that controls Ableton Live
- **Abstract Exercises**: Device-agnostic note/rhythm representations
- **MVP Focus**: Basic interval drills on generic MIDI keyboard first

---

## 🚀 Development Workflow

### Step 1: Understand the Codebase Structure (10 min)

```
P172_lyra-live/
├── lyra_live/              # Main package
│   ├── devices/            # Device profiles (S88, LinnStrument, etc.)
│   ├── ear_training/       # Exercise definitions
│   ├── ableton_backend/    # P050 MCP wrapper
│   ├── sessions/           # Practice session orchestration
│   └── config/             # Configuration loading
├── tests/                  # pytest tests
│   ├── unit/
│   └── integration/
├── docs/                   # Additional documentation
├── config/                 # YAML configs for devices
└── README.md              # Quick start guide
```

### Step 2: Environment Setup (5 min)

```bash# Install dependencies
pip install -r requirements.txt

# Set up environment (if needed for future P050 API calls)
cp .env.example .env
```

### Step 3: Implementation Order - Follow PHASE1_TASKS.md Exactly

Work through these in sequence:

**Part 1: Foundation (30-45 min)**
1. Device profile base class
2. Generic keyboard profile
3. MIDI device detection using `mido`

**Part 2: Exercise Engine (30-45 min)**
1. Exercise data structures (Exercise, Note, ExerciseResult)
2. Interval recognition exercise
3. Validation logic (compare expected vs actual notes)

**Part 3: Ableton Backend (30-45 min)**
1. P050 MCP HTTP client
2. Session creation method
3. Exercise playback method

**Part 4: Orchestration (30 min)**
1. SessionManager class
2. Exercise flow: play → capture → validate → feedback

**Part 5: CLI & Testing (30 min)**
1. CLI entry point with device selection
2. Unit tests for exercise logic
3. Integration test (mock P050 API)
---

## 🧪 Testing Strategy

### Unit Tests (Required)
```bash
# Test exercise logic
pytest tests/unit/test_exercises.py -v

# Test device profiles
pytest tests/unit/test_devices.py -v

# Test validation
pytest tests/unit/test_validation.py -v
```

### Integration Tests (Nice to have)
```bash
# Test with mock P050 API
pytest tests/integration/test_session.py -v
```

### Manual Testing (Jeremy will do)
```bash
# List devices
python -m lyra_live.cli list-devices

# Run interval drill
python -m lyra_live.cli practice intervals --device "Generic Keyboard"
```

---

## 🎯 MVP Success Criteria

You're done with Phase 1 when:
- ✅ `lyra_live.cli list-devices` shows available MIDI devices
- ✅ User can run `practice intervals` and see an interval played via Ableton
- ✅ User can play response on MIDI keyboard
- ✅ Lyra validates response and gives text feedback ("Correct! That's a perfect fifth")
- ✅ All unit tests pass
- ✅ Code is clean, documented, and extensible

---

## ⚠️ Critical Notes

### About P050 Ableton MCP Server
- **Location**: `/Users/jeremybradford/SyncedProjects/P050_ableton-mcp`
- **Assumption**: Already running on localhost (check with Jeremy)
- **API**: HTTP-based, provides DAW control methods
- **DO NOT**: Modify P050 code—treat as black box service
### About Device-Specific Features (Phase 2)
- **S88 Light Guide**: Proprietary NI protocol—stub it for now with TODO
- **LinnStrument MPE**: Advanced—treat as standard MIDI initially
- **MojoPedals**: Simple 13-note MIDI—easy to add in Phase 2

### Python Best Practices
- Type hints everywhere (`from typing import List, Dict, Optional`)
- Docstrings for public methods
- Keep classes small and focused
- Use dataclasses for data structures (`@dataclass`)

### Error Handling
- Graceful failures if P050 API unreachable
- Clear error messages for missing MIDI devices
- Don't crash on invalid user input

---

## 💡 Code Patterns to Follow

### Device Profile Pattern
```python
from lyra_live.devices.base import DeviceProfile

class GenericKeyboardProfile(DeviceProfile):
    name_pattern = ".*"  # Match anything
    
    def send_note(self, pitch: int, velocity: int, duration_ms: int):
        # Use mido to send MIDI note
        pass
    
    def detect_input(self) -> Optional[MIDIEvent]:
        # Listen for incoming MIDI
        pass
```

### Exercise Pattern
```python
from dataclasses import dataclass
from lyra_live.ear_training.base import Exercise, Note

@dataclass
class IntervalExercise(Exercise):
    interval_type: str  # "major_third", "perfect_fifth", etc.
    
    def generate(self) -> List[Note]:
        # Create two notes with specified interval
        pass
    
    def validate(self, user_notes: List[Note]) -> bool:
        # Check if user played correct interval
        pass
```
### Ableton Backend Pattern
```python
import requests

class AbletonBackend:
    def __init__(self, api_url: str = "http://localhost:8080"):
        self.api_url = api_url
    
    def create_session(self, device_name: str) -> str:
        response = requests.post(f"{self.api_url}/session/create")
        return response.json()["session_id"]
    
    def play_exercise(self, exercise: Exercise):
        # Convert exercise to MIDI clip data
        # Send to P050 API for playback
        pass
```

---

## 📚 Key Files to Reference

- **PRD.md**: Product vision, use cases, requirements
- **PHASE1_TASKS.md**: Step-by-step implementation guide with code templates
- **P050_ableton-mcp/README.md**: API documentation for Ableton control

---

## 🚫 Out of Scope for Phase 1

Don't implement these yet (Phase 2+):
- S88 Light Guide integration
- LinnStrument MPE features
- Beatles melody pack
- Multi-device coordination
- Progress tracking dashboard
- Timing validation (just pitch for now)
- Custom curriculum builder

Keep it simple: **Basic interval recognition on any MIDI keyboard**

---

## ✅ Checklist Before Calling It Done

- [ ] All code has type hints and docstrings
- [ ] Unit tests pass (`pytest tests/unit/`)
- [ ] CLI can list MIDI devices
- [ ] CLI can run basic interval drill
- [ ] README has clear setup instructions
- [ ] No P050 code was modified
- [ ] Code is clean and extensible for Phase 2

---

**Good luck! Focus on MVP first, make it solid, then we'll add the cool device-specific features.**