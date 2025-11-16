# P172: Lyra Live

**Intelligent Ear Training with MIDI Hardware Awareness**

Transform your MIDI devices into personalized music teachers. Lyra Live knows about your S88 keyboard, LinnStrument, and MojoPedals—using their unique capabilities to teach intervals, chords, and melodies through your actual instruments, orchestrated via Ableton Live.

---

## 🎯 What This Does

- **Device-Aware Practice**: Detects your MIDI hardware and adapts exercises to leverage specific capabilities
- **Ableton-Orchestrated**: Automatically creates sessions, routes MIDI, and plays exercises via your existing Ableton MCP server
- **Real Ear Training**: Not computer keyboard exercises—practice on your actual instruments
- **Progressive Learning**: Start simple (intervals), build to complex (Beatles melodies by ear)

---

## 🚀 Quick Start (MVP - Phase 1)

### Prerequisites

```bash
# Python 3.9+
python3 --version

# P050 Ableton MCP Server running
# Check: curl http://localhost:8080/health

# At least one MIDI device connected
```

### Installation

```bash
# Clone repository
cd /Users/jeremybradford/SyncedProjects/P172_lyra-live

# Install dependencies
pip install -r requirements.txt
```

### Run Your First Exercise

```bash
# List available MIDI devices
python -m cli list-devices

# Run interval recognition drill
python -m cli practice-intervals --device "Your Device Name" --num-exercises 5

# Run chord quality drill
python -m cli practice-chords --num-exercises 5 --chord-types triads

# Run melody imitation drill
python -m cli practice-melody --num-exercises 5 --melody-length 6

# Run rhythm drill (requires drum kit)
python -m cli practice-rhythm-snare --subdivision eighth --tempo 80 --bars 4
python -m cli practice-rhythm-kit --pattern backbeat --tempo 80 --bars 4

# Run voice/pitch exercises (requires microphone)
python -m cli practice-voice-pitch --exercises 10
python -m cli practice-voice-scale --exercises 5 --scales major,minor
python -m cli practice-voice-sightsing --exercises 5 --length 4

# Run a deterministic demo (for video recording)
python -m cli demo-intervals --mode correct
```

**What happens**:
1. Lyra plays an exercise via Ableton (or shows visual feedback)
2. You play the response on your MIDI device
3. Lyra validates and gives feedback ("Correct! That's a perfect fifth")
4. Repeat for N exercises
5. See your score and accuracy percentage

---

## 🏗️ Architecture

```
Lyra Live (P172)
      ↓
   Device Profiles (Keyboards, Drum Kits, Voice/Mic)
      ↓
   Exercise Engine (Intervals, Chords, Melodies, Rhythm, Voice)
      ↓
   Session Manager (Orchestrate practice flow)
      ↓
   Ableton Backend (Wrapper around P050 MCP)
      ↓
   P050 Ableton MCP Server (Controls Ableton Live)
```

**Key Principle**: Lyra sits ON TOP of P050—never modifies that codebase

---

## 📁 Project Structure

```
P172_lyra-live/
├── lyra_live/              # Main package
│   ├── devices/            # Device profiles
│   │   ├── generic_keyboard.py  # Standard MIDI keyboards
│   │   ├── drum_kit.py         # Donner drum kit
│   │   └── test_device.py      # Simulation device
│   ├── ear_training/       # Keyboard exercises
│   │   ├── intervals.py
│   │   ├── chords.py
│   │   ├── melodies.py
│   │   └── rhythm.py           # Drum rhythm exercises
│   ├── voice/              # Voice/pitch detection
│   │   ├── pitch.py           # Aubio-based pitch detector
│   │   ├── exercises.py       # Singing exercises
│   │   └── test_utils.py      # Voice simulation
│   ├── lessons/            # Lesson/MIDI system
│   ├── demos/              # Demo flows for videos
│   ├── ableton_backend/    # P050 MCP wrapper
│   ├── sessions/           # Session orchestration
│   └── config/             # Configuration
├── tests/                  # pytest tests (66 tests)
│   ├── unit/               # Unit tests
│   │   ├── test_intervals.py
│   │   ├── test_chords.py
│   │   ├── test_melodies.py
│   │   └── test_voice.py
│   └── test_e2e.py        # End-to-end tests
├── docs/                   # Documentation
├── config/                 # YAML configs
├── cli.py                 # CLI interface
├── README.md              # This file
└── requirements.txt       # Dependencies
```

---

## 🎵 Supported Devices

### Phase 1 (MVP) ✅
- **Generic MIDI Keyboard**: Any standard MIDI device (fallback profile)

### Phase 3 ✅
- **Donner Drum Kit**: 5-piece e-drums with 3 cymbals for rhythm exercises
- **Voice/Microphone Input**: Real-time pitch detection for singing exercises

### Phase 4 (Coming Soon) 🔄
- **Native Instruments S88**: With Light Guide hints for chord tones
- **LinnStrument**: MPE expressiveness + LED grid patterns
- **Crumar MojoPedals**: 13-note bass pedalboard for root movement

---

## 🎓 Exercise Types

### Phase 1 (MVP) ✅
1. **Interval Recognition**: Identify intervals by ear (unison through octave)

### Phase 2 ✅
1. **Chord Quality**: Major, minor, diminished, augmented triads + 7th chords
2. **Melody Imitation**: Play back 4-8 note melodic phrases
3. **Lesson System**: Load MIDI files and practice phrases

