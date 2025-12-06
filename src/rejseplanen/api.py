"""Rejseplanen API client for API 2.0."""

from datetime import datetime

import requests

from .config import Config
from .models import Departure, Leg, Location, Trip


class RejseplanenAPI:
    """Client for Rejseplanen API 2.0."""

    # NEW API 2.0 BASE URL
    BASE_URL = "https://www.rejseplanen.dk/api"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or Config().get_api_key()
        if not self.api_key:
            raise ValueError(
                "API key not found. Set it with: rejs config set-api-key YOUR_KEY"
            )
        self.session = requests.Session()

    def _request(self, endpoint: str, params: dict) -> dict:
        """Make API request."""
        # API 2.0 requires format and authentication
        params["format"] = "json"

        # Add API key to parameters
        params["accessId"] = self.api_key

        url = f"{self.BASE_URL}/{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API request failed: {e}")

    def search_location(self, query: str, include_addresses: bool = False) -> list[Location]:
        """Search for locations/stations using location.name endpoint.

        Args:
            query: Search query (station name or address)
            include_addresses: If True, also returns addresses and POIs
        """
        params = {"input": query}

        # API 2.0 uses 'location.name' endpoint
        data = self._request("location.name", params)

        # Parse response - API 2.0 structure
        locations = []

        # API 2.0 uses 'stopLocationOrCoordLocation' array
        if "stopLocationOrCoordLocation" in data:
            location_items = data["stopLocationOrCoordLocation"]

            # Ensure it's a list
            if isinstance(location_items, dict):
                location_items = [location_items]

            for item in location_items:
                # Each item can have 'StopLocation' or 'CoordLocation'
                if "StopLocation" in item:
                    stop = item["StopLocation"]
                    # API 2.0 uses 'lon' and 'lat' instead of 'x' and 'y'
                    # Use 'id' field (complex string) or 'extId' as fallback
                    location_id = stop.get("id") or stop.get("extId", "")

                    locations.append(Location(
                        id=location_id,
                        name=stop.get("name", ""),
                        type="stop",
                        x=float(stop.get("lon", 0)) if stop.get("lon") is not None else None,
                        y=float(stop.get("lat", 0)) if stop.get("lat") is not None else None
                    ))
                elif "CoordLocation" in item and include_addresses:
                    coord = item["CoordLocation"]
                    loc_type = coord.get("type", "coord")  # ADR, POI, or coord

                    # Handle coordinate-based locations (addresses, POIs)
                    locations.append(Location(
                        id=coord.get("id", ""),
                        name=coord.get("name", ""),
                        type=loc_type.lower() if loc_type else "coord",
                        x=float(coord.get("lon", 0)) if coord.get("lon") is not None else None,
                        y=float(coord.get("lat", 0)) if coord.get("lat") is not None else None
                    ))

        return locations

    def find_nearby_stops(self, latitude: float, longitude: float, max_results: int = 10) -> list[Location]:
        """Find nearby stops given coordinates.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            max_results: Maximum number of results (default: 10)

        Returns:
            List of nearby stops sorted by distance
        """
        params = {
            "originCoordLat": str(latitude),
            "originCoordLong": str(longitude),
            "maxNo": str(max_results)
        }

        data = self._request("location.nearbystops", params)

        # Parse response - same structure as location.name
        stops = []

        if "stopLocationOrCoordLocation" in data:
            location_items = data["stopLocationOrCoordLocation"]

            # Ensure it's a list
            if isinstance(location_items, dict):
                location_items = [location_items]

            for item in location_items:
                if "StopLocation" in item:
                    stop = item["StopLocation"]
                    location_id = stop.get("id") or stop.get("extId", "")
                    distance = stop.get("dist")  # Distance in meters

                    location = Location(
                        id=location_id,
                        name=stop.get("name", ""),
                        type="stop",
                        x=float(stop.get("lon", 0)) if stop.get("lon") is not None else None,
                        y=float(stop.get("lat", 0)) if stop.get("lat") is not None else None
                    )

                    # Add distance as a temporary attribute (not in model)
                    # We'll use it for display
                    if distance is not None:
                        location.__dict__['distance'] = int(distance)

                    stops.append(location)

        return stops

    def get_departures(
        self,
        location_id: str,
        date: datetime | None = None
    ) -> list[Departure]:
        """Get departures from a location using departureBoard endpoint."""
        params = {"id": location_id}

        if date:
            params["date"] = date.strftime("%d.%m.%y")
            params["time"] = date.strftime("%H:%M")

        data = self._request("departureBoard", params)

        # Parse departures - API 2.0 has Departure directly at root
        departures = []

        # API 2.0 structure: Departure array at root level
        departure_list = data.get("Departure", [])

        # Ensure it's a list
        if isinstance(departure_list, dict):
            departure_list = [departure_list]

        for dep in departure_list:
            # API 2.0 uses ISO date format (2025-12-06) and HH:MM:SS time format
            date_str = dep.get("date", "")
            time_str = dep.get("time", "")

            # Skip if missing required fields (check for empty strings and None)
            if not date_str or not time_str:
                continue

            # Convert to string and strip whitespace
            date_str = str(date_str).strip()
            time_str = str(time_str).strip()

            if not date_str or not time_str:
                continue

            # Parse date - could be ISO format (2025-12-06) or DD.MM.YY format
            try:
                if "-" in date_str:
                    # ISO format: 2025-12-06
                    date_part = datetime.strptime(date_str, "%Y-%m-%d").date()
                else:
                    # Old format: 06.12.25
                    date_part = datetime.strptime(date_str, "%d.%m.%y").date()
            except ValueError:
                # Skip if date parsing fails
                continue

            # Parse time - could be HH:MM:SS or HH:MM
            try:
                time_parts = time_str.split(":")
                if len(time_parts) == 3:
                    # HH:MM:SS format
                    time_part = datetime.strptime(time_str, "%H:%M:%S").time()
                elif len(time_parts) == 2:
                    # HH:MM format
                    time_part = datetime.strptime(time_str, "%H:%M").time()
                else:
                    # Invalid time format, skip
                    continue
            except ValueError:
                # Skip if time parsing fails
                continue

            dep_time = datetime.combine(date_part, time_part)

            # Parse real-time if available
            rt_time = None
            if "rtTime" in dep and dep["rtTime"]:
                rt_date_str = dep.get("rtDate", date_str)
                rt_time_str = dep["rtTime"]

                if rt_date_str and rt_time_str:
                    try:
                        if "-" in rt_date_str:
                            rt_date_part = datetime.strptime(rt_date_str, "%Y-%m-%d").date()
                        else:
                            rt_date_part = datetime.strptime(rt_date_str, "%d.%m.%y").date()

                        rt_time_parts = rt_time_str.split(":")
                        if len(rt_time_parts) == 3:
                            rt_time_part = datetime.strptime(rt_time_str, "%H:%M:%S").time()
                        elif len(rt_time_parts) == 2:
                            rt_time_part = datetime.strptime(rt_time_str, "%H:%M").time()
                        else:
                            rt_time_part = None

                        if rt_time_part:
                            rt_time = datetime.combine(rt_date_part, rt_time_part)
                    except (ValueError, AttributeError):
                        # If real-time parsing fails, just use scheduled time
                        rt_time = None

            # Get track - prefer rtTrack (real-time) over track (scheduled)
            track = dep.get("rtTrack") or dep.get("track")
            # Track might be in platform object
            if not track:
                platform = dep.get("platform") or dep.get("rtPlatform")
                if platform and isinstance(platform, dict):
                    track = platform.get("text")

            departures.append(Departure(
                name=dep.get("name", ""),
                type=dep.get("type", ""),
                stop=dep.get("stop", ""),
                time=dep_time,
                date=date_str,
                direction=dep.get("direction"),
                track=track,
                rtTime=rt_time,
                rtDate=dep.get("rtDate")
            ))

        # Sort departures by time (earliest first)
        departures.sort(key=lambda d: d.time)

        return departures

    def plan_trip(
        self,
        origin_id: str,
        dest_id: str,
        departure_time: datetime | None = None
    ) -> list[Trip]:
        """Plan a trip between two locations using trip endpoint."""
        params = {
            "originId": origin_id,
            "destId": dest_id
        }

        if departure_time:
            params["date"] = departure_time.strftime("%d.%m.%y")
            params["time"] = departure_time.strftime("%H:%M")

        data = self._request("trip", params)

        # Parse trips - API 2.0 structure
        trips = []
        trip_list = data.get("Trip", [])

        # Ensure it's a list
        if isinstance(trip_list, dict):
            trip_list = [trip_list]

        for trip_data in trip_list:
            try:
                # Parse legs
                legs = []
                leg_list_data = trip_data.get("LegList", {})
                leg_data = leg_list_data.get("Leg", [])

                # Ensure it's a list
                if isinstance(leg_data, dict):
                    leg_data = [leg_data]

                for leg in leg_data:
                    # Parse origin
                    origin_data = leg.get("Origin", {})
                    origin = Location(
                        id=origin_data.get("id", ""),
                        name=origin_data.get("name", ""),
                        type=origin_data.get("type", ""),
                        x=float(origin_data.get("lon", 0)),
                        y=float(origin_data.get("lat", 0))
                    )

                    # Parse destination
                    dest_data = leg.get("Destination", {})
                    destination = Location(
                        id=dest_data.get("id", ""),
                        name=dest_data.get("name", ""),
                        type=dest_data.get("type", ""),
                        x=float(dest_data.get("lon", 0)),
                        y=float(dest_data.get("lat", 0))
                    )

                    # Parse times
                    origin_date = origin_data.get("date", "")
                    origin_time = origin_data.get("time", "")
                    dest_date = dest_data.get("date", "")
                    dest_time = dest_data.get("time", "")

                    # Parse departure time
                    if "-" in origin_date:
                        dep_date = datetime.strptime(origin_date, "%Y-%m-%d").date()
                    else:
                        dep_date = datetime.strptime(origin_date, "%d.%m.%y").date()

                    time_parts = origin_time.split(":")
                    if len(time_parts) == 3:
                        dep_time = datetime.strptime(origin_time, "%H:%M:%S").time()
                    else:
                        dep_time = datetime.strptime(origin_time, "%H:%M").time()

                    departure_dt = datetime.combine(dep_date, dep_time)

                    # Parse arrival time
                    if "-" in dest_date:
                        arr_date = datetime.strptime(dest_date, "%Y-%m-%d").date()
                    else:
                        arr_date = datetime.strptime(dest_date, "%d.%m.%y").date()

                    time_parts = dest_time.split(":")
                    if len(time_parts) == 3:
                        arr_time = datetime.strptime(dest_time, "%H:%M:%S").time()
                    else:
                        arr_time = datetime.strptime(dest_time, "%H:%M").time()

                    arrival_dt = datetime.combine(arr_date, arr_time)

                    # Calculate duration in minutes
                    duration_minutes = int((arrival_dt - departure_dt).total_seconds() / 60)

                    # Get transport name (e.g., "A", "Metro M1", "Bus 5C")
                    transport_name = leg.get("name", "")
                    transport_type = leg.get("category", leg.get("type", ""))

                    legs.append(Leg(
                        name=transport_name,
                        type=transport_type,
                        origin=origin,
                        destination=destination,
                        departure_time=departure_dt,
                        arrival_time=arrival_dt,
                        duration=duration_minutes
                    ))

                # Get overall trip times from first and last leg
                if legs:
                    trip_departure = legs[0].departure_time
                    trip_arrival = legs[-1].arrival_time
                    trip_duration = int((trip_arrival - trip_departure).total_seconds() / 60)

                    # Extract price information from TariffResult
                    price = None
                    currency = "DKK"
                    fare_type = None

                    tariff_result = trip_data.get("TariffResult", {})
                    if tariff_result:
                        fare_set_items = tariff_result.get("fareSetItem", [])
                        if isinstance(fare_set_items, dict):
                            fare_set_items = [fare_set_items]

                        # Get first adult fare (passenger type 'A')
                        for fare_set in fare_set_items:
                            fare_items = fare_set.get("fareItem", [])
                            if isinstance(fare_items, dict):
                                fare_items = [fare_items]

                            for fare_item in fare_items:
                                # Check if this is an adult fare
                                params = fare_item.get("param", [])
                                is_adult = any(p.get("name") == "psg" and p.get("value") == "A" for p in params)

                                if is_adult:
                                    # Price is in øre/cents, convert to DKK
                                    price_ore = fare_item.get("price")
                                    if price_ore:
                                        price = price_ore / 100.0

                                    currency = fare_item.get("cur", "DKK")

                                    # Get fare type from params
                                    for param in params:
                                        if param.get("name") == "prod_name":
                                            fare_type = param.get("value")
                                            break

                                    break
                            if price is not None:
                                break

                    trips.append(Trip(
                        legs=legs,
                        departure_time=trip_departure,
                        arrival_time=trip_arrival,
                        duration=trip_duration,
                        price=price,
                        currency=currency,
                        fare_type=fare_type
                    ))

            except (ValueError, KeyError, TypeError):
                # Skip trips that fail to parse
                continue

        return trips
