"""Pytest configuration and fixtures."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from rejseplanen.api import RejseplanenAPI
from rejseplanen.models import Departure, Location


@pytest.fixture
def mock_api():
    """Mock API client."""
    api = Mock(spec=RejseplanenAPI)
    return api


@pytest.fixture
def sample_location():
    """Sample location for testing."""
    return Location(
        id="008600626",
        name="Nørreport St. (Metro)",
        type="stop",
        x=12.571389,
        y=55.683611
    )


@pytest.fixture
def sample_locations():
    """Sample list of locations."""
    return [
        Location(
            id="008600626",
            name="Nørreport St. (Metro)",
            type="stop",
            x=12.571389,
            y=55.683611
        ),
        Location(
            id="008600625",
            name="Nørreport St. (S-tog)",
            type="stop",
            x=12.571389,
            y=55.683611
        )
    ]


@pytest.fixture
def sample_departure():
    """Sample departure for testing."""
    return Departure(
        name="M1",
        type="M",
        stop="Nørreport St.",
        time=datetime(2024, 12, 5, 10, 30),
        date="05.12.24",
        direction="Vestamager",
        track="2"
    )


@pytest.fixture
def sample_departures():
    """Sample list of departures."""
    return [
        Departure(
            name="M1",
            type="M",
            stop="Nørreport St.",
            time=datetime(2024, 12, 5, 10, 30),
            date="05.12.24",
            direction="Vestamager",
            track="2"
        ),
        Departure(
            name="M2",
            type="M",
            stop="Nørreport St.",
            time=datetime(2024, 12, 5, 10, 32),
            date="05.12.24",
            direction="Lufthavnen",
            track="1"
        ),
        Departure(
            name="Bus 5A",
            type="BUS",
            stop="Nørreport St.",
            time=datetime(2024, 12, 5, 10, 35),
            date="05.12.24",
            direction="Husum Torv",
            track=None
        )
    ]


@pytest.fixture
def delayed_departure():
    """Sample delayed departure."""
    return Departure(
        name="M1",
        type="M",
        stop="Nørreport St.",
        time=datetime(2024, 12, 5, 10, 30),
        date="05.12.24",
        direction="Vestamager",
        track="2",
        rtTime=datetime(2024, 12, 5, 10, 35),  # 5 min delay
        rtDate="05.12.24"
    )
