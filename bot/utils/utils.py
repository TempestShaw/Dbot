import os
import random
import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands, tasks
from dotenv import load_dotenv
from newsapi import NewsApiClient
import asyncio
from datetime import datetime, timedelta
import forecasting
load_dotenv(verbose=True)
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
NEWSAPI_TOKEN = os.getenv('NEWSAPI_TOKEN')
newsapi = NewsApiClient(api_key=NEWSAPI_TOKEN)
TS_KEY = os.getenv('TS_KEY')

def get_news(source="bbc-news"):
    top_headlines = newsapi.get_top_headlines(sources=source)
    news_articles = top_headlines['articles']
    embed = discord.Embed(
        title='News',
        colour=discord.Colour.green()
    )
    embed.set_footer(text="News from " + source)
    for l in news_articles:
        embed.add_field(name=l["title"], value=l["description"], inline=False)
        embed.add_field(name=l["url"], value=l["publishedAt"], inline=False)
    return embed

def get_stock_basic_change(stock_url):
    page = requests.get(stock_url)
    soup = BeautifulSoup(page.text, "html.parser")
    try:
        current_price = soup.find_all("div", {"class": "My(6px) Pos(r) smartphone_Mt(6px)"})[0].find_all("span")[0]
        change = soup.find_all("div", {"class": "My(6px) Pos(r) smartphone_Mt(6px)"})[0].find_all("span")[1]
        return "NASDAQ 100 Pre Market\t" + current_price.text + "\t" + change.text
    except:
        return "No data found"

def av_stat_analytics(stocklist,
                      current_date=(datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"),
                      past_date=(datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")):
#datetime get last friday

    stocklist = ",".join(stocklist)
    url = f'https://alphavantageapi.co/timeseries/analytics?SYMBOLS={stocklist}&RANGE={past_date}&RANGE={current_date}&INTERVAL=DAILY&OHLC=close&CALCULATIONS=MEAN,STDDEV,CORRELATION&apikey={TS_KEY}'
    # url = f'https://alphavantageapi.co/timeseries/analytics?SYMBOLS=AAPL,MSFT,IBM&RANGE=2023-07-01&RANGE=2023-08-31&INTERVAL=DAILY&OHLC=close&CALCULATIONS=MEAN,STDDEV,CORRELATION&apikey={TS_KEY}'
    r = requests.get(url)
    data = r.json()
    print(url)
    print(data)
av_stat_analytics(["AAPL", "MSFT","IBM"])

