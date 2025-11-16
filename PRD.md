# Product Requirements Document: Lyra Live

**Project**: P172 - Lyra Live  
**Category**: Personal Project  
**Status**: MVP Planning  
**Created**: 2025-11-16  
**Owner**: Jeremy Bradford

---

## Executive Summary

**Lyra Live** is an intelligent ear training and MIDI orchestration platform that treats your hardware as first-class citizens in your musical education. It sits on top of your existing Ableton MCP server (P050), orchestrating practice sessions across multiple MIDI devices—from the Native Instruments S88 keyboard with its Light Guide, to the expressive LinnStrument MPE controller, to the Crumar MojoPedals bass pedalboard.

**The Vision**: Instead of generic computer-based ear training that ignores your actual instruments, Lyra Live knows what you're playing on, what it can do, and how to teach you using those specific capabilities. Play on the S88? It lights up chord tones in color. Switch to LinnStrument? It maps intervals across the grid and uses MPE expressiveness. Working on bass pedals? It gives you walking bass and pedal tone exercises.

**Core Philosophy**: MIDI is not the enemy—it's the center. Treat each device as a unique learning partner with its own strengths.

---

## Problem Statement

### Current Pain Points

1. **Generic Ear Training Tools**
   - Computer-based exercises that ignore your actual instruments
   - No integration with your DAW or hardware
   - One-size-fits-all approach that doesn't leverage device capabilities

2. **Disconnected Hardware**
   - S88 Light Guide sits unused except in NI software
   - LinnStrument's MPE and grid layout not leveraged for learning
   - MojoPedals used only for performance, not practice
   - Each device operates in isolation

3. **Manual Session Setup**
   - Creating ear training sessions in Ableton is tedious
   - Routing MIDI, creating tracks, setting up instruments takes time
   - No structured curriculum or progression tracking

4. **Lost Practice Ideas**
   - "I should practice Beatles melodies by ear"
   - "I want to drill ii-V-I in all keys with lights showing me the chord tones"
   - "Let me use pedals for root movement while S88 shows chord shapes"
   - These ideas never materialize because there's no system to support them

### User Story (Jeremy's Daily Practice)

**Current Reality**:
- Opens Ableton, creates tracks manually
- Routes MIDI from keyboard
- Tries to remember which chord tones to practice
- S88 lights sit dark and useless
- LinnStrument used only for performance, not systematic learning
- MojoPedals gather dust between gigs

**Desired Reality with Lyra Live**:
- Run: `lyra practice intervals-and-triads --device s88`
- Lyra detects S88, creates Ableton session automatically
- Exercise 1: "Listen to this interval" (Lyra plays via Ableton)- S88 lights up showing the two notes in different colors (root=red, other=blue)
- "Now play that interval" → Jeremy plays
- Lyra validates: "Correct! That's a perfect fifth"
- Exercise 2: "Here's a major triad" → Lights show root/third/fifth in colors
- "Now play it without lights" → Lights go dark, Jeremy plays from memory
- After 10 exercises: "You got 9/10 correct. Struggled with minor sixths—let's do 5 more"

Later that day:
- Run: `lyra beatles "yesterday" --device linnstrument`
- Lyra loads "Yesterday" melody, maps it to LinnStrument's grid
- Shows first phrase as lit LEDs on the surface
- Jeremy plays along, feeling the melody spatially
- "Now play it without hints" → LEDs turn off
- Lyra scores accuracy and timing

Evening bass practice:
- Run: `lyra pedal-tones --device mojo --duration 10min`
- Lyra creates walking bass exercises specifically for pedals
- Uses S88 or LinnStrument simultaneously to show chord changes
- Practices root movement patterns that work with hands and feet together

---

## Product Goals

### Primary Goal: MVP (Phase 1)
Build a device-aware ear training system that can:
1. Detect and profile MIDI devices (S88, LinnStrument, MojoPedals, generic keyboards)
2. Run basic interval recognition exercises
3. Orchestrate Ableton sessions automatically via P050 MCP server
4. Provide immediate feedback on correctness
5. Work without device-specific features (lights, MPE) initially—just MIDI notes

### Secondary Goals: Enhanced Features (Phase 2)
1. S88 Light Guide integration for visual chord/interval hints
2. LinnStrument MPE expressiveness in exercises
3. Beatles melody pack (iconic melodies for ear training)
4. Multi-device coordination (pedals + keyboard simultaneously)
5. Progress tracking and adaptive difficulty