### Phase 3 ✅
1. **Rhythm Exercises**: Snare timing drills and full kit patterns (Donner drum kit support)
   - Single-limb timing accuracy with ±50ms tolerance
   - Rush/drag detection and feedback
   - Backbeat and syncopated patterns
2. **Voice/Pitch Detection**: Singing exercises with real-time pitch analysis
   - Pitch matching with cents deviation (±50 cents tolerance)
   - Scale singing (major, minor, pentatonic)
   - Sight-singing melodic phrases

### Phase 4 🎵
1. **Beatles Pack**: Learn iconic melodies by ear ("Yesterday", "Let It Be", etc.)
2. **Walking Bass**: Pedal exercises with chord changes
3. **ii-V-I Progressions**: In all keys with visual hints
4. **Device-Specific Features**: S88 Light Guide, LinnStrument MPE + LED grid, MojoPedals

---

## 🧪 Development

### Run Tests

```bash
# All tests
pytest tests/

# Unit tests only
pytest tests/unit/ -v

# Specific test
pytest tests/unit/test_intervals.py -v
```

### Development Setup

```bash
# Install in editable mode
pip install -e .

# Run linting
flake8 lyra_live/

# Type checking
mypy lyra_live/
```

---

## 📚 Documentation

- **PRD.md**: Complete product vision and requirements
- **ARCHITECTURE.md**: Technical architecture and design decisions
- **CLAUDE_CODE_SETUP.md**: Development guide for Claude Code Web
- **PHASE1_TASKS.md**: Detailed MVP implementation tasks

---

## 🔧 Configuration

**Global Settings** (`config/settings.yml`):
```yaml
ableton_mcp:
  host: localhost
  port: 8080

practice:
  default_tempo: 80
  use_lights_when_available: true  # Phase 2
```

**Device Mappings** (`config/devices.yml`):
```yaml
devices:
  - name_pattern: "Komplete Kontrol S88.*"
    profile: "NativeS88Profile"  # Phase 2
    
  - name_pattern: "LinnStrument.*"
    profile: "LinnStrumentProfile"  # Phase 2
    
  - name_pattern: ".*"
    profile: "GenericKeyboardProfile"  # Fallback
```

---

## 🛠️ Troubleshooting

### "No MIDI devices found"
Check MIDI connections:
```bash
python -c "import mido; print(mido.get_input_names())"
```

### "P050 Ableton MCP server not reachable"
1. Verify P050 is running: `curl http://localhost:8080/health`
2. Check P050 logs for errors
3. Ensure Ableton Live is open

### "ImportError: No module named 'mido'"
Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 🗺️ Roadmap

### ✅ Phase 1: MVP (Complete)
- [x] Project structure
- [x] Device profiles (generic keyboard)
- [x] Interval recognition exercises
- [x] Ableton backend stub
- [x] CLI interface
- [x] Unit tests (18 tests)

### ✅ Phase 2: Exercise Expansion (Complete)
- [x] Chord quality exercises (triads + 7th chords)
- [x] Melody imitation exercises
- [x] Lesson/MIDI file system
- [x] TestDeviceProfile for simulation
- [x] End-to-end tests (47 tests total)
- [x] Demo flows for video recording

### ✅ Phase 3: Percussion & Voice (Complete)
- [x] Drum kit device profile (DrumKitProfile, DonnerDrumKitProfile)
- [x] Rhythm exercises with timing validation (±50ms tolerance)
- [x] Rush/drag detection for rhythm feedback
- [x] Voice/pitch detection (aubio + pyaudio)
- [x] Pitch matching exercises (±50 cents tolerance)
- [x] Scale singing exercises (major, minor, pentatonic)
- [x] Sight-singing melodic phrases
- [x] TestVoiceInput for simulation
- [x] Voice unit tests (19 tests, 66 tests total)
- [x] CLI commands for rhythm and voice
- [ ] TestDrumKitProfile for rhythm simulation
- [ ] Rhythm demo flows for video recording

### 🎵 Phase 4: Device-Specific Features & Content
- [ ] S88 profile with Light Guide integration
- [ ] LinnStrument profile with MPE + LED grid
- [ ] MojoPedals profile (13-note bass pedalboard)
- [ ] Beatles melody pack (iconic songs)
- [ ] Multi-device coordination (pedals + keyboard)

### 🚀 Phase 5: Intelligence & Integration
- [ ] Progress tracking and analytics
- [ ] Adaptive difficulty
- [ ] Custom curriculum builder
- [ ] SADB integration for long-term growth tracking
- [ ] Voice control via Whisper MCP
- [ ] Export sessions as MIDI for review

---

## 🤝 Related Projects

- **P050_ableton-mcp**: Ableton Live MCP server (dependency)
- **P171_elevenlabs-music-mcp**: Music generation for practice sessions
- **P033_resonance-prime**: Betty Memory MCP (future integration)

---

## 📄 License

Personal project - see main SyncedProjects LICENSE

---

## 🎉 Get Started

Ready to practice? Follow the Quick Start above and run your first interval drill!

**Remember**: The goal isn't just to drill exercises—it's to deeply learn your instruments and train your ear through deliberate, device-aware practice.

---

*"Not just ear training—intelligent musical education through your actual instruments."*

**Status**: 🟢 Phase 3 Complete - Percussion & Voice Support Working
**Last Updated**: 2025-11-16
**Next Milestone**: Device-specific features (S88 Light Guide, LinnStrument MPE, MojoPedals)