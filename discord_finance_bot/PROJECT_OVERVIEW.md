# Discord Finance Bot - Project Overview

## Project Structure

```
discord_finance_bot/
├── controllers/              # Request handlers and business logic
│   ├── bot_controller.py     # Discord bot controller
│   └── scheduler_controller.py # Scheduled task controller
│
├── repositories/             # Data access layer
│   ├── alphavantage_repo.py  # Alpha Vantage API client
│   ├── polymarket_repo.py    # Polymarket scraping repository
│   └── web_crawler_repo.py   # Web scraping repository
│
├── services/                 # Business logic layer
│   ├── alphavantage_service.py
│   ├── message_service.py    # Message generation service
│   └── web_crawler_service.py
│
├── utils/                    # Utility functions
│   ├── data_parser.py
│   ├── logger.py
│   └── scheduler_utils.py
│
├── tests/                    # Test suite
│   ├── conftest.py           # Test configuration and fixtures
│   ├── test_*.py             # Test files
│   └── README.md
│
├── config.py                 # Configuration management
├── main.py                   # Entry point
├── TESTING.md                # Testing guide
├── demo_tests.py             # Test demonstration script
└── run_tests.sh              # Test runner script
```

## Architecture Pattern

The project follows a **Layered Architecture** with Repository-Service-Controller pattern:

```
Controller (Scheduler/Bot)
    ↓
Service (Business Logic)
    ↓
Repository (Data Access)
    ↓
External APIs (Alpha Vantage, Polymarket, Moomoo)
```

### Component Responsibilities

#### Controllers
- **bot_controller.py**: Handles Discord events and commands
- **scheduler_controller.py**: Manages scheduled tasks and message formatting

#### Repositories
- **alphavantage_repo.py**: Fetches earnings and IPO data from Alpha Vantage API
- **polymarket_repo.py**: Scrapes earnings predictions from Polymarket
- **web_crawler_repo.py**: Scrapes sector data from Moomoo

#### Services
- **alphavantage_service.py**: Business logic for Alpha Vantage data
- **web_crawler_service.py**: Orchestrates web scraping operations
- **message_service.py**: Generates daily summary messages and JSON payloads

#### Utils
- **logger.py**: Logging configuration
- **data_parser.py**: Data transformation utilities
- **scheduler_utils.py**: Scheduler-specific utilities

## Data Flow

### Daily Summary Generation

1. **Scheduler triggers** at 9:00 AM daily
2. **MessageService.generate_daily_summary_json_async()** is called
3. **WebCrawlerService** fetches:
   - Sector data from Moomoo (via API interception)
   - Polymarket earnings predictions (via Playwright scraping)
4. **AlphaVantageService** fetches:
   - Upcoming earnings
   - Upcoming IPOs
5. **MessageService** combines all data into standardized format
6. **SchedulerController** formats data into Discord embed
7. **BotController** sends embed to Discord channel

### Polymarket Scraping Flow

1. **Scheduler** calls MessageService
2. **MessageService** calls WebCrawlerService
3. **WebCrawlerService** calls PolymarketRepo
4. **PolymarketRepo**:
   - Launches Playwright browser (headless)
   - Navigates to https://polymarket.com/earnings
   - Waits for "Earnings Calendar" to load
   - Locates active date columns (opacity-100)
   - Extracts earnings predictions from cards
   - Returns structured data
5. Data flows back through service layers to Discord

## Key Features

### 1. Polymarket Earnings Predictions
- Scrapes market predictions from Polymarket
- Extracts EPS forecasts and probability data
- Displays in Discord embed with 🎯 emoji

### 2. Alpha Vantage Integration
- Fetches official earnings calendar
- Retrieves upcoming IPO information
- Provides structured financial data

### 3. Sector Analysis
- Scrapes top-performing sectors from Moomoo
- Captures API responses for accurate data
- Displays sector performance metrics

### 4. Automated Scheduling
- Daily execution at 9:00 AM
- APScheduler for robust scheduling
- Error handling and logging