### Long-term Vision (Phase 3+)
1. Custom curriculum builder ("30-day chord mastery")
2. Export practice sessions as MIDI files for review
3. Integration with SADB for tracking musical growth over time
4. Voice control via Whisper MCP ("Lyra, drill me on seventh chords")
5. Collaborative practice (network multiple instances)
---

## Technical Requirements

### System Architecture

```
Lyra Live (P172)
      ↓
   [Device Layer]
   - Native S88 Profile (MIDI + Light Guide stub)
   - LinnStrument Profile (MPE + LED grid)
   - MojoPedals Profile (13-note pedalboard)
   - Generic Keyboard Profile (fallback)
      ↓
   [Ear Training Engine]
   - Abstract exercise definitions
   - Device-agnostic note/rhythm representation
   - Correctness validation
      ↓
   [Session Orchestration]
   - Practice session flow
   - Exercise sequencing
   - Progress tracking
      ↓
   [Ableton Backend]
   - Wrapper around P050 MCP Server
   - Creates tracks, routes MIDI, places clips
   - Does NOT modify P050 codebase
      ↓
   [P050 Ableton MCP Server]
   - Already running as service
   - Provides HTTP API for DAW control
```

### Core Components

#### 1. Device Profiles (`lyra_live/devices/`)

**Base Device Profile** (`base.py`):
```python
class DeviceProfile:
    name_pattern: str  # Regex to match MIDI device name
    capabilities: DeviceCapabilities  # What can this device do?
    
    def send_note(self, pitch, velocity, duration)
    def send_hint(self, notes: List[Note], colors: Dict)    def detect_input(self) -> MIDIEvent
    def get_supported_ranges(self) -> Range  # What notes can it play?
```

**Native S88 Profile** (`native_s88.py`):
- Standard MIDI keyboard with 88 keys
- Polyphonic aftertouch supported
- Light Guide integration (TODO for Phase 2)
  - Proprietary NI protocol, not standard MIDI
  - Will require reverse-engineered SysEx or Komplete Kontrol integration
  - Initial MVP: works without lights, just MIDI

**LinnStrument Profile** (`linnstrument.py`):
- MPE controller (Multi-dimensional Polyphonic Expression)
- Per-note X/Y movement + pressure
- Configurable grid layout (intervals per row/column)
- LED grid for visual hints (MIDI-controllable)
- Initial MVP: treat as standard MIDI, MPE for Phase 2

**MojoPedals Profile** (`mojo_pedals.py`):
- 13-note MIDI pedalboard
- USB class-compliant
- Can be used for:
  - Note triggers (bass lines, root movement)
  - Transport control (next/previous exercise)
  - Chord root pedals while hands play upper structure

**Generic Keyboard Profile** (`generic_keyboard.py`):
- Fallback for any unknown MIDI device
- Assumes standard note on/off, no special features
- Still fully functional for ear training

#### 2. Ear Training Engine (`lyra_live/ear_training/`)

**Exercise Types** (MVP):
1. **Interval Recognition**
   - Play random interval → user identifies → validation
   - Support: unison through octave, ascending/descending

2. **Chord Quality Recognition**
   - Play chord (major, minor, diminished, augmented) → user identifies
   - Can show visual hints (colors on S88) before testing without

3. **Melody Imitation**
   - Play 4-8 note phrase → user plays back → score accuracy
   - Start with simple stepwise motion, progress to leaps

**Exercise Data Structure**:
```python
@dataclass
class Exercise:
    id: str
    type: ExerciseType  # interval, chord, melody, rhythm
    notes: List[Note]   # Abstract representation
    metadata: Dict      # key, tempo, difficulty, hints
    
@dataclass
class Note:
    pitch: int          # MIDI note number
    duration_ms: int
    role: str           # "root", "third", "fifth", etc.
    color_hint: str     # For devices with lights (optional)
```

**Beatles Pack** (Phase 2):
- Library of iconic melodies: "Yesterday", "Let It Be", "Hey Jude", etc.
- Stored as MIDI clips + metadata (title, key, difficulty, sections)
- Can be loaded into any exercise type
- Jeremy plays along, then without hints, then scored

#### 3. Ableton Backend (`lyra_live/ableton_backend/`)

**Purpose**: High-level wrapper around P050 MCP Server
**Key Methods**:
```python
class AbletonBackend:
    def create_ear_training_session(self, device_name: str) -> Session:
        """Create new Live set with routing for specified device"""
        
    def place_exercise_clip(self, exercise: Exercise, track_num: int):
        """Convert abstract exercise to MIDI clip and place in session"""
        
    def route_midi_input(self, device_name: str, track_num: int):
        """Route MIDI from device to track for capture"""
        
    def play_exercise(self, exercise: Exercise):
        """Trigger playback of exercise via Ableton"""
        
    def capture_user_response(self, timeout_s: int) -> List[Note]:
        """Record MIDI input and return as note sequence"""
```

