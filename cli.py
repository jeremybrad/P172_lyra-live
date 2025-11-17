"""
Lyra Live CLI - Command-line interface for ear training.

Provides commands to:
- List available MIDI devices
- Run interval recognition drills
- Run chord quality recognition drills
- Run melody imitation drills
- Practice lesson phrases
"""

import click
from pathlib import Path
from lyra_live.devices.discovery import list_midi_devices, get_device_profile
from lyra_live.sessions.manager import SessionManager
from lyra_live.ableton_backend.client import AbletonMCPClient
from lyra_live.lessons.core import Lesson, LessonPhrase
from lyra_live.ear_training.base import Note
from lyra_live.standards.core import StandardsLibrary


@click.group()
def cli():
    """
    Lyra Live - Intelligent Ear Training

    Practice ear training with your actual MIDI devices, orchestrated through Ableton Live.
    """
    pass


@cli.command()
def list_devices():
    """List available MIDI devices"""
    try:
        devices = list_midi_devices()

        if not devices:
            click.echo("\n❌ No MIDI devices found")
            click.echo("   Make sure your MIDI device is connected and powered on.\n")
            return

        click.echo("\n🎹 Available MIDI Devices:")
        for i, device in enumerate(devices, 1):
            click.echo(f"   {i}. {device}")
        click.echo()

    except Exception as e:
        click.echo(f"\n❌ Error listing devices: {e}\n")


