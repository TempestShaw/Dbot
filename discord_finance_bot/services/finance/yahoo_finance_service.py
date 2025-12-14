from datetime import datetime, timedelta
import yfinance as yf
import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt
import io
from typing import Optional, Dict, Tuple
from utils.logger import get_logger
from yfinance.exceptions import YFRateLimitError
import json


class YahooFinanceService:
    def __init__(self):
        self.logger = get_logger(__name__)


    def fetch_stock_data(self, ticker: str, period: str = '3mo'):
        try:
            self.logger.info(f"Fetching {ticker} data, period={period}")

            data = yf.download(
                tickers=ticker,
                period=period,
                interval="1d",
                auto_adjust=False,
                progress=False,
                threads=False,
            )

            if data is None or data.empty:
                return {
                    "type": "not_found",
                    "message": f"No price data found for {ticker}"
                }

            data.index = pd.to_datetime(data.index, utc=True)

            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            return data

        except YFRateLimitError as e:
            self.logger.warning(f"Yahoo rate limit hit for {ticker}: {e}")
            return {
                "type": "rate_limit",
                "message": "Yahoo Finance rate limit exceeded. Please try again later."
            }

        except json.JSONDecodeError as e:
            # Common when Yahoo returns empty body
            self.logger.warning(f"Yahoo JSON error for {ticker}: {e}")
            return {
                "type": "unknown",
                "message": "Yahoo Finance returned invalid data."
            }

        except Exception as e:
            self.logger.error(f"Unexpected error fetching {ticker}: {e}")
            return {
                "type": "unknown",
                "message": str(e)
            }



    def extract_stock_info(self, ticker: str, data: pd.DataFrame) -> Dict:
        latest = data.iloc[-1]
        previous = data.iloc[-2] if len(data) > 1 else latest

        change = latest["Close"] - previous["Close"]
        change_percent = (change / previous["Close"]) * 100 if previous["Close"] else 0

        return {
            "ticker": ticker.upper(),
            "price": round(latest["Close"], 2),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "volume": int(latest["Volume"]),
            "day_high": round(latest["High"], 2),
            "day_low": round(latest["Low"], 2),
        }

    def create_candlestick_chart(
        self,
        data: pd.DataFrame,
        ticker: str,
        period: str = "3mo",
        mav_periods: Tuple[int, ...] = (10, 20),
    ) -> bytes:
        # Parse period and set title
        period_title = period.upper()
        if period.endswith('d'):
            period_title = f"Last {period[:-1]} Days"
        elif period.endswith('mo'):
            period_title = f"Last {period[:-2]} Month{'s' if period[:-2] != '1' else ''}"
        elif period.endswith('y'):
            period_title = f"Last {period[:-1]} Year{'s' if period[:-1] != '1' else ''}"

        plots = []
        for p in mav_periods:
            if len(data) >= p:
                plots.append(
                    mpf.make_addplot(
                        data["Close"].rolling(p).mean(),
                        width=1.5
                    )
                )
        market_colors = mpf.make_marketcolors(
            up="#26a69a",
            down="#ef5350",
            edge="inherit",
            wick="inherit",
            volume="#8e8e8e"
        )

        style = mpf.make_mpf_style(
            marketcolors=market_colors,
            facecolor="#0e1117",
            figcolor="#0e1117",
            gridcolor="#2a2e39",
            gridstyle="--",
            rc={
                "axes.labelcolor": "#c9d1d9",
                "xtick.color": "#8b949e",
                "ytick.color": "#8b949e",
                "axes.edgecolor": "#30363d",
                "text.color": "#c9d1d9",
                "font.size": 11,
            }
        )

        fig, _ = mpf.plot(
            data,
            type="candle",
            style=style,
            addplot=plots,
            volume=True,
            title=f"{ticker} - {period_title}",
            returnfig=True,
            figsize=(14, 8),
        )


        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()
