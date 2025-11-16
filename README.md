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
   Device Profiles (S88, LinnStrument, MojoPedals, Generic)
      ↓
   Exercise Engine (Intervals, Chords, Melodies)
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
│   ├── devices/            # Device profiles (S88, LinnStrument, etc.)
│   ├── ear_training/       # Exercise definitions
│   ├── ableton_backend/    # P050 MCP wrapper
│   ├── sessions/           # Practice session orchestration
│   └── config/             # Configuration loading
├── tests/                  # pytest tests
│   ├── unit/
│   └── integration/
├── docs/                   # Documentation
│   ├── PRD.md             # Product requirements
│   ├── ARCHITECTURE.md    # Technical design
│   └── PHASE1_TASKS.md    # Implementation guide
├── config/                 # YAML device configs
├── README.md              # This file
└── requirements.txt       # Python dependencies
```

---

## 🎵 Supported Devices

### Phase 1 (MVP) ✅
- **Generic MIDI Keyboard**: Any standard MIDI device (fallback profile)

### Phase 2 (Coming Soon) 🔄
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

### Phase 3 🎵
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
- [ ] S88 profile with Light Guide integration (Phase 2.5)
- [ ] LinnStrument profile with MPE + LED grid (Phase 2.5)
- [ ] MojoPedals profile (Phase 2.5)

### 🎵 Phase 3: Beatles & Intelligence
- [ ] Beatles melody pack (iconic songs)
- [ ] Multi-device coordination (pedals + keyboard)
- [ ] Progress tracking and analytics
- [ ] Adaptive difficulty

### 🚀 Phase 4: Polish & Integration
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

**Status**: 🟢 Phase 2 Complete - Full Exercise Suite Working
**Last Updated**: 2025-11-16
**Next Milestone**: Device-specific features (S88, LinnStrument, MojoPedals)