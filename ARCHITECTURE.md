# Architecture - Lyra Live

**Last Updated**: 2025-11-16  
**Status**: Phase 1 MVP

---

## System Overview

Lyra Live is a layered architecture that sits on top of the existing P050 Ableton MCP server, providing device-aware ear training without modifying the underlying DAW control infrastructure.

```
┌─────────────────────────────────────────────────┐
│           User Interface Layer (CLI)            │
│  - Device selection                             │
│  - Exercise type selection                      │
│  - Progress display                             │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│         Session Management Layer                │
│  - Practice session orchestration               │
│  - Exercise sequencing                          │
│  - Progress tracking                            │
│  - Feedback generation                          │
└─────┬──────────────────────────────┬────────────┘
      │                              │
┌─────▼─────────┐          ┌─────────▼──────────┐
│  Exercise     │          │   Device Profile   │
│  Engine       │          │   Layer            │
│               │          │                    │
│ - Intervals   │          │ - S88              │
│ - Chords      │          │ - LinnStrument     │
│ - Melodies    │          │ - MojoPedals       │
│ - Validation  │          │ - Generic          │
└───────────────┘          └─────────┬──────────┘
                                     │
                           ┌─────────▼──────────┐
                           │   MIDI I/O Layer   │
                           │   (mido/rtmidi)    │
                           └────────────────────┘
                     
┌─────────────────────────────────────────────────┐
│        Ableton Backend (P050 Wrapper)           │
│  - Session creation                             │
│  - MIDI routing                                 │
│  - Clip playback                                │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│     P050 Ableton MCP Server (Existing)          │
│  - HTTP API for Ableton Live control            │
│  - Track management, MIDI routing, playback     │
└─────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Device Profile Layer

**Purpose**: Abstract hardware differences, expose capabilities

**Key Classes**:
- `DeviceProfile` (abstract base)
- `GenericKeyboardProfile` (MVP)- `NativeS88Profile` (Phase 2)
- `LinnStrumentProfile` (Phase 2)
- `MojoPedalsProfile` (Phase 2)

**Responsibilities**:
- MIDI device detection and matching
- Send notes to device
- Capture MIDI input from device
- Expose device capabilities (lights, MPE, aftertouch, etc.)
- Handle device-specific protocols (Light Guide, MPE, LED grid)

**Data Flow**:
```
Physical Device → mido → DeviceProfile → Lyra Core
Lyra Core → DeviceProfile → mido → Physical Device
```

---

### 2. Exercise Engine

**Purpose**: Device-agnostic exercise definitions and validation

**Key Classes**:
- `Exercise` - Abstract exercise data structure
- `Note` - Abstract note representation
- `IntervalExercise` - Generate interval drills (MVP)
- `ChordExercise` - Generate chord quality drills (Phase 2)
- `MelodyExercise` - Generate melody imitation drills (Phase 2)
- `ExerciseValidator` - Validate user responses

**Data Structures**:
```python
Exercise:
  - id: str
  - type: ExerciseType (interval, chord, melody)
  - notes: List[Note]
  - correct_response: List[Note]
  - metadata: Dict

Note:
  - pitch: int (MIDI number)
  - duration_ms: int
  - velocity: int
  - role: Optional[str] (root, third, fifth, etc.)
```

**Validation Strategy**:
- Phase 1: Pitch-only (ignore timing, velocity)
- Phase 2: Add timing validation
- Phase 3: Add velocity/dynamics validation

---

### 3. Session Management Layer

**Purpose**: Orchestrate practice sessions, handle flow control

**Key Classes**:
- `SessionManager` - Main orchestrator
- `SessionState` - Track current session state
- `ProgressTracker` - Record results (Phase 2)

**Session Flow**:
1. Initialize session (select device, exercise type)
2. For each exercise:
   a. Generate exercise
   b. Play via Ableton
   c. Capture user input
   d. Validate response
   e. Provide feedback
3. Generate session summary

---

### 4. Ableton Backend

**Purpose**: High-level wrapper around P050 MCP Server

**Key Classes**:
- `AbletonMCPClient` - HTTP client for P050 API
- `SessionTemplate` - Ableton session structure for ear training

**Critical Design Decision**:
- **Never modify P050 codebase**
- Treat P050 as black-box service
- Work around any API limitations rather than adding to P050

**API Methods**:
```python
health_check() → bool
create_session() → str  
play_exercise(exercise: Exercise) → None
capture_input(timeout_s: int) → List[Note]
```

---

## Data Flow: Complete Exercise

```
1. User selects exercise type (CLI)
   ↓