### 5. Comprehensive Testing
- Unit tests for all components
- Integration tests for service interactions
- Health checks for service availability
- Mock-based testing (no external dependencies)

## Testing Strategy

### Test Categories

1. **Unit Tests**
   - Test individual components in isolation
   - Mock all external dependencies
   - Fast execution (< 100ms per test)

2. **Integration Tests**
   - Test component interactions
   - Verify data flow through layers
   - Ensure proper error handling

3. **Health Checks**
   - Verify service initialization
   - Check dependency injection
   - Validate configuration

### Running Tests

```bash
# All tests
./run_tests.sh

# With coverage
pytest tests/ --cov=. --cov-report=html

# Specific test
pytest tests/test_polymarket_repo.py -v
```

See **TESTING.md** for detailed testing documentation.

## Dependencies

### Runtime Dependencies
- `discord.py` - Discord API wrapper
- `asyncio` - Async framework
- `playwright` - Web scraping
- `apscheduler` - Task scheduling
- `requests` - HTTP client
- `python-dotenv` - Environment configuration

### Development Dependencies
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities

## Configuration

Configuration is managed through environment variables:

```bash
DISCORD_TOKEN=your_bot_token
DISCORD_CHANNEL_ID=123456789
SELECTED_STOCKS=AAPL,MSFT,GOOGL
TIMEZONE=Asia/Shanghai
ALPHAVANTAGE_API_KEY=your_api_key
```

See `config.py` for full configuration details.

## Error Handling

The project implements comprehensive error handling:

1. **Repository Layer**: Catches and logs scraping/API errors
2. **Service Layer**: Handles data transformation errors
3. **Controller Layer**: Manages user-facing error messages
4. **Scheduler**: Logs errors without stopping the bot

## Logging

All operations are logged using the custom logger:
- **INFO**: Normal operations
- **WARNING**: Recoverable errors
- **ERROR**: Failed operations
- **DEBUG**: Detailed information (development only)

## Extending the Project

### Adding a New Data Source

1. Create a new repository in `repositories/`
2. Create a corresponding service in `services/`
3. Add the service to `MessageService`
4. Update the embed builder in `scheduler_controller.py`
5. Write tests for the new components

### Adding New Tests

1. Create test file in `tests/`
2. Use existing fixtures from `conftest.py`
3. Mock external dependencies
4. Follow naming convention: `test_<component>.py`

### Modifying the Schedule

Edit `scheduler_controller.py`:
```python
# Change schedule
self.scheduler.add_job(
    lambda: asyncio.create_task(self.daily_update()),
    "cron",
    hour=10,  # Changed from 9 to 10
    minute=30  # Added minutes
)
```

## Performance Considerations

1. **Playwright**: Runs in headless mode for faster execution
2. **Async Operations**: All I/O operations are asynchronous
3. **Caching**: Consider adding caching for frequently accessed data
4. **Rate Limiting**: Alpha Vantage has rate limits (5 requests/minute for free tier)

## Security Best Practices

1. **API Keys**: Stored in environment variables, never in code
2. **Web Scraping**: Respects robots.txt and rate limits
3. **Error Messages**: Sanitized to avoid exposing sensitive data
4. **Logging**: No sensitive information logged

## Monitoring

Monitor the following metrics:
- Bot uptime and responsiveness
- Successful/failed scheduled runs
- API rate limit usage
- Scraping success rate
- Error frequency and types

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**
   - Ensure correct Python environment
   - Install dependencies: `pip install -r requirements.txt`

2. **Playwright errors**
   - Install browser: `python -m playwright install chromium`

3. **Discord connection issues**
   - Verify bot token is correct
   - Check bot permissions in Discord server

4. **No data scraped**
   - Check if target website structure changed
   - Verify selectors in repository code

## Contributing

When contributing to the project:

1. Follow the existing architecture pattern
2. Write tests for new features
3. Update documentation
4. Use type hints
5. Follow PEP 8 style guide
6. Add logging for new operations

## License

This project is for educational and personal use only.
