# main.py
import asyncio
import json
import discord
import os
from discord.ext import tasks, commands
from utils.vinted_scraper import search_vinted, get_market_price
from utils.db_handler import load_seen_ads, save_seen_ads
from utils.discord_notifier import send_to_discord
from flask import Flask
import threading

# --- Config ---
with open("config.json") as f:
    config = json.load(f)

# Token depuis variable d'environnement
config["discord_token"] = os.environ.get("DISCORD_TOKEN")

# --- Discord ---
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

seen_ads = load_seen_ads()

@tasks.loop(minutes=config["check_interval"])
async def check_vinted():
    global seen_ads
    channel = bot.get_channel(int(config["channel_id"]))
    for keyword in config["keywords"]:
        market_price = get_market_price(keyword)
        ads = search_vinted(keyword)
        for ad in ads:
            if ad.link not in seen_ads:
                margin = (market_price - ad.price) / market_price * 100 if market_price > 0 else 0
                if margin >= config["profit_threshold"]:
                    await send_to_discord(channel, ad, market_price, margin)
                seen_ads.add(ad.link)
    save_seen_ads(seen_ads)

@bot.event
async def on_ready():
    print(f"{bot.user} est connecté !")
    check_vinted.start()

# --- Flask pour garder le bot actif sur Railway ---
app = Flask('')

@app.route('/')
def home():
    return "Bot en ligne !"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_flask).start()

# --- Run Discord bot ---
bot.run(config["discord_token"])