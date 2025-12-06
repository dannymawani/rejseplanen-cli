"""Output formatting utilities."""

from rich.console import Console
from rich.table import Table

from .models import Departure, Trip

console = Console()


def format_departures(departures: list[Departure], station_name: str) -> None:
    """Format and display departures."""
    if not departures:
        console.print(f"[yellow]No departures found for {station_name}[/yellow]")
        return

    table = Table(title=f"Departures from {station_name}", show_header=True)
    table.add_column("Time", style="cyan", width=8)
    table.add_column("Line", style="green", width=12)
    table.add_column("Direction", style="white", width=30)
    table.add_column("Track", style="magenta", width=6)
    table.add_column("Status", style="yellow", width=15)

    for dep in departures[:15]:  # Show max 15
        time_str = dep.time.strftime("%H:%M")

        # Status
        if dep.is_delayed:
            status = f"[red]Delayed +{dep.delay_minutes}m[/red]"
            time_str = f"[red]{dep.rtTime.strftime('%H:%M')}[/red]"
        else:
            status = "[green]On time[/green]"

        table.add_row(
            time_str,
            dep.name,
            dep.direction or "-",
            dep.track or "-",
            status
        )

    console.print(table)


def format_trip(trip: Trip) -> None:
    """Format and display a single trip."""
    console.print("\n[bold]Journey:[/bold]")
    console.print(f"Departure: {trip.departure_time.strftime('%H:%M')}")
    console.print(f"Arrival: {trip.arrival_time.strftime('%H:%M')}")
    console.print(f"Duration: {trip.duration} minutes")
    console.print(f"Changes: {trip.num_changes}")

    # Display price if available
    if trip.price is not None:
        price_str = f"[green]Price: {trip.price:.2f} {trip.currency}[/green]"
        if trip.fare_type:
            price_str += f" [dim]({trip.fare_type})[/dim]"
        console.print(price_str)

    for i, leg in enumerate(trip.legs, 1):
        console.print(f"\n[cyan]Leg {i}:[/cyan]")
        console.print(f"  {leg.name} ({leg.type})")
        console.print(f"  From: {leg.origin.name} at {leg.departure_time.strftime('%H:%M')}")
        console.print(f"  To: {leg.destination.name} at {leg.arrival_time.strftime('%H:%M')}")


def print_error(message: str) -> None:
    """Print error message."""
    console.print(f"[red]Error:[/red] {message}")


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"[green]✓[/green] {message}")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"[blue]ℹ[/blue] {message}")
