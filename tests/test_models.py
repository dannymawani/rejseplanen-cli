"""Tests for data models."""

from datetime import datetime

from rejseplanen.models import Departure, Leg, Location, Trip


def test_location_model():
    """Test Location model."""
    loc = Location(
        id="test_id",
        name="Test Station",
        type="stop",
        x=12.5,
        y=55.6
    )
    assert loc.id == "test_id"
    assert loc.name == "Test Station"
    assert loc.type == "stop"
    assert loc.x == 12.5
    assert loc.y == 55.6


def test_location_without_coordinates():
    """Test Location model without coordinates."""
    loc = Location(
        id="test_id",
        name="Test Station",
        type="stop"
    )
    assert loc.x is None
    assert loc.y is None


def test_departure_not_delayed():
    """Test departure without delay."""
    dep = Departure(
        name="M1",
        type="M",
        stop="Nørreport",
        time=datetime(2024, 12, 5, 10, 30),
        date="05.12.24"
    )
    assert not dep.is_delayed
    assert dep.delay_minutes == 0


def test_departure_delayed():
    """Test departure with delay."""
    dep = Departure(
        name="M1",
        type="M",
        stop="Nørreport",
        time=datetime(2024, 12, 5, 10, 30),
        date="05.12.24",
        rtTime=datetime(2024, 12, 5, 10, 35)
    )
    assert dep.is_delayed
    assert dep.delay_minutes == 5


def test_leg_model():
    """Test Leg model."""
    origin = Location(id="1", name="Start", type="stop", x=12.5, y=55.6)
    dest = Location(id="2", name="End", type="stop", x=12.6, y=55.7)

    leg = Leg(
        name="A",
        type="train",
        origin=origin,
        destination=dest,
        departure_time=datetime(2024, 12, 5, 10, 0),
        arrival_time=datetime(2024, 12, 5, 10, 30),
        duration=30
    )

    assert leg.name == "A"
    assert leg.type == "train"
    assert leg.duration == 30
    assert leg.origin.name == "Start"
    assert leg.destination.name == "End"


def test_trip_without_price():
    """Test Trip model without price."""
    origin = Location(id="1", name="Start", type="stop", x=12.5, y=55.6)
    dest = Location(id="2", name="End", type="stop", x=12.6, y=55.7)

    leg = Leg(
        name="A",
        type="train",
        origin=origin,
        destination=dest,
        departure_time=datetime(2024, 12, 5, 10, 0),
        arrival_time=datetime(2024, 12, 5, 10, 30),
        duration=30
    )

    trip = Trip(
        legs=[leg],
        departure_time=datetime(2024, 12, 5, 10, 0),
        arrival_time=datetime(2024, 12, 5, 10, 30),
        duration=30
    )

    assert len(trip.legs) == 1
    assert trip.num_changes == 0
    assert trip.price is None
    assert trip.currency == "DKK"


def test_trip_with_price():
    """Test Trip model with price."""
    origin = Location(id="1", name="Start", type="stop", x=12.5, y=55.6)
    dest = Location(id="2", name="End", type="stop", x=12.6, y=55.7)

    leg = Leg(
        name="A",
        type="train",
        origin=origin,
        destination=dest,
        departure_time=datetime(2024, 12, 5, 10, 0),
        arrival_time=datetime(2024, 12, 5, 10, 30),
        duration=30
    )

    trip = Trip(
        legs=[leg],
        departure_time=datetime(2024, 12, 5, 10, 0),
        arrival_time=datetime(2024, 12, 5, 10, 30),
        duration=30,
        price=24.50,
        currency="DKK",
        fare_type="EasyTrip"
    )

    assert trip.price == 24.50
    assert trip.currency == "DKK"
    assert trip.fare_type == "EasyTrip"


def test_trip_num_changes():
    """Test Trip num_changes calculation."""
    origin = Location(id="1", name="Start", type="stop", x=12.5, y=55.6)
    middle = Location(id="2", name="Middle", type="stop", x=12.55, y=55.65)
    dest = Location(id="3", name="End", type="stop", x=12.6, y=55.7)

    leg1 = Leg(
        name="A",
        type="train",
        origin=origin,
        destination=middle,
        departure_time=datetime(2024, 12, 5, 10, 0),
        arrival_time=datetime(2024, 12, 5, 10, 15),
        duration=15
    )

    leg2 = Leg(
        name="B",
        type="train",
        origin=middle,
        destination=dest,
        departure_time=datetime(2024, 12, 5, 10, 20),
        arrival_time=datetime(2024, 12, 5, 10, 40),
        duration=20
    )

    trip = Trip(
        legs=[leg1, leg2],
        departure_time=datetime(2024, 12, 5, 10, 0),
        arrival_time=datetime(2024, 12, 5, 10, 40),
        duration=40
    )

    assert trip.num_changes == 1  # 2 legs = 1 change