**Assumption**: P050 Ableton MCP Server is already running and reachable.  
**Non-Goal**: Modifying P050 codebase—treat it as a black-box service.

#### 4. Session Orchestration (`lyra_live/sessions/`)

**Practice Session Flow**:
1. Detect available MIDI devices
2. User selects device and exercise type
3. Create Ableton session template via backend
4. Run exercise sequence:
   - Play example → wait → capture input → validate → give feedback
5. Track progress (correct/incorrect, time taken)
6. Adapt difficulty based on performance

**Session Manager**:
```python
class SessionManager:
    def start_practice(self, device: DeviceProfile, exercises: List[Exercise]):
        """Orchestrate full practice session"""
        
    def run_exercise(self, exercise: Exercise) -> ExerciseResult:
        """Run single exercise: play → capture → validate"""
        
    def validate_response(self, expected: List[Note], actual: List[Note]) -> Score:
        """Compare user input to correct answer"""
```

#### 5. Configuration (`lyra_live/config/`)

**Device Mappings** (`devices.yml`):
```yamldevices:
  - name_pattern: "Komplete Kontrol S88.*"
    profile: "NativeS88Profile"
    capabilities:
      lights: true  # TODO: Phase 2
      aftertouch: true
      
  - name_pattern: "LinnStrument.*"
    profile: "LinnStrumentProfile"
    capabilities:
      mpe: true
      led_grid: true
      
  - name_pattern: ".*Mojo.*Pedals.*"
    profile: "MojoPedalsProfile"
    capabilities:
      pedals: 13
```

**Global Settings** (`settings.yml`):
```yaml
ableton_mcp:
  host: "localhost"
  port: 8080
  
practice:
  default_tempo: 80
  use_lights_when_available: true
  enable_beatles_pack: false  # Phase 2
  
progress:
  save_results: true
  results_path: "~/Music/Lyra/progress/"
```

---

## MVP Feature Scope (Phase 1)

### In Scope ✅
1. Device detection and profiling (S88, LinnStrument, MojoPedals, generic)
2. Three exercise types: interval recognition, chord quality, melody imitation
3. Ableton session automation via P050 MCP
4. CLI interface for session management
5. Basic correctness validation (pitch only, not timing yet)
6. Simple text-based feedback ("Correct!", "Try again—that was a major third")

### Out of Scope (Phase 2+) ❌
1. S88 Light Guide integration (proprietary protocol)2. LinnStrument MPE features and LED grid control
3. Beatles melody pack (will need manual MIDI entry)
4. Multi-device coordination (pedals + keyboard simultaneously)
5. Progress tracking dashboard/UI
6. Timing validation (correct notes but wrong rhythm)
7. Voice control integration
8. Custom curriculum builder

---

## Success Criteria

### Phase 1 Complete When:
- ✅ CLI can detect and list available MIDI devices
- ✅ User can select device and load appropriate profile
- ✅ Interval recognition exercise works end-to-end:
  - Lyra plays interval via Ableton
  - User plays answer on selected device
  - Lyra validates and gives feedback
- ✅ Basic chord quality exercise works (major/minor/diminished/augmented)
- ✅ Simple 4-note melody imitation exercise works
- ✅ Ableton session created automatically with correct routing
- ✅ No crashes, graceful error handling
- ✅ README has clear setup instructions

### Ultimate Success (Long-term):
- Jeremy practices daily using Lyra Live instead of manual Ableton setup
- Progress is tracked over time, showing improvement
- Beatles melodies learned by ear, not by reading charts
- S88 lights guide learning, then turn off for validation
- MojoPedals integrated into practice (not just performance)

---

## Dependencies

### Internal Dependencies
- **P050 Ableton MCP Server**: Must be running and reachable
  - Provides HTTP API for DAW control
  - Already implemented and stable
  - Lyra does NOT modify P050 code

### External Dependencies (Python packages)
- `mido`: MIDI I/O in Python
- `rtmidi`: Real-time MIDI for device detection
- `requests`: HTTP client for P050 MCP API calls- `pyyaml`: Configuration file parsing
- `pytest`: Testing framework

