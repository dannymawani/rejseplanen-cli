# Rejseplanen CLI

Modern command-line tool for Danish public transport using Rejseplanen API 2.0.

## Features

- 🚇 **Departure boards** - Live departures from any station with real-time updates
- 🗺️ **Journey planning** - Find the best routes between stations
- 📍 **Address support** - Plan trips directly from addresses or POIs
- 💰 **Price information** - See ticket prices for each journey
- 🚏 **Nearby stops** - Find the closest bus/train stops to any address
- 💾 **Saved routes** - Quick access to frequent journeys
- 🎨 **Beautiful output** - Rich terminal formatting with colors
- 🔒 **Secure** - API keys stored safely in system keyring
- ⚡ **Fast** - Built with modern Python tools

## Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer

### Setup

```bash
# Clone the repository
git clone https://github.com/andreadiluca/rejseplanen-cli.git
cd rejseplanen-cli

# Install uv (fast package installer)
pip install uv

# Create and activate virtual environment
# Option 1: Using conda
conda create -n rejseplanen python=3.12
conda activate rejseplanen

# Option 2: Using venv
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
make install-dev

# Set your API key (choose one method)
# Option 1: Using the CLI command
rejs config set-api-key YOUR_API_KEY

# Option 2: Using .env file
# Create a .env file in the project root:
echo "REJSEPLANEN_API_KEY=your_api_key_here" > .env
```

### Getting an API Key

1. Visit [Rejseplanen Labs](https://labs.rejseplanen.dk)
2. Register for API access
3. Copy your API key
4. Set it using either method:
   - CLI: `rejs config set-api-key YOUR_KEY`
   - Environment file: Add `REJSEPLANEN_API_KEY=YOUR_KEY` to a `.env` file in the project root

## Usage

### Basic Commands

```bash
# Show departures from a station
rejs departures "Nørreport"
rejs departures "København H" --limit 10

# Filter by specific lines
rejs departures "Nørreport" --lines "M1,M2"

# Search for stations
rejs search "Nørreport"
rejs search "København"

# Plan a trip between stations
rejs trip "Nørreport" "Aarhus"
rejs trip "København H" "Roskilde" --depart-at "14:30"

# Plan a trip from address to address
rejs trip-from-address "Vesterbrogade 4A, København" "Aarhus H"
rejs trip-from-address "Nørreport" "DTU"

# Find nearby stops to an address
rejs nearby "Vesterbrogade 4A, København"
rejs nearby "Tivoli" --max 5
```

### Saved Routes

```bash
# Save a frequent route (works with stations or addresses)
rejs save home-work "Nørreport" "DTU"
rejs save gym "Frederiksberg" "Vanløse"

# List saved routes
rejs list

# Use a saved route (quick access)
rejs route home-work
rejs route gym
```

### Configuration

```bash
# Show configuration
rejs config show

# Set API key
rejs config set-api-key YOUR_KEY
```

## Development

### Setup Development Environment

```bash
make setup              # Create virtual environment
make install-dev        # Install with dev dependencies
```

### Common Commands

```bash
make test              # Run all tests
make lint              # Run linter (ruff)
make format            # Format code (black + ruff)
make type-check        # Type checking (mypy)
make check             # Run all checks (lint + type-check + test)
make clean             # Clean build artifacts
make build             # Build package distribution
```

### Run Locally

```bash
make run ARGS="departures Nørreport"
make run ARGS="trip 'Nørreport' 'Aarhus'"
make run ARGS="nearby 'Vesterbrogade 4A'"
```

### Testing

The project includes comprehensive test coverage (40+ tests):

```bash
# Run all tests
make test

# Run tests with verbose output
PYTHONPATH=src python -m pytest -v
```

## Project Structure

```
rejseplanen-cli/
├── src/
│   └── rejseplanen/
│       ├── __init__.py      # Package initialization
│       ├── cli.py           # CLI commands
│       ├── api.py           # Rejseplanen API client
│       ├── models.py        # Data models (Pydantic)
│       ├── config.py        # Configuration management
│       └── formatter.py     # Output formatting (Rich)
├── tests/                   # Test suite
├── pyproject.toml           # Project configuration
├── Makefile                 # Development commands
└── README.md
```

## Examples

### Morning Commute Check

```bash
# Quick check of your morning commute
rejs departures "Nørreport" --lines "M1,M2" --limit 5
```

### Weekend Trip Planning

```bash
# Plan a trip to Aarhus
rejs trip "København H" "Aarhus"

# Plan with specific departure time
rejs trip "København H" "Aarhus" --depart-at "10:00"
```

### Save and Reuse Routes

```bash
# Save your commute (works with addresses too!)
rejs save commute "Nørreport" "DTU"

# Check it anytime with just:
rejs route commute
```

### Address-Based Planning

```bash
# Find nearest stops to your home
rejs nearby "Vesterbrogade 4A, København" --max 5

# Plan trip from address to address
rejs trip-from-address "Vesterbrogade 4A" "Tivoli, Aarhus"
```

## Troubleshooting

### API Key Issues

```bash
# Check if API key is set
rejs config show

# Reset API key
rejs config set-api-key NEW_KEY
```

### Station Not Found

Try being more specific or use the search command:

```bash
rejs search "København"
# Shows all matches, use the exact name
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests and linting (`make check`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request


## Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for CLI
- Terminal UI powered by [Rich](https://rich.readthedocs.io/)
- Data validation with [Pydantic](https://pydantic-docs.helpmanual.io/)
- Uses [Rejseplanen API 2.0](https://labs.rejseplanen.dk/)

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/andreadiluca/rejseplanen-cli/issues) page
2. Create a new issue with details
3. Feel free to contact me 😊
