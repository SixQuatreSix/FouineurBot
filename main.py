# main.py
import asyncio
import json
import subprocess
import sys
import discord
import os
from discord.ext import tasks, commands
from utils.vinted_scraper import search_vinted, get_market_price
from utils.db_handler import load_seen_ads, save_seen_ads
from utils.discord_notifier import send_to_discord
from flask import Flask
import threading

# --- Installer Playwright et ses navigateurs si nécessaire ---
subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)

# --- Config ---
with open("config.json") as f:
    config = json.load(f)

# Token depuis variable d'environnement
config["discord_token"] = os.environ.get("DISCORD_TOKEN")

# --- Discord ---
intents = discord.Intents.default()
intents.message_content = True  # Permet de lire les messages pour les commandes
bot = commands.Bot(command_prefix="!", intents=intents)

seen_ads = load_seen_ads()

# --- Fonction principale pour vérifier les annonces ---
async def check_vinted_func():
    global seen_ads
    channel = bot.get_channel(int(config["channel_id"]))
    if channel is None:
        print("❌ Erreur : Canal Discord introuvable ! Vérifie l'ID du canal et les permissions du bot.")
        return

    for keyword in config["keywords"]:
        try:
            ads = await search_vinted(keyword)
            print(f"[DEBUG] {len(ads)} annonces trouvées pour '{keyword}'")

            market_price = await get_market_price(keyword)
            print(f"[DEBUG] Prix moyen pour '{keyword}' : {market_price}")
        except Exception as e:
            print(f"[ERROR] Erreur scraping pour '{keyword}' : {e}")
            continue

        for ad in ads:
            margin = (market_price - ad.price) / market_price * 100 if market_price > 0 else 0
            print(f"[DEBUG] {ad.title} : prix {ad.price}, marge {margin:.2f}%")

            if ad.link not in seen_ads and margin >= config["profit_threshold"]:
                print(f"[DEBUG] Envoi de l'annonce : {ad.title}")
                try:
                    await send_to_discord(channel, ad, market_price, margin)
                except Exception as e:
                    print(f"[ERROR] Impossible d'envoyer l'annonce : {e}")
                seen_ads.add(ad.link)

    save_seen_ads(seen_ads)

# --- Tâche automatique toutes les X minutes ---
@tasks.loop(minutes=config["check_interval"])
async def check_vinted():
    await check_vinted_func()

# --- Commande Discord pour tester manuellement ---
@bot.command()
async def testcheck(ctx):
    await check_vinted_func()
    await ctx.send("✅ Check Vinted manuel terminé !")

# --- Événement Ready ---
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