### Hardware Dependencies
- At least one MIDI device (S88, LinnStrument, MojoPedals, or generic keyboard)
- Ableton Live running on same machine as P050 MCP server
- macOS (Jeremy's environment)

---

## Technical Constraints

### Performance
- Exercise playback should be immediate (<100ms latency)
- MIDI input capture should feel real-time
- Session creation via Ableton backend: <2 seconds acceptable

### Compatibility
- Python 3.9+ (match P050 requirements)
- macOS Sequoia (Jeremy's system)
- Ableton Live 11+ (with P050 MCP compatibility)

### S88 Light Guide Limitation
- Light control uses proprietary NI protocol, not standard MIDI
- Options for Phase 2:
  1. Reverse-engineer SysEx messages (like SynthesiaKontrol project)
  2. Integrate with Komplete Kontrol software
  3. Accept that lights may not work initially—focus on MIDI functionality

---

## Open Questions

### For Jeremy to Clarify
1. **P050 API Coverage**: Does P050 MCP expose everything Lyra needs?
   - Track creation, MIDI routing, clip placement, playback control?
   - If not, what's missing?

2. **Device Priority**: Which device is most important for MVP?
   - S88 (with lights eventually)?
   - LinnStrument (for grid-based learning)?
   - Generic keyboard (maximum compatibility)?

3. **Exercise Preferences**: Which exercises excite you most?
   - Intervals → chords → progressions?
   - Beatles melodies?
   - Walking bass patterns?
4. **Progress Tracking**: How should results be stored?
   - Simple JSON logs?
   - SQLite database?
   - Integration with SADB for long-term tracking?

### Technical Questions
1. **MIDI Device Enumeration**: Test on Jeremy's Mac—does `mido` reliably detect all devices?
2. **P050 MCP Reliability**: Can Lyra assume P050 is always running, or handle offline gracefully?
3. **Concurrency**: If Betty or another agent is using Ableton via P050, does that conflict with Lyra?

---

## Implementation Phases

### Phase 1: MVP (Target: 1-2 Claude Code Web sessions)
**Goal**: Basic interval recognition working on generic keyboard

**Tasks**:
1. Project scaffold with directory structure
2. Device profile base class + generic keyboard implementation
3. Basic MIDI input/output via `mido`
4. Interval exercise data structures
5. Minimal Ableton backend (create session, place clip, play)
6. CLI entry point: list devices, select device, run interval drill
7. Simple validation and feedback
8. Unit tests for core logic

**Deliverables**:
- Working CLI that runs interval drills
- Can be tested immediately with any MIDI keyboard
- Clean, extensible code for Phase 2 additions

### Phase 2: Enhanced Devices (Target: 1 session)
**Tasks**:
1. S88 profile (MIDI working, lights stubbed with TODO)
2. LinnStrument profile (standard MIDI, MPE stubbed)
3. MojoPedals profile
4. Chord quality and melody imitation exercises
5. Device capabilities detection and graceful fallbacks

### Phase 3: Special Features (Target: 2-3 sessions)
**Tasks**:1. S88 Light Guide integration (research NI protocol)
2. LinnStrument MPE + LED grid
3. Beatles melody pack (manually enter a few songs)
4. Multi-device coordination
5. Progress tracking and analytics

### Phase 4: Intelligence & Polish (Future)
1. Adaptive difficulty based on performance
2. Custom curriculum builder
3. SADB integration for long-term tracking
4. Voice control via Whisper MCP
5. Export sessions as MIDI for review

---

## Risk Assessment

### High Risk
- **S88 Light Guide**: Proprietary protocol may be harder than expected
  - Mitigation: Make lights optional, focus on MIDI functionality first
  
### Medium Risk
- **P050 API Gaps**: May not expose everything Lyra needs
  - Mitigation: Test early, add to P050 if needed (or find workarounds)
  
- **MIDI Latency**: Real-time feel is critical
  - Mitigation: Profile early, use async I/O, optimize hot paths

### Low Risk
- **Device Detection**: `mido` is mature and reliable
- **Basic Exercise Logic**: Straightforward Python data structures
- **CLI Interface**: Standard Python patterns

---

## Appendix: Betty's Original Prompt

For reference, here's Betty's excellent original prompt that captured the vision:

```
I want to create a new repo called P0xx_lyra-live that sits on top of my existing P050_ableton-mcp project.

Goals for Lyra Live:
• Treat P050_ableton-mcp as a backend service for controlling Ableton Live.
• Focus on ear training and MIDI device orchestration, not low-level DAW control.
• Work with multiple hardware devices: Native Instruments S88 keyboard, LinnStrument, 
  Crumar MojoPedals, and generic MIDI devices.

[...detailed requirements follow...]
```