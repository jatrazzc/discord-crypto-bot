import discord
import requests
import asyncio
import os

TOKEN = os.getenv("TOKEN")



CHANNELS = {
    "NXPCUSDT": 1491535220661555424,
    "BTCUSDT": 1491535867628490832,
    "ETHUSDT": 1491535369982709780,
    "SOLUSDT": 1491535327620235525,
    "AVAXUSDT": 1491535431240515675
}

UPDATE_TIME = 120

intents = discord.Intents.default()
client = discord.Client(intents=intents)


def get_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    data = requests.get(url).json()
    return float(data["price"])


def get_emoji(symbol):
    return {
        "NXPCUSDT": "🟣",
        "BTCUSDT": "🟡",
        "ETHUSDT": "💎",
        "SOLUSDT": "🟢",
        "AVAXUSDT": "🔺"
    }.get(symbol, "💰")


@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}")

    last_prices = {}

    while True:
        for symbol, channel_id in CHANNELS.items():
            try:
                channel = client.get_channel(channel_id)
                price = get_price(symbol)

                last_price = last_prices.get(symbol)

                if last_price:
                    if price > last_price:
                        trend = "📈"
                    elif price < last_price:
                        trend = "📉"
                    else:
                        trend = "➖"
                else:
                    trend = ""

                emoji = get_emoji(symbol)

                if price >= 1000:
                    price_text = f"${price:,.0f}"
                elif price >= 1:
                    price_text = f"${price:,.2f}"
                else:
                    price_text = f"${price:.4f}"

                name = symbol.replace("USDT", "")

                new_name = f"{trend}{emoji} {name}: {price_text}"

                await channel.edit(name=new_name)

                last_prices[symbol] = price

            except Exception as e:
                print(f"Error con {symbol}:", e)

        await asyncio.sleep(UPDATE_TIME)


client.run(TOKEN)
