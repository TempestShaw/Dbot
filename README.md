# Trading Bot for Discord: Active & Quant Investing

This document outlines the design and functionality of a Discord bot focused on trading. The bot aims to cater to both active and quant investors by providing actionable insights, real-time alerts, and a platform for strategy testing and optimization.

## Features Overview

### Active Investing Module

- **Signal Detection**: Leverages technical analysis, news sentiment, and other indicators to provide users with actionable investment signals.
- **Stock Watchlist**: Users can create, manage, and monitor a personalized watchlist of stocks.
- **Alerts and Notifications**: Customizable alerts based on price changes, volume spikes, or significant news events.

### Quant Investing Module

- **盘中突破 (Intraday Breakout) Signal**: Identifies potential intraday breakouts within specific industries, signaling stocks with significant price surges.
- **Backtesting Platform**: Allows users to test the 盘中突破 signal and other strategies against historical data.
- **Strategy Optimization**: Tools for strategy refinement and optimization based on user-defined parameters.

## Detailed Functionality

### Active Investing

#### Useful Signals Examples

- **Volume Spike**: Alerts on abnormal volume, indicating potential insider information or heightened interest.
- **Price Breakout**: Notifies users when a stock price exits a predefined range, suggesting a strategic entry or exit point.
- **Moving Average Crossover**: Identifies bullish signals when a short-term moving average crosses above a long-term moving average.

#### Main Stock Examples

- Targets high-liquidity stocks, especially within the S&P 500, to ensure relevance and market interest.
- Offers sector-specific insights for key areas like technology (e.g., AAPL, MSFT) and finance (e.g., JPM, GS).

### Quant Investing

#### 盘中突破 (Intraday Breakout)

- Focuses on industries with collective momentum and singles out stocks breaking past their 30-day highs, with substantial trading volume as a supporting factor.

#### Backtesting and Optimization

- Enables simple strategy input for performance evaluation against historical data.
- Allows users to tweak strategy parameters, such as lookback periods and volume thresholds, for optimal results.

## Implementation Hierarchy

1. **Bot Framework**
   - **Command Parser**: Routes user commands to the correct module.
   - **User Management**: Manages preferences, watchlists, and alert settings.

2. **Active Investing Module**
   - **Signal Finder**: Searches for active investment signals in the market.
   - **Alert System**: Dispatches real-time notifications based on user-defined criteria.

3. **Quant Investing Module**
   - **Strategy Engine**: Implements the 盘中突破 signal and other quant strategies.
   - **Backtester**: Facilitates strategy testing with historical data and parameter adjustments.

## Conclusion

This Discord bot is designed to be an essential tool for traders, combining active and quant investing features to provide a comprehensive trading platform. By prioritizing user engagement and continuous improvement, the bot aims to support informed trading decisions within the Discord community. Compliance with financial regulations and data protection laws will be upheld in all functionalities.

## Notes

### 0.0.1
As calling api is expensive, I would like to develop the stock choosing function first. It helps us to choose the most valuable stock at that day.
For the same reason, I will focus on daily candle instead of shorter period. Or maybe I can select some stock today, and look at their intraday performance the next day.

**TO-DO list**
 - select stocks by technical analysis
   - 1. find the most valuable industry(s)
   - 2. looking for out-performed-industry stock(s) by technical analysis
   - 3. Monitoring their performance tmr