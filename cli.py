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
from lyra_live.devices.discovery import list_midi_devices, get_device_profile
from lyra_live.sessions.manager import SessionManager
from lyra_live.ableton_backend.client import AbletonMCPClient
from lyra_live.lessons.core import Lesson, LessonPhrase
from lyra_live.ear_training.base import Note


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
def version():
    """Show Lyra Live version"""
    from lyra_live import __version__
    click.echo(f"\nLyra Live v{__version__}")
    click.echo("Intelligent Ear Training with MIDI Hardware Awareness\n")


if __name__ == '__main__':
    cli()