@cli.command()
@click.option('--device', default=None, help='MIDI device name (or use first available)')
@click.option('--num-exercises', default=10, help='Number of exercises to run')
def practice_intervals(device, num_exercises):
    """
    Run interval recognition drill.

    Example:
        lyra practice-intervals --device "Generic Keyboard" --num-exercises 5
    """
    try:
        # Check Ableton connection (optional for MVP)
        click.echo("\n🔍 Checking Ableton MCP server connection...")
        ableton = AbletonMCPClient()

        if not ableton.health_check():
            click.echo("⚠️  Warning: P050 Ableton MCP server not reachable")
            click.echo("   Exercises will run without Ableton playback (using visual feedback)")
            click.echo("   To enable Ableton integration, make sure P050 is running on localhost:8080\n")
        else:
            click.echo("✓ Connected to Ableton MCP server\n")

        # Select device
        if not device:
            devices = list_midi_devices()
            if not devices:
                click.echo("❌ No MIDI devices found")
                click.echo("   Make sure your MIDI device is connected and powered on.\n")
                return

            device = devices[0]  # Use first device
            click.echo(f"📱 Using device: {device}")
        else:
            click.echo(f"📱 Using device: {device}")

        # Get profile and run session
        profile = get_device_profile(device)
        manager = SessionManager(profile, ableton)
        manager.run_interval_drill(num_exercises)

    except KeyboardInterrupt:
        click.echo("\n\n👋 Bye! Keep practicing!")
    except Exception as e:
        click.echo(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


@cli.command()
@click.option('--device', default=None, help='MIDI device name (or use first available)')
@click.option('--num-exercises', default=10, help='Number of exercises to run')
@click.option('--chord-types', default='triads', help='Chord types: triads, sevenths, or all')
def practice_chords(device, num_exercises, chord_types):
    """
    Run chord quality recognition drill.

    Example:
        lyra practice-chords --num-exercises 5 --chord-types triads
    """
    try:
        # Parse chord types
        if chord_types == 'triads':
            chord_type_list = ["major", "minor", "diminished", "augmented"]
        elif chord_types == 'sevenths':
            chord_type_list = ["dominant_7", "major_7", "minor_7", "half_diminished_7"]
        elif chord_types == 'all':
            chord_type_list = None  # Use all types
        else:
            chord_type_list = None

        # Check Ableton connection
        click.echo("\n🔍 Checking Ableton MCP server connection...")
        ableton = AbletonMCPClient()

        if not ableton.health_check():
            click.echo("⚠️  Warning: P050 Ableton MCP server not reachable")
            click.echo("   Exercises will run without Ableton playback (using visual feedback)\n")
        else:
            click.echo("✓ Connected to Ableton MCP server\n")

        # Select device
        if not device:
            devices = list_midi_devices()
            if not devices:
                click.echo("❌ No MIDI devices found")
                click.echo("   Make sure your MIDI device is connected and powered on.\n")
                return

            device = devices[0]
            click.echo(f"📱 Using device: {device}")
        else:
            click.echo(f"📱 Using device: {device}")

        # Get profile and run session
        profile = get_device_profile(device)
        manager = SessionManager(profile, ableton)
        manager.run_chord_drill(num_exercises, chord_types=chord_type_list)

    except KeyboardInterrupt:
        click.echo("\n\n👋 Bye! Keep practicing!")
    except Exception as e:
        click.echo(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


@cli.command()
@click.option('--device', default=None, help='MIDI device name (or use first available)')
@click.option('--num-exercises', default=10, help='Number of exercises to run')
@click.option('--melody-length', default=5, help='Number of notes per melody')
def practice_melody(device, num_exercises, melody_length):
    """
    Run melody imitation drill.

    Example:
        lyra practice-melody --num-exercises 5 --melody-length 6
    """
    try:
        # Check Ableton connection
        click.echo("\n🔍 Checking Ableton MCP server connection...")
        ableton = AbletonMCPClient()

        if not ableton.health_check():
            click.echo("⚠️  Warning: P050 Ableton MCP server not reachable")
            click.echo("   Exercises will run without Ableton playback (using visual feedback)\n")
        else:
            click.echo("✓ Connected to Ableton MCP server\n")

        # Select device
        if not device:
            devices = list_midi_devices()
            if not devices:
                click.echo("❌ No MIDI devices found")
                click.echo("   Make sure your MIDI device is connected and powered on.\n")
                return

            device = devices[0]
            click.echo(f"📱 Using device: {device}")
        else:
            click.echo(f"📱 Using device: {device}")

        # Get profile and run session
        profile = get_device_profile(device)
        manager = SessionManager(profile, ableton)
        manager.run_melody_drill(num_exercises, melody_length=melody_length)

    except KeyboardInterrupt:
        click.echo("\n\n👋 Bye! Keep practicing!")
    except Exception as e:
        click.echo(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


@cli.command()
@click.option('--device', default=None, help='MIDI device name (or use first available)')
@click.argument('lesson_id', required=False)
def practice_lesson(device, lesson_id):
    """
    Practice a specific lesson by ID.

    For demo purposes, creates a simple lesson. In production, this would
    load from a lesson index or MIDI file.

    Example:
        lyra practice-lesson demo_lesson
    """
    try:
        # Check Ableton connection
        click.echo("\n🔍 Checking Ableton MCP server connection...")
        ableton = AbletonMCPClient()

        if not ableton.health_check():
            click.echo("⚠️  Warning: P050 Ableton MCP server not reachable")
            click.echo("   Exercises will run without Ableton playback (using visual feedback)\n")
        else:
            click.echo("✓ Connected to Ableton MCP server\n")

        # Select device
        if not device:
            devices = list_midi_devices()
            if not devices:
                click.echo("❌ No MIDI devices found")
                click.echo("   Make sure your MIDI device is connected and powered on.\n")
                return

            device = devices[0]
            click.echo(f"📱 Using device: {device}")
        else:
            click.echo(f"📱 Using device: {device}")

        # Create a demo lesson (in production, load from file/database)
        lesson = Lesson(
            id=lesson_id or "demo_lesson",
            title="Simple Melody Lesson",
            artist="Demo",
            difficulty="beginner",
            description="A simple melodic exercise"
        )

        # Add some demo phrases
        phrase1 = LessonPhrase(
            id="phrase1",
            notes=[
                Note(60, 500),  # C
                Note(62, 500),  # D
                Note(64, 500),  # E
                Note(65, 500),  # F
            ],
            description="Ascending scale fragment"
        )

        phrase2 = LessonPhrase(
            id="phrase2",
            notes=[
                Note(60, 500),  # C
                Note(64, 500),  # E
                Note(67, 500),  # G
                Note(60, 500),  # C
            ],
            description="C major arpeggio"
        )

        lesson.add_phrase(phrase1)
        lesson.add_phrase(phrase2)

        # Get profile and run lesson practice
        profile = get_device_profile(device)
        manager = SessionManager(profile, ableton)
        manager.run_lesson_practice(lesson)

    except KeyboardInterrupt:
        click.echo("\n\n👋 Bye! Keep practicing!")
    except Exception as e:
        click.echo(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


@cli.command()
@click.option('--device', default=None, help='Drum kit device name')
@click.option('--subdivision', default='eighth', type=click.Choice(['quarter', 'eighth', 'sixteenth']))
@click.option('--tempo', default=80, help='Tempo in BPM')
@click.option('--bars', default=4, help='Number of bars to play')
def practice_rhythm_snare(device, subdivision, tempo, bars):
    """
    Practice rhythm on snare drum only.

    Example:
        lyra practice-rhythm-snare --subdivision eighth --tempo 80 --bars 4
    """
    try:
        from lyra_live.devices.drum_kit import DonnerDrumKitProfile
        from lyra_live.sessions.manager import SessionManager
        from lyra_live.ableton_backend.client import AbletonMCPClient

        click.echo("\n🔍 Checking Ableton MCP server connection...")
        ableton = AbletonMCPClient()

        if not ableton.health_check():
            click.echo("⚠️  Warning: P050 Ableton MCP server not reachable\n")
        else:
            click.echo("✓ Connected to Ableton MCP server\n")

        # Select drum kit device
        if not device:
            devices = list_midi_devices()
            drum_devices = [d for d in devices if 'drum' in d.lower() or 'donner' in d.lower()]

            if not drum_devices:
                click.echo("❌ No drum kit devices found")
                click.echo("   Available devices:")
                for d in devices:
                    click.echo(f"     - {d}")
                return

            device = drum_devices[0]
            click.echo(f"🥁 Using drum kit: {device}")
        else:
            click.echo(f"🥁 Using drum kit: {device}")

        # Create drum kit profile
        profile = DonnerDrumKitProfile(device)
        manager = SessionManager(profile, ableton)

        # Run snare drill
        manager.run_rhythm_snare_drill(
            subdivision=subdivision,
            tempo_bpm=tempo,
            num_bars=bars
        )

    except KeyboardInterrupt:
        click.echo("\n\n👋 Bye! Keep grooving!")
    except Exception as e:
        click.echo(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


@cli.command()
@click.option('--device', default=None, help='Drum kit device name')
@click.option('--pattern', default='backbeat', type=click.Choice(['backbeat', 'syncopated']))
@click.option('--tempo', default=80, help='Tempo in BPM')
@click.option('--bars', default=4, help='Number of bars to play')
def practice_rhythm_kit(device, pattern, tempo, bars):
    """
    Practice rhythm patterns on full drum kit.

    Example:
        lyra practice-rhythm-kit --pattern backbeat --tempo 80 --bars 4
    """
    try:
        from lyra_live.devices.drum_kit import DonnerDrumKitProfile
        from lyra_live.sessions.manager import SessionManager
        from lyra_live.ableton_backend.client import AbletonMCPClient

        click.echo("\n🔍 Checking Ableton MCP server connection...")
        ableton = AbletonMCPClient()

        if not ableton.health_check():
            click.echo("⚠️  Warning: P050 Ableton MCP server not reachable\n")
        else:
            click.echo("✓ Connected to Ableton MCP server\n")

        # Select drum kit device
        if not device:
            devices = list_midi_devices()
            drum_devices = [d for d in devices if 'drum' in d.lower() or 'donner' in d.lower()]

            if not drum_devices:
                click.echo("❌ No drum kit devices found")
                return

            device = drum_devices[0]
            click.echo(f"🥁 Using drum kit: {device}")
        else:
            click.echo(f"🥁 Using drum kit: {device}")

        # Create drum kit profile
        profile = DonnerDrumKitProfile(device)
        manager = SessionManager(profile, ableton)

        # Run kit drill
        manager.run_rhythm_kit_drill(
            pattern_type=pattern,
            tempo_bpm=tempo,
            num_bars=bars
        )

    except KeyboardInterrupt:
        click.echo("\n\n👋 Bye! Keep grooving!")
    except Exception as e:
        click.echo(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


@cli.command()
@click.option('--exercises', default=10, help='Number of pitches to match')
@click.option('--min-pitch', default=55, help='Minimum MIDI pitch (G3)')
@click.option('--max-pitch', default=79, help='Maximum MIDI pitch (G5)')
def practice_voice_pitch(exercises, min_pitch, max_pitch):
    """
    Practice pitch matching with voice.

    Example:
        lyra practice-voice-pitch --exercises 10
    """
    try:
        from lyra_live.voice.pitch import AubioPitchDetector
        from lyra_live.sessions.manager import SessionManager
        from lyra_live.ableton_backend.client import AbletonMCPClient

        click.echo("\n🔍 Checking Ableton MCP server connection...")
        ableton = AbletonMCPClient()

        if not ableton.health_check():
            click.echo("⚠️  Warning: P050 Ableton MCP server not reachable\n")
        else:
            click.echo("✓ Connected to Ableton MCP server\n")

        # Create pitch detector
        click.echo("🎤 Initializing microphone input...")
        detector = AubioPitchDetector()

        manager = SessionManager(detector, ableton)

        # Run pitch match drill
        manager.run_voice_pitch_match_drill(
            num_exercises=exercises,
            min_pitch=min_pitch,
            max_pitch=max_pitch
        )

    except KeyboardInterrupt:
        click.echo("\n\n👋 Bye! Keep singing!")
    except ImportError as e:
        click.echo(f"\n❌ Error: {e}")
        click.echo("   Voice features require aubio and pyaudio.")
        click.echo("   Install with: pip install aubio pyaudio\n")
    except Exception as e:
        click.echo(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


@cli.command()
@click.option('--exercises', default=5, help='Number of scales to sing')
@click.option('--scales', default='major,minor', help='Comma-separated scale types')
def practice_voice_scale(exercises, scales):
    """
    Practice singing scales.

    Example:
        lyra practice-voice-scale --exercises 5 --scales major,minor
    """
    try:
        from lyra_live.voice.pitch import AubioPitchDetector
        from lyra_live.sessions.manager import SessionManager
        from lyra_live.ableton_backend.client import AbletonMCPClient

        click.echo("\n🔍 Checking Ableton MCP server connection...")
        ableton = AbletonMCPClient()

        if not ableton.health_check():
            click.echo("⚠️  Warning: P050 Ableton MCP server not reachable\n")
        else:
            click.echo("✓ Connected to Ableton MCP server\n")

        # Parse scale types
        scale_types = [s.strip() for s in scales.split(',')]

        # Create pitch detector
        click.echo("🎤 Initializing microphone input...")
        detector = AubioPitchDetector()

        manager = SessionManager(detector, ableton)

        # Run scale drill
        manager.run_voice_scale_drill(
            num_exercises=exercises,
            scale_types=scale_types
        )

    except KeyboardInterrupt:
        click.echo("\n\n👋 Bye! Keep singing!")
    except ImportError as e:
        click.echo(f"\n❌ Error: {e}")
        click.echo("   Voice features require aubio and pyaudio.")
        click.echo("   Install with: pip install aubio pyaudio\n")
    except Exception as e:
        click.echo(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


@cli.command()
@click.option('--exercises', default=5, help='Number of phrases to sing')
@click.option('--length', default=4, help='Phrase length (notes)')
def practice_voice_sightsing(exercises, length):
    """
    Practice sight-singing melodies.

    Example:
        lyra practice-voice-sightsing --exercises 5 --length 4
    """
    try:
        from lyra_live.voice.pitch import AubioPitchDetector
        from lyra_live.sessions.manager import SessionManager
        from lyra_live.ableton_backend.client import AbletonMCPClient

        click.echo("\n🔍 Checking Ableton MCP server connection...")
        ableton = AbletonMCPClient()

        if not ableton.health_check():
            click.echo("⚠️  Warning: P050 Ableton MCP server not reachable\n")
        else:
            click.echo("✓ Connected to Ableton MCP server\n")

        # Create pitch detector
        click.echo("🎤 Initializing microphone input...")
        detector = AubioPitchDetector()

        manager = SessionManager(detector, ableton)

        # Run sight-singing drill
        manager.run_voice_sight_singing_drill(
            num_exercises=exercises,
            phrase_length=length
        )

    except KeyboardInterrupt:
        click.echo("\n\n👋 Bye! Keep singing!")
    except ImportError as e:
        click.echo(f"\n❌ Error: {e}")
        click.echo("   Voice features require aubio and pyaudio.")
        click.echo("   Install with: pip install aubio pyaudio\n")
    except Exception as e:
        click.echo(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


@cli.command()
@click.option('--mode', default='correct', help='Demo mode: correct, wrong_interval, partial_melody')
def demo_intervals(mode):
    """Run interval recognition demo (deterministic, for video recording)"""
    from lyra_live.demos.demo_flows import run_interval_demo
    run_interval_demo(num_exercises=3, mode=mode)


@cli.command()
@click.option('--mode', default='correct', help='Demo mode: correct, wrong_chord')
def demo_chords(mode):
    """Run chord quality demo (deterministic, for video recording)"""
    from lyra_live.demos.demo_flows import run_chord_demo
    run_chord_demo(num_exercises=3, mode=mode)


@cli.command()
@click.option('--mode', default='correct', help='Demo mode: correct, partial_melody')
def demo_lesson(mode):
    """Run lesson practice demo (deterministic, for video recording)"""
    from lyra_live.demos.demo_flows import run_melody_lesson_demo
    run_melody_lesson_demo(mode=mode)


@cli.command()
def demo_full():
    """Run complete demo suite (all features)"""
    from lyra_live.demos.demo_flows import run_full_demo_suite
    run_full_demo_suite()


@cli.command()
@click.option('--mode', default='perfect', help='Demo mode: perfect, rushing, dragging, inconsistent')
def demo_rhythm(mode):
    """Run rhythm timing demo (deterministic, for video recording)"""
    from lyra_live.demos.demo_flows import run_rhythm_demo
    run_rhythm_demo(mode=mode)


@cli.command()
@click.option('--mode', default='perfect', help='Demo mode: perfect, rushing, dragging')
def demo_backbeat(mode):
    """Run backbeat pattern demo (deterministic, for video recording)"""
    from lyra_live.demos.demo_flows import run_rhythm_backbeat_demo
    run_rhythm_backbeat_demo(mode=mode)


@cli.command()
@click.option('--style', default=None, help='Filter by style (e.g., bebop, swing, ballad)')
@click.option('--difficulty', default=None, help='Filter by difficulty (e.g., beginner, intermediate, advanced)')
@click.option('--index-path', default='data/standards/index.yaml', help='Path to standards index file')
def list_standards(style, difficulty, index_path):
    """
    List available jazz standards from the library.

    Example:
        lyra list-standards
        lyra list-standards --style bebop
        lyra list-standards --difficulty intermediate
    """
    try:
        index_file = Path(index_path)

        if not index_file.exists():
            click.echo(f"\n❌ Standards index not found at: {index_path}")
            click.echo("   Create an index file or specify a different path with --index-path\n")
            return

        library = StandardsLibrary(index_file)

        # Apply filters using list_tunes()
        tunes = library.list_tunes(style=style, difficulty=difficulty)

        if not tunes:
            click.echo("\n📚 No standards found matching your filters\n")
            return

        click.echo(f"\n📚 Jazz Standards Library ({len(tunes)} tunes):\n")

        for tune in tunes:
            click.echo(f"   • {tune.title}")
            if tune.composer:
                click.echo(f"     Composer: {tune.composer}")
            click.echo(f"     Key: {tune.key} | Tempo: {tune.tempo} BPM | Form: {tune.form}")
            if hasattr(tune, 'style') and tune.style:
                click.echo(f"     Style: {tune.style}")
            if hasattr(tune, 'difficulty') and tune.difficulty:
                click.echo(f"     Difficulty: {tune.difficulty}")
            click.echo()

    except Exception as e:
        click.echo(f"\n❌ Error loading standards library: {e}\n")
        import traceback
        traceback.print_exc()


@cli.command()
@click.argument('tune_name')
@click.option('--loop', is_flag=True, default=True, help='Loop the backing track')
@click.option('--index-path', default='data/standards/index.yaml', help='Path to standards index file')
def play_standard(tune_name, loop, index_path):
    """
    Play a jazz standard backing track (no capture/analysis).

    Example:
        lyra play-standard "Autumn Leaves"
        lyra play-standard "All The Things You Are" --no-loop
    """
    try:
        index_file = Path(index_path)

        if not index_file.exists():
            click.echo(f"\n❌ Standards index not found at: {index_path}\n")
            return

        library = StandardsLibrary(index_file)

        # Find tune by name
        tune = library.get_tune(tune_name)

        if not tune:
            click.echo(f"\n❌ Tune not found: {tune_name}")
            click.echo("\n   Available tunes:")
            tune_list = library.list_tunes()
            for t in tune_list[:10]:
                click.echo(f"     • {t.title}")
            if len(library.tunes) > 10:
                click.echo(f"     ... and {len(library.tunes) - 10} more")
            click.echo("\n   Use 'lyra list-standards' to see all tunes\n")
            return

        # Check Ableton connection
        click.echo("\n🔍 Checking Ableton MCP server connection...")
        ableton = AbletonMCPClient()

        if not ableton.health_check():
            click.echo("❌ P050 Ableton MCP server not reachable")
            click.echo("   Make sure P050 is running on localhost:8080\n")
            return
        else:
            click.echo("✓ Connected to Ableton MCP server\n")

        click.echo(f"🎵 Playing: {tune.title}")
        if tune.composer:
            click.echo(f"   Composer: {tune.composer}")
        click.echo(f"   Key: {tune.key} | Tempo: {tune.tempo} BPM\n")

        # Get MIDI path
        midi_path = tune.get_full_midi_path(Path.cwd())

        if not midi_path.exists():
            click.echo(f"❌ MIDI file not found at: {midi_path}\n")
            return

        # Play the standard
        success = ableton.play_standard(midi_path, loop=loop)

        if success:
            click.echo("✓ Playback started")
            click.echo("\n   Press Ctrl+C to stop\n")

            # Keep running until interrupted
            import time
            while True:
                time.sleep(1)
        else:
            click.echo("❌ Failed to start playback\n")

    except KeyboardInterrupt:
        click.echo("\n\n👋 Stopping playback")
    except Exception as e:
        click.echo(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


@cli.command()
@click.argument('tune_name')
@click.option('--choruses', default=3, help='Number of choruses to play')
@click.option('--device', default=None, help='MIDI device name')
@click.option('--simulation', is_flag=True, help='Run in simulation mode (no hardware)')
@click.option('--index-path', default='data/standards/index.yaml', help='Path to standards index file')
def practice_improv(tune_name, choruses, device, simulation, index_path):
    """
    Practice improvisation over a jazz standard with analysis.

    This will:
    1. Play the backing track
    2. Capture your solo
    3. Analyze your improvisation (chord tones, guide tones, rhythm)
    4. Provide feedback and scoring

    Example:
        lyra practice-improv "Autumn Leaves" --choruses 2
        lyra practice-improv "Blue Bossa" --simulation
    """
    try:
        index_file = Path(index_path)

        if not index_file.exists():
            click.echo(f"\n❌ Standards index not found at: {index_path}\n")
            return

        library = StandardsLibrary(index_file)

        # Find tune by name
        tune = library.get_tune(tune_name)

        if not tune:
            click.echo(f"\n❌ Tune not found: {tune_name}\n")
            click.echo("   Use 'lyra list-standards' to see available tunes\n")
            return

        # Check Ableton connection (skip in simulation mode)
        ableton = AbletonMCPClient()

        if not simulation:
            click.echo("\n🔍 Checking Ableton MCP server connection...")
            if not ableton.health_check():
                click.echo("❌ P050 Ableton MCP server not reachable")
                click.echo("   Make sure P050 is running, or use --simulation flag\n")
                return
            else:
                click.echo("✓ Connected to Ableton MCP server\n")
        else:
            click.echo("\n🎭 Running in SIMULATION mode (no hardware required)\n")

        # Get device profile (only needed in real mode)
        profile = None
        if not simulation:
            if not device:
                devices = list_midi_devices()
                if not devices:
                    click.echo("❌ No MIDI devices found")
                    click.echo("   Use --simulation flag to run without hardware\n")
                    return
                device = devices[0]
                click.echo(f"📱 Using device: {device}")
            else:
                click.echo(f"📱 Using device: {device}")

            profile = get_device_profile(device)

        # Show tune info
        click.echo(f"🎵 Standard: {tune.title}")
        if tune.composer:
            click.echo(f"   Composer: {tune.composer}")
        click.echo(f"   Key: {tune.key} | Tempo: {tune.tempo} BPM | Form: {tune.form}")
        click.echo(f"   Choruses: {choruses}\n")

        # Create session manager
        manager = SessionManager(profile, ableton)

        # Run improvisation session
        click.echo("=" * 60)
        click.echo("STARTING IMPROVISATION SESSION")
        click.echo("=" * 60)
        click.echo()

        results = manager.run_improv_session(
            tune=tune,
            chorus_count=choruses,
            use_simulation=simulation
        )

        click.echo("\n" + "=" * 60)
        click.echo("SESSION COMPLETE")
        click.echo("=" * 60)

        if results:
            click.echo(f"\n✓ Analyzed {len(results)} chorus(es)")
            click.echo("\n   Review the detailed analysis above for feedback\n")

    except KeyboardInterrupt:
        click.echo("\n\n👋 Session interrupted")
    except Exception as e:
        click.echo(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


@cli.command()
def version():
    """Show Lyra Live version"""
    from lyra_live import __version__
    click.echo(f"\nLyra Live v{__version__}")
    click.echo("Intelligent Ear Training with MIDI Hardware Awareness\n")


if __name__ == '__main__':
    cli()
