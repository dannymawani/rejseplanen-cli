"""Tests for CLI commands."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from rejseplanen.cli import cli
from rejseplanen.models import Leg, Location, Trip


@pytest.fixture
def runner():
    """CLI test runner."""
    return CliRunner()


def test_cli_help(runner):
    """Test CLI help output."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Rejseplanen CLI" in result.output


def test_config_show(runner):
    """Test config show command."""
    with patch('rejseplanen.cli.Config') as mock_config:
        mock_instance = Mock()
        mock_instance.get_api_key.return_value = None
        mock_instance.config_dir = "/test/path"
        mock_config.return_value = mock_instance

        result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0
        assert "Configuration" in result.output


def test_search_command(runner, sample_locations):
    """Test search command."""
    with patch('rejseplanen.cli.RejseplanenAPI') as mock_api_class:
        mock_api = Mock()
        mock_api.search_location.return_value = sample_locations
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ["search", "Nørreport"])
        assert result.exit_code == 0
        assert "Nørreport St." in result.output


def test_departures_command(runner, sample_locations, sample_departures):
    """Test departures command."""
    with patch('rejseplanen.cli.RejseplanenAPI') as mock_api_class:
        mock_api = Mock()
        mock_api.search_location.return_value = sample_locations
        mock_api.get_departures.return_value = sample_departures
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ["departures", "Nørreport"])
        assert result.exit_code == 0
        assert "Departures" in result.output


def test_trip_command(runner, sample_locations):
    """Test trip command."""
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
        price=24.50
    )

    with patch('rejseplanen.cli.RejseplanenAPI') as mock_api_class:
        mock_api = Mock()
        mock_api.search_location.return_value = [sample_locations[0]]
        mock_api.plan_trip.return_value = [trip]
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ["trip", "Start", "End"])
        assert result.exit_code == 0
        assert "Journey" in result.output


def test_nearby_command(runner):
    """Test nearby command."""
    address = Location(id="1", name="Test Address", type="adr", x=12.5, y=55.6)
    stop = Location(id="2", name="Nearby Stop", type="stop", x=12.5, y=55.6)
    stop.__dict__['distance'] = 100

    with patch('rejseplanen.cli.RejseplanenAPI') as mock_api_class:
        mock_api = Mock()
        mock_api.search_location.return_value = [address]
        mock_api.find_nearby_stops.return_value = [stop]
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ["nearby", "Test Address"])
        assert result.exit_code == 0
        assert "nearby stop" in result.output.lower()


def test_trip_from_address_command(runner):
    """Test trip-from-address command."""
    address = Location(id="1", name="Test Address", type="adr", x=12.5, y=55.6)
    stop = Location(id="2", name="Nearby Stop", type="stop", x=12.5, y=55.6)
    stop.__dict__['distance'] = 100

    leg = Leg(
        name="A",
        type="train",
        origin=stop,
        destination=stop,
        departure_time=datetime(2024, 12, 5, 10, 0),
        arrival_time=datetime(2024, 12, 5, 10, 30),
        duration=30
    )

    trip = Trip(
        legs=[leg],
        departure_time=datetime(2024, 12, 5, 10, 0),
        arrival_time=datetime(2024, 12, 5, 10, 30),
        duration=30,
        price=24.50
    )

    with patch('rejseplanen.cli.RejseplanenAPI') as mock_api_class:
        mock_api = Mock()
        mock_api.search_location.return_value = [address]
        mock_api.find_nearby_stops.return_value = [stop]
        mock_api.plan_trip.return_value = [trip]
        mock_api_class.return_value = mock_api

        result = runner.invoke(cli, ["trip-from-address", "Address1", "Address2"])
        assert result.exit_code == 0
        assert "Journey" in result.output


def test_save_route_command(runner):
    """Test save route command."""
    with patch('rejseplanen.cli.Config') as mock_config:
        mock_instance = Mock()
        mock_config.return_value = mock_instance

        result = runner.invoke(cli, ["save", "test-route", "Start", "End"])
        assert result.exit_code == 0
        mock_instance.save_route.assert_called_once()


def test_list_routes_command(runner):
    """Test list routes command."""
    with patch('rejseplanen.cli.Config') as mock_config:
        mock_instance = Mock()
        mock_instance.get_saved_routes.return_value = {
            "home-work": {"origin": "Home", "destination": "Work"}
        }
        mock_config.return_value = mock_instance

        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "home-work" in result.output


def test_route_command(runner):
    """Test route command with saved route."""
    address = Location(id="1", name="Test", type="stop", x=12.5, y=55.6)

    leg = Leg(
        name="A",
        type="train",
        origin=address,
        destination=address,
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

    with patch('rejseplanen.cli.Config') as mock_config:
        mock_instance = Mock()
        mock_instance.get_saved_routes.return_value = {
            "test": {"origin": "Start", "destination": "End"}
        }
        mock_config.return_value = mock_instance

        with patch('rejseplanen.cli.RejseplanenAPI') as mock_api_class:
            mock_api = Mock()
            mock_api.search_location.return_value = [address]
            mock_api.find_nearby_stops.return_value = [address]
            mock_api.plan_trip.return_value = [trip]
            mock_api_class.return_value = mock_api

            result = runner.invoke(cli, ["route", "test"])
            assert result.exit_code == 0
