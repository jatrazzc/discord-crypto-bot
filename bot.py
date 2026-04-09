import discord
import requests
import asyncio
import os
from flask import Flask
from threading import Thread

# ===== CONFIG =====
TOKEN = os.getenv("TOKEN")
PORT = int(os.environ.get("PORT", 10000))
UPDATE_TIME = 60  # segundos entre actualizaciones

# ===== WEB SERVER (OBLIGATORIO PARA RENDER) =====
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot activo ✅"

def run_web():
    print("🔥 Iniciando servidor web...")
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# ===== DISCORD BOT =====
CHANNELS = {
    "NXPCUSDT": 1491592257311342852,
    "BTCUSDT": 1491592429839847545,
    "ETHUSDT": 1491592579739812022,
    "SOLUSDT": 1491592537515757718,
    "AVAXUSDT": 1491592490942468247,
    "WEMIXUSDT": 1491592672949964990
}

intents = discord.Intents.default()
client = discord.Client(intents=intents)

last_prices = {}

def get_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        data = requests.get(url).json()
        return float(data["price"])
    except Exception as e:
        print(f"[ERROR] No se pudo obtener el precio de {symbol}: {e}")
        return None

def get_emoji(symbol):
    return {
        "NXPCUSDT": "🟣",
        "BTCUSDT": "🟡",
        "ETHUSDT": "💎",
        "SOLUSDT": "🟢",
        "AVAXUSDT": "🔺",
        "WEMIXUSDT": "🟠"
    }.get(symbol, "💰")

async def price_loop():
    await client.wait_until_ready()
    while not client.is_closed():
        print("⏱ Ejecutando actualización de precios...")
        for symbol, channel_id in CHANNELS.items():
            try:
                channel = client.get_channel(channel_id)
                if channel is None:
                    print(f"[ERROR] No se encontró el canal {channel_id} para {symbol}")
                    continue

                price = get_price(symbol)
                if price is None:
                    continue  # saltar si falla Binance

                print(f"[DEBUG] {symbol}: {price}")

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
                print(f"[UPDATE] Canal {channel.name} actualizado a {new_name}")

                last_prices[symbol] = price

            except discord.errors.Forbidden:
                print(f"[ERROR] No se pudo editar el canal {symbol} ({channel_id}): permisos insuficientes")
            except Exception as e:
                print(f"[ERROR] con {symbol}: {e}")

        await asyncio.sleep(UPDATE_TIME)

@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}")
    client.loop.create_task(price_loop())

# ===== START =====
keep_alive()
client.run(TOKEN)
