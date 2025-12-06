"""Tests for formatter module."""

from datetime import datetime
from io import StringIO
from unittest.mock import patch

from rejseplanen.formatter import (
    format_departures,
    format_trip,
    print_error,
    print_info,
    print_success,
)
from rejseplanen.models import Leg, Location, Trip


def test_format_departures_empty():
    """Test formatting empty departures list."""
    with patch('sys.stdout', new=StringIO()):
        format_departures([], "Test Station")
        # Should handle empty list


def test_format_departures_with_data(sample_departures):
    """Test formatting departures with data."""
    with patch('sys.stdout', new=StringIO()):
        format_departures(sample_departures, "Test Station")
        # Should not raise any errors


def test_format_trip_without_price():
    """Test formatting trip without price."""
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

    with patch('sys.stdout', new=StringIO()):
        format_trip(trip)
        # Should not raise any errors


def test_format_trip_with_price():
    """Test formatting trip with price."""
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

    with patch('sys.stdout', new=StringIO()):
        format_trip(trip)
        # Should display price information


def test_format_trip_multiple_legs():
    """Test formatting trip with multiple legs."""
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
        duration=40,
        price=35.00
    )

    with patch('sys.stdout', new=StringIO()):
        format_trip(trip)
        # Should display all legs


def test_print_error():
    """Test error message printing."""
    with patch('sys.stdout', new=StringIO()):
        print_error("Test error")
        # Should not raise any errors


def test_print_success():
    """Test success message printing."""
    with patch('sys.stdout', new=StringIO()):
        print_success("Test success")
        # Should not raise any errors


def test_print_info():
    """Test info message printing."""
    with patch('sys.stdout', new=StringIO()):
        print_info("Test info")
        # Should not raise any errors

