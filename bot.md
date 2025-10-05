# Bot Development and File Management Guide

A practical guide for future contributors to keep the codebase clean, maintainable, and easy to extend.

## Goals and Scope
- Standardize layered responsibilities: Controller, Service, Repository, Utils, Config, Tests.
- Normalize file/module naming, imports, and execution.
- Explain how to add new data sources and integrate them into daily messages and scheduled pushes.

## Project Structure
- `discord_finance_bot/`
  - `config.py`: Loads configuration and environment variables (supports `.env`).
  - `controllers/`:
    - `bot_controller.py`: Discord events and command handling.
    - `scheduler_controller.py`: APScheduler jobs; calls `MessageService` to generate and send content.
  - `services/`: Thin orchestration layer. Compose and forward calls to Repositories.
    - `finance_service.py`, `stock_service.py`, `sector_service.py`, `alphavantage_service.py`.
  - `repositories/`: Heavy data-access layer. Encapsulates external API/crawling and parsing.
    - `yahoo_repo.py`, `web_crawler_repo.py`, `alphavantage_repo.py`.
  - `utils/`: Shared helpers, such as `logger.py`, `data_parser.py`, `scheduler_utils.py`.
  - `tests/`: Unit and integration tests.
  - `requirements.txt`: Dependencies.

## Layered Responsibilities
- Controller: Coordination only (scheduling, event handling). No business logic or data fetching.
- Service (thin):
  - Compose/forward calls, aggregate data from repositories, prepare outputs for upper layers (e.g., `MessageService`).
  - Do not directly access external APIs; always go through repositories.
- Repository (heavy):
  - External API integration (requests, parsing, error handling, field filtering).
  - Perform necessary data transformations (types, dates, normalized field names).
- Utils: Common utilities (logging, formatting, timezone).
- Config: Centralized configuration and environment variables.

## Naming and File Management
- Directories and filenames use snake_case, e.g., `alphavantage_repo.py`.
- Class names use PascalCase, e.g., `AlphaVantageRepo`, `MessageService`.
- Mapping conventions:
  - `repositories/<data_source>_repo.py`
  - `services/<domain>_service.py`
  - `controllers/<role>_controller.py`
- Services always depend on repositories; never implement network calls or scraping logic inside services.

## Imports and Execution
- Use intra-package imports consistent with this codebase style, for example:
  - `from services.message_service import MessageService`
  - `from repositories.alphavantage_repo import AlphaVantageRepo`
- Prefer running as a module to ensure stable imports:
  - Run main: `python -m discord_finance_bot.main`
  - Run a submodule (for ad-hoc checks): `python -m discord_finance_bot.repositories.yahoo_repo`
- If running a file directly (not `-m`), ensure the working directory is the project root and set `PYTHONPATH` accordingly:
  - `PYTHONPATH=$(pwd)/discord_finance_bot python discord_finance_bot/repositories/yahoo_repo.py`

## Configuration and Environment Variables
- Loaded via `config.py` from `.env` or system environment:
  - `DISCORD_TOKEN`: Discord Bot token.
  - `DISCORD_CHANNEL_ID`: Target channel ID for pushes.
  - `SELECTED_STOCKS`: Comma-separated tickers, e.g., `AAPL,MSFT,GOOGL`.
  - `TIMEZONE`: IANA timezone, e.g., `Asia/Shanghai`.
  - `ALPHAVANTAGE_API_KEY`: Alpha Vantage API key.
  - `LOG_LEVEL`: Logging level (default `INFO`).

## Scheduling and Message Generation
- `SchedulerController` focuses on scheduling and sending: call `MessageService` once at a fixed time daily.
- Integrate new data sources (e.g., Alpha Vantage Earnings/IPO) inside `MessageService`:
  - `generate_daily_summary_json()`: aggregates `macro/stocks/sectors/earnings/ipos`.
  - `generate_daily_summary_text()`: outputs unified Markdown (tables built via `utils/data_parser.py`).
- Avoid building multiple separate texts inside the scheduler; keep the “single compose, single send” pattern.

## Recommended Workflow to Add Features
1. Create a Repository: implement external data retrieval and parsing (requests, CSV/JSON parsing, field selection, error handling).
2. Create a thin Service: wrap repository calls and expose clean methods for `MessageService`.
3. Aggregate in `MessageService`:
   - JSON: add the new keys in `generate_daily_summary_json()`.
   - Text: add tables or sections in `generate_daily_summary_text()`.
4. For scheduled pushes, keep `SchedulerController` calling `MessageService` only.
5. Write/update tests and verify locally.

## Testing and Verification
- Example tests: `discord_finance_bot/tests/test_message_service.py`.
- Recommendations:
  - Add unit tests for repository parsing (field mapping, date filtering).
  - Add snapshot-like tests for `MessageService` to validate JSON shape and text formatting.

## Commits and Version Control
- Prefer small, focused commits: each commit targets a single theme (e.g., “add repo”, “adjust message formatting”).
- `.gitignore` covers common Python artifacts and sensitive files like `.env`.
- Suggested commit messages: `feat(repo): add alphavantage earnings/ipo filters`, `refactor(service): embed calendars in message service`.

## Common Pitfalls and Fixes
- Import failures: prefer `python -m` module execution; or set `PYTHONPATH` to the package directory.
- Invalid tokens/keys: verify environment variables are loaded (`config.py`); rotate keys if needed.
- Timezone issues: `TIMEZONE` must be a valid IANA name; fallback is UTC if invalid.
- API rate limits: Alpha Vantage `demo` key has strict limits; use your own API key.

---
By following these conventions, integrating new features and maintaining daily pushes will be clearer and more stable. If you need stricter policies (type checking, CI checks, code formatting), extend this document with additional rules.