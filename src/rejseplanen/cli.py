"""CLI commands for Rejseplanen tool."""

from datetime import datetime

import click

from .api import RejseplanenAPI
from .config import Config
from .formatter import (
    console,
    format_departures,
    format_trip,
    print_error,
    print_info,
    print_success,
)


@click.group()
@click.version_option()
def cli():
    """Rejseplanen CLI - Modern Danish public transport tool.

    Examples:
        rejs departures "Nørreport"
        rejs trip "Nørreport" "Aarhus"
        rejs save home-work "Nørreport" "DTU"
    """
    pass


@cli.command()
@click.argument("station")
@click.option("--lines", "-l", help="Filter by line names (comma-separated)")
@click.option("--limit", "-n", default=15, help="Number of departures to show")
def departures(station: str, lines: str | None, limit: int):
    """Show departures from a station.

    Examples:
        rejs departures "Nørreport"
        rejs departures "København H" --lines "A,F"
    """
    try:
        api = RejseplanenAPI()

        # Search for station
        print_info(f"Searching for station: {station}")
        locations = api.search_location(station)

        if not locations:
            print_error(f"No station found matching '{station}'")
            return

        if len(locations) > 1:
            console.print("\n[yellow]Multiple stations found:[/yellow]")
            for i, loc in enumerate(locations[:5], 1):
                console.print(f"  {i}. {loc.name}")
            console.print("\nUsing first match. Be more specific if needed.")

        location = locations[0]
        print_info(f"Getting departures from: {location.name}")

        # Get departures
        deps = api.get_departures(location.id)

        # Filter by lines if specified
        if lines:
            line_list = [line.strip() for line in lines.split(",")]
            deps = [d for d in deps if d.name in line_list]

        # Limit results
        deps = deps[:limit]

        # Display
        format_departures(deps, location.name)

    except Exception as e:
        print_error(str(e))
        raise click.Abort()


@cli.command()
@click.argument("origin")
@click.argument("destination")
@click.option("--depart-at", "-d", help="Departure time (HH:MM)")
@click.option("--date", help="Date (DD.MM.YY)")
def trip(origin: str, destination: str, depart_at: str | None, date: str | None):
    """Plan a trip between two stations.

    Examples:
        rejs trip "Nørreport" "Aarhus"
        rejs trip "København H" "Roskilde" --depart-at "14:30"
    """
    try:
        api = RejseplanenAPI()

        # Search for origin
        print_info(f"Searching for origin: {origin}")
        origin_locs = api.search_location(origin)
        if not origin_locs:
            print_error(f"Origin station not found: {origin}")
            return
        origin_loc = origin_locs[0]

        # Search for destination
        print_info(f"Searching for destination: {destination}")
        dest_locs = api.search_location(destination)
        if not dest_locs:
            print_error(f"Destination station not found: {destination}")
            return
        dest_loc = dest_locs[0]

        # Parse time if provided
        departure_time = None
        if depart_at:
            try:
                departure_time = datetime.strptime(depart_at, "%H:%M")
                departure_time = departure_time.replace(
                    year=datetime.now().year,
                    month=datetime.now().month,
                    day=datetime.now().day
                )
            except ValueError:
                print_error("Invalid time format. Use HH:MM (e.g., 14:30)")
                return

        print_info(f"Planning trip from {origin_loc.name} to {dest_loc.name}")

        # Plan trip
        trips = api.plan_trip(origin_loc.id, dest_loc.id, departure_time)

        if not trips:
            print_error("No trips found")
            return

        # Display first 3 options
        for i, t in enumerate(trips[:3], 1):
            console.print(f"\n[bold cyan]Option {i}:[/bold cyan]")
            format_trip(t)

    except Exception as e:
        print_error(str(e))
        raise click.Abort()


@cli.command()
@click.argument("station")
def search(station: str):
    """Search for stations by name.

    Examples:
        rejs search "Nørreport"
        rejs search "København"
    """
    try:
        api = RejseplanenAPI()
        print_info(f"Searching for: {station}")

        locations = api.search_location(station)

        if not locations:
            print_error(f"No stations found matching '{station}'")
            return

        console.print(f"\n[bold]Found {len(locations)} station(s):[/bold]\n")
        for loc in locations:
            console.print(f"  • {loc.name} (ID: {loc.id})")

    except Exception as e:
        print_error(str(e))
        raise click.Abort()


