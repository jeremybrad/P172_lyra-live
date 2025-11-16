"""
Lyra Live CLI - Command-line interface for ear training.

Provides commands to:
- List available MIDI devices
- Run interval recognition drills
- (Future) Run chord and melody exercises
"""

import click
from lyra_live.devices.discovery import list_midi_devices, get_device_profile
from lyra_live.sessions.manager import SessionManager
from lyra_live.ableton_backend.client import AbletonMCPClient


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
def version():
    """Show Lyra Live version"""
    from lyra_live import __version__
    click.echo(f"\nLyra Live v{__version__}")
    click.echo("Intelligent Ear Training with MIDI Hardware Awareness\n")


if __name__ == '__main__':
    cli()
