# HANDOFF TO CLAUDE CODE WEB

**Project**: P172 - Lyra Live  
**Repository**: https://github.com/jeremybrad/P172_lyra-live  
**Status**: Ready for Phase 1 MVP Development  
**Created**: 2025-11-16

---

## For Claude Code Web: Start Here

### Your Mission
Build Phase 1 MVP: Basic interval recognition ear training that works with any MIDI keyboard, orchestrated through Jeremy's existing Ableton MCP server (P050).

### Documents to Read (In Order)
1. **CLAUDE_CODE_SETUP.md** - Your main development guide (start here!)
2. **PHASE1_TASKS.md** - Detailed implementation roadmap with code templates
3. **PRD.md** - Complete product vision (read sections 1-4 minimum)
4. **ARCHITECTURE.md** - System design overview

### What's Already Done
✅ Complete project structure created  
✅ All documentation written (PRD, Architecture, Setup guides)  
✅ Directory structure scaffolded  
✅ requirements.txt with dependencies  
✅ .env.example for configuration  
✅ Test infrastructure ready  
✅ Git repository initialized and pushed to GitHub

### What You Need to Build (Phase 1 MVP)
1. **Device Profiles** (`lyra_live/devices/`)
   - Base device profile abstract class
   - Generic keyboard profile using mido
   - Device discovery/detection

2. **Exercise Engine** (`lyra_live/ear_training/`)
   - Exercise data structures (Exercise, Note, ExerciseResult)
   - Interval exercise generator
   - Validation logic for comparing expected vs actual

3. **Ableton Backend** (`lyra_live/ableton_backend/`)
   - HTTP client for P050 MCP Server API
   - Methods: health_check, create_session, play_exercise
   - **Critical**: Do NOT modify P050 code—treat as service

4. **Session Orchestration** (`lyra_live/sessions/`)
   - SessionManager class
   - Exercise flow: generate → play → capture → validate → feedback

5. **CLI Interface** (`lyra_live/cli.py`)
   - Command: `list-devices` (show available MIDI devices)
   - Command: `practice-intervals` (run interval drill)

6. **Tests** (`tests/`)
   - Unit tests for exercise logic
   - Unit tests for validation
   - Integration test with mocked P050 API

### Success Criteria - You're Done When:
- ✅ `python -m lyra_live.cli list-devices` shows MIDI devices
- ✅ `python -m lyra_live.cli practice-intervals` runs interval drill
- ✅ Exercise plays via Ableton (through P050)
- ✅ User can play response on MIDI keyboard
- ✅ Lyra validates and gives feedback ("Correct! That's a perfect fifth")
- ✅ All unit tests pass
- ✅ Code is clean, documented, and extensible

### CRITICAL NOTES

**About P050 Ableton MCP Server**:
- Location: `/Users/jeremybradford/SyncedProjects/P050_ableton-mcp`
- Assumption: Already running on localhost (Jeremy will verify)
- API: HTTP-based for Ableton Live control
- **NEVER modify P050 code**—treat as black box service

**About MIDI**:
- Use `mido` library for MIDI I/O
- Use `python-rtmidi` as backend for mido
- Generic keyboard profile is fallback for any device

**About Exercise Logic**:
- Phase 1: Pitch-only validation (ignore timing/velocity)
- Keep exercise definitions device-agnostic
- Device profiles handle hardware specifics

**About Testing**:
- Unit tests required for core logic
- Mock P050 API for integration tests
- Jeremy will do manual testing with real hardware

### Quick Start Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests (as you build)
pytest tests/unit/ -v

# Test device discovery (once implemented)
python -m lyra_live.cli list-devices

# Run interval drill (once complete)
python -m lyra_live.cli practice-intervals --device "Generic Keyboard"
```

### Code Style Guidelines
- Type hints everywhere
- Docstrings for public methods
- Follow PEP 8
- Keep classes small and focused
- Use dataclasses for data structures

### Time Budget
Aim for 2-3 hours of focused development. Follow PHASE1_TASKS.md step by step—code templates are provided to speed things up.

---

## For Jeremy: What to Tell Claude Code Web

**Suggested Prompt**:

```
I've created the P172_lyra-live repository with complete documentation for an 
intelligent ear training platform.

Please read these documents to understand the project:
1. CLAUDE_CODE_SETUP.md - Your main development guide
2. PHASE1_TASKS.md - Detailed implementation roadmap with code templates
3. PRD.md - Product vision
4. ARCHITECTURE.md - System design

Your goal: Implement Phase 1 MVP - basic interval recognition on any MIDI keyboard, 
orchestrated through my existing P050 Ableton MCP server.

Follow PHASE1_TASKS.md step by step. The directory structure is already created, 
and code templates are provided. Focus on getting the MVP working first.

CRITICAL: Do NOT modify the P050_ableton-mcp project—treat it as a service.

Start with CLAUDE_CODE_SETUP.md and work through the task list.
```

---

## Project Context for Future Sessions

### Background (From Betty's Original Vision)
- Jeremy has multiple MIDI devices: S88 keyboard, LinnStrument, MojoPedals
- S88 has Light Guide LEDs (proprietary NI protocol, Phase 2 feature)
- LinnStrument has MPE + LED grid (Phase 2 feature)
- MojoPedals is 13-note bass pedalboard (Phase 2 feature)
- Jeremy already has P050 Ableton MCP server that controls Ableton Live
- Vision: Device-aware ear training that leverages unique hardware capabilities

### Why This Approach
- **Device Abstraction**: Every device gets a profile, exercises work with any device
- **On Top of P050**: Don't reinvent DAW control—use existing infrastructure
- **Progressive Enhancement**: MVP works with generic keyboard, Phase 2 adds device-specific features
- **Extensible**: Easy to add new exercise types, new devices, new features

### What Comes After MVP (Phase 2+)
- S88 Light Guide integration (chord tones in color)
- LinnStrument MPE features (per-note expression)
- Beatles melody pack (learn songs by ear)
- Multi-device coordination (pedals + keyboard simultaneously)
- Progress tracking and analytics
- SADB integration for long-term learning

---

## Repository Stats

**Files Created**: 17  
**Lines of Documentation**: ~2,000  
**Lines of Code**: 0 (ready for you to build!)

**Documentation Breakdown**:
- PRD.md: 350+ lines (complete product vision)
- ARCHITECTURE.md: 340+ lines (system design)
- CLAUDE_CODE_SETUP.md: 200+ lines (your guide)
- PHASE1_TASKS.md: 500+ lines (detailed tasks + code templates)
- README.md: 280+ lines (overview + quick start)

---

## Questions or Issues?

If anything is unclear or you need clarification:
1. Check the documentation first—it's comprehensive
2. PRD.md has "Open Questions" section
3. ARCHITECTURE.md explains design decisions
4. PHASE1_TASKS.md has code patterns and examples

Jeremy is available for questions about:
- P050 API specifics
- Device priorities
- Exercise preferences
- Architecture adjustments

---

**Ready to build! Start with CLAUDE_CODE_SETUP.md and follow PHASE1_TASKS.md. Good luck!**