@cli.command()
@click.argument("address")
@click.option("--max", "-n", default=10, help="Maximum number of nearby stops to show")
def nearby(address: str, max: int):
    """Find nearest bus/train stops to an address.

    Examples:
        rejs nearby "Vesterbrogade 4A, København"
        rejs nearby "Tivoli" --max 5
    """
    try:
        api = RejseplanenAPI()
        print_info(f"Searching for address: {address}")

        # Search for the address (include addresses/POIs)
        locations = api.search_location(address, include_addresses=True)

        if not locations:
            print_error(f"Address not found: {address}")
            return

        # Get first result (most relevant)
        location = locations[0]

        # Show what we found
        loc_type = "Address" if location.type == "adr" else "Location"
        if location.type == "poi":
            loc_type = "Point of Interest"

        console.print(f"\n[bold]{loc_type}:[/bold] {location.name}")

        if location.x and location.y:
            console.print(f"[dim]Coordinates: {location.y:.6f}, {location.x:.6f}[/dim]\n")

            # Find nearby stops
            print_info("Finding nearby stops...")
            stops = api.find_nearby_stops(location.y, location.x, max_results=max)

            if not stops:
                print_error("No nearby stops found")
                return

            console.print(f"\n[bold]Found {len(stops)} nearby stop(s):[/bold]\n")

            for i, stop in enumerate(stops, 1):
                distance = stop.__dict__.get('distance', 'N/A')
                distance_str = f"{distance}m" if isinstance(distance, int) else distance

                console.print(f"  [cyan]{i}.[/cyan] {stop.name}")
                console.print(f"      [dim]Distance: {distance_str}[/dim]")
        else:
            print_error("Could not determine coordinates for this location")

    except Exception as e:
        print_error(str(e))
        raise click.Abort()


@cli.command(name="trip-from-address")
@click.argument("origin")
@click.argument("destination")
@click.option("--depart-at", help="Departure time (HH:MM)")
@click.option("--date", help="Date (DD.MM.YY)")
def trip_from_address(origin: str, destination: str, depart_at: str | None, date: str | None):
    """Plan a trip from one address to another.

    Automatically finds the nearest stops to both addresses and plans the trip.

    Examples:
        rejs trip-from-address "Vesterbrogade 4A, København" "Tivoli, Aarhus"
        rejs trip-from-address "DTU" "Nørreport" --depart-at "14:30"
    """
    try:
        api = RejseplanenAPI()

        # Search for origin address
        print_info(f"Searching for origin: {origin}")
        origin_locs = api.search_location(origin, include_addresses=True)

        if not origin_locs:
            print_error(f"Origin not found: {origin}")
            return

        origin_loc = origin_locs[0]

        # Find nearest stop to origin
        if origin_loc.type in ["adr", "poi"]:
            if origin_loc.x and origin_loc.y:
                print_info(f"Found address: {origin_loc.name}")
                print_info("Finding nearest stop to origin...")
                origin_stops = api.find_nearby_stops(origin_loc.y, origin_loc.x, max_results=1)

                if not origin_stops:
                    print_error("No stops found near origin")
                    return

                origin_stop = origin_stops[0]
                distance = origin_stop.__dict__.get('distance', 'N/A')
                console.print(f"[dim]→ Using: {origin_stop.name} ({distance}m away)[/dim]\n")
            else:
                print_error("Could not determine coordinates for origin")
                return
        else:
            origin_stop = origin_loc
            console.print(f"[dim]→ Using station: {origin_stop.name}[/dim]\n")

        # Search for destination address
        print_info(f"Searching for destination: {destination}")
        dest_locs = api.search_location(destination, include_addresses=True)

        if not dest_locs:
            print_error(f"Destination not found: {destination}")
            return

        dest_loc = dest_locs[0]

        # Find nearest stop to destination
        if dest_loc.type in ["adr", "poi"]:
            if dest_loc.x and dest_loc.y:
                print_info(f"Found address: {dest_loc.name}")
                print_info("Finding nearest stop to destination...")
                dest_stops = api.find_nearby_stops(dest_loc.y, dest_loc.x, max_results=1)

                if not dest_stops:
                    print_error("No stops found near destination")
                    return

                dest_stop = dest_stops[0]
                distance = dest_stop.__dict__.get('distance', 'N/A')
                console.print(f"[dim]→ Using: {dest_stop.name} ({distance}m away)[/dim]\n")
            else:
                print_error("Could not determine coordinates for destination")
                return
        else:
            dest_stop = dest_loc
            console.print(f"[dim]→ Using station: {dest_stop.name}[/dim]\n")

        # Parse time if provided
        departure_time = None
        if depart_at:
            try:
                departure_time = datetime.strptime(depart_at, "%H:%M")
                departure_time = departure_time.replace(
                    year=datetime.now().year,
                    month=datetime.now().month,
                    day=datetime.now().day
                )
            except ValueError:
                print_error("Invalid time format. Use HH:MM (e.g., 14:30)")
                return

        print_info(f"Planning trip from {origin_stop.name} to {dest_stop.name}")

        # Plan trip
        trips = api.plan_trip(origin_stop.id, dest_stop.id, departure_time)

        if not trips:
            print_error("No trips found")
            return

        # Display first 3 options
        for i, t in enumerate(trips[:3], 1):
            console.print(f"\n[bold cyan]Option {i}:[/bold cyan]")
            format_trip(t)

    except Exception as e:
        print_error(str(e))
        raise click.Abort()


