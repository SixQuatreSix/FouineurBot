# utils/discord_notifier.py
import discord

async def send_to_discord(channel, ad, market_price, margin):
    embed = discord.Embed(
        title=ad.title,
        url=ad.link,
        description=f"Prix demandé : {ad.price}€\nPrix moyen : {market_price:.2f}€\nMarge : {margin:.2f}%\nVendeur : {ad.seller} ({ad.seller_reviews} avis)",
        color=0x00ff00
    )
    embed.set_thumbnail(url=ad.photo_url)
    await channel.send(embed=embed)