2. SessionManager generates Exercise
   ↓
3. Exercise converted to MIDI clip data
   ↓
4. AbletonBackend sends to P050 MCP Server
   ↓
5. P050 creates clip in Ableton Live, triggers playback
   ↓
6. User hears exercise, plays response on MIDI device
   ↓
7. DeviceProfile captures MIDI input
   ↓
8. ExerciseValidator compares expected vs actual
   ↓
9. SessionManager generates feedback
   ↓
10. CLI displays result to user
```

---

## Technology Stack

### Core
- **Python 3.9+**: Main language
- **mido**: MIDI I/O library
- **python-rtmidi**: Real-time MIDI backend for mido
- **click**: CLI framework

### Communication
- **requests**: HTTP client for P050 API

### Testing
- **pytest**: Testing framework
- **pytest-asyncio**: Async testing support (if needed)

### Configuration
- **pyyaml**: YAML config parsing
- **python-dotenv**: Environment variable management

---

## Design Principles

### 1. Device Abstraction
Every device implements the same `DeviceProfile` interface. Exercise logic never knows about device specifics—it works with abstract `Note` objects.

### 2. Separation of Concerns
- **Devices**: Know about MIDI hardware
- **Exercises**: Know about music theory
- **Sessions**: Know about practice flow
- **Ableton Backend**: Know about P050 API

No component crosses boundaries inappropriately.

### 3. Graceful Degradation
If device-specific features unavailable (lights, MPE):
- Fall back to basic MIDI functionality
- Exercises still work
- User informed about missing features

### 4. Extensibility
New exercise types, new device profiles, new features—all added without modifying existing code.

---

## Security & Privacy

### Data Storage
- No PII collected
- Practice results stored locally (optional)
- No network calls except to localhost P050

### MIDI Access
- Only accesses MIDI devices user explicitly selects
- No background MIDI monitoring

---

## Performance Considerations

### Critical Path: Exercise Latency
```
User plays note → DeviceProfile detects → Validation → Feedback
```
**Target**: <100ms end-to-end

**Optimization strategies**:
- Async MIDI input detection
- Pre-generate exercises (not on-demand)
- Cache validation logic

### P050 API Calls
- Create session once per practice session (not per exercise)
- Batch operations where possible

---

## Error Handling

### P050 Unreachable
- Check health on startup
- Clear error message with recovery steps
- Don't crash—graceful exit

### MIDI Device Disconnected
- Detect mid-session
- Pause session, prompt to reconnect
- Resume when device returns

### Invalid User Input
- Validate input notes (in range, reasonable timing)
- Ignore spurious MIDI events
- Provide helpful feedback

---

## Future Architecture Considerations

### Phase 2 Additions
- Light Guide driver for S88
- MPE handler for LinnStrument
- LED grid controller for LinnStrument
- Multi-device coordinator (pedals + keyboard simultaneously)

### Phase 3 Additions
- Progress tracking database (SQLite)
- SADB integration for long-term learning analytics
- Curriculum builder with dependency graphs
- Voice control integration (Whisper MCP)

### Phase 4 Possibilities
- Web UI (FastAPI + React)
- Mobile companion app
- Network multiplayer practice
- AI-generated exercises based on weakness detection

---

## Testing Strategy

### Unit Tests
- Each component tested in isolation
- Mock MIDI I/O for device profile tests
- Mock P050 API for backend tests

### Integration Tests
- Full exercise flow with mocked external dependencies
- Verify session orchestration

### Manual Testing
- Real MIDI devices
- Real Ableton + P050 server
- User acceptance criteria validation

---

## Deployment

### Development
- Run from source: `python -m lyra_live.cli`
- Edit code, test immediately

### Production (Future)
- Installable package: `pip install .`
- System-wide CLI command: `lyra`
- Automatic P050 health check on startup

---

**Next**: See PHASE1_TASKS.md for detailed implementation guide