@cli.command()
@click.argument("name")
@click.argument("origin")
@click.argument("destination")
def save(name: str, origin: str, destination: str):
    """Save a route for quick access.

    Examples:
        rejs save home-work "Nørreport" "DTU"
        rejs save gym "Frederiksberg" "Vanløse"
    """
    try:
        config = Config()
        config.save_route(name, origin, destination)
        print_success(f"Route '{name}' saved: {origin} → {destination}")
        print_info(f"Use it with: rejs {name}")

    except Exception as e:
        print_error(str(e))
        raise click.Abort()


@cli.command(name="list")
def list_routes():
    """List all saved routes."""
    try:
        config = Config()
        routes = config.get_saved_routes()

        if not routes:
            print_info("No saved routes. Create one with: rejs save <name> <origin> <dest>")
            return

        console.print("\n[bold]Saved Routes:[/bold]\n")
        for name, route in routes.items():
            console.print(f"  • [cyan]{name}[/cyan]: {route['origin']} → {route['destination']}")

    except Exception as e:
        print_error(str(e))
        raise click.Abort()


@cli.group()
def config():
    """Manage configuration."""
    pass


@config.command(name="set-api-key")
@click.argument("api_key")
def set_api_key(api_key: str):
    """Set your Rejseplanen API key.

    The key will be stored securely in your system keyring.

    Example:
        rejs config set-api-key YOUR_API_KEY_HERE
    """
    try:
        cfg = Config()
        cfg.set_api_key(api_key)
        print_success("API key saved securely")

    except Exception as e:
        print_error(str(e))
        raise click.Abort()


@config.command(name="show")
def show_config():
    """Show current configuration."""
    try:
        cfg = Config()

        console.print("\n[bold]Configuration:[/bold]\n")

        # Check if API key exists
        api_key = cfg.get_api_key()
        if api_key:
            masked = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
            console.print(f"  API Key: {masked}")
        else:
            console.print("  API Key: [red]Not set[/red]")
            console.print("  Set it with: rejs config set-api-key YOUR_KEY")

        console.print(f"\n  Config directory: {cfg.config_dir}")

    except Exception as e:
        print_error(str(e))
        raise click.Abort()


# Dynamic command routing for saved routes
@cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("route_name")
@click.pass_context
def route(ctx, route_name: str):
    """Quick access to saved routes.

    This is automatically called for any unknown command.
    """
    try:
        cfg = Config()
        routes = cfg.get_saved_routes()

        if route_name not in routes:
            print_error(f"Unknown route: {route_name}")
            print_info("Available routes:")
            for name in routes.keys():
                console.print(f"  • {name}")
            return

        route_info = routes[route_name]

        # Use trip-from-address to support both stations and addresses
        ctx.invoke(
            trip_from_address,
            origin=route_info["origin"],
            destination=route_info["destination"],
            depart_at=None,
            date=None
        )

    except Exception as e:
        print_error(str(e))
        raise click.Abort()


if __name__ == "__main__":
    cli()
