"""Data models for Rejseplanen API responses."""

from datetime import datetime

from pydantic import BaseModel


class Location(BaseModel):
    """Represents a location/station."""
    id: str
    name: str
    type: str
    x: float | None = None  # Longitude
    y: float | None = None  # Latitude


class Departure(BaseModel):
    """Represents a departure."""
    name: str  # Line name (e.g., "Bus 5A")
    type: str  # Transport type
    stop: str  # Stop name
    time: datetime
    date: str
    direction: str | None = None
    track: str | None = None
    rtTime: datetime | None = None  # Real-time adjusted time
    rtDate: str | None = None

    @property
    def is_delayed(self) -> bool:
        """Check if departure is delayed."""
        return self.rtTime is not None and self.rtTime > self.time

    @property
    def delay_minutes(self) -> int:
        """Get delay in minutes."""
        if not self.is_delayed or self.rtTime is None:
            return 0
        return int((self.rtTime - self.time).total_seconds() / 60)


class Leg(BaseModel):
    """Represents one leg of a journey."""
    name: str
    type: str
    origin: Location
    destination: Location
    departure_time: datetime
    arrival_time: datetime
    duration: int  # minutes


class Trip(BaseModel):
    """Represents a complete journey."""
    legs: list[Leg]
    departure_time: datetime
    arrival_time: datetime
    duration: int  # minutes
    price: float | None = None  # Price in DKK (converted from øre)
    currency: str | None = "DKK"
    fare_type: str | None = None  # e.g., "Rejsekort", "EasyTrip"

    @property
    def num_changes(self) -> int:
        """Number of changes required."""
        return max(0, len(self.legs) - 1)
