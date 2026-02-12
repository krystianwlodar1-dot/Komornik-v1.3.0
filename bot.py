import discord
from discord.ext import commands, tasks
from scraper import scrape
from database import get_all, count_houses
from datetime import datetime, timedelta
import os
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

FAST_THRESHOLD = timedelta(days=13, hours=20)
alerted_houses = set()

def parse_date(s):
    try:
        return datetime.strptime(s, "%d.%m.%Y (%H:%M)")
    except:
        return None

async def scrape_with_progress(ch):
    total_houses = count_houses()  # liczba w cache przed wczytaniem
    progress_msg = await ch.send(f"⏳ Wczytywanie domków: 0/{total_houses}…\n[░░░░░░░░░░] 0%")

    done_counter = 0

    def progress_callback(done, total):
        nonlocal done_counter
        done_counter = done

    # Wywołanie scrapera w osobnym wątku
    await asyncio.to_thread(scrape, progress_callback)

    # Aktualizacja paska co 3 sekundy
    while done_counter < count_houses():
        await asyncio.sleep(3)
        current = done_counter
        total = count_houses()
        percent = int(current / total * 100) if total else 0
        bars = "█" * (percent // 10) + "░" * (10 - percent // 10)
        # szacowany czas = zakładamy że tempo stałe
        est_time = (total - current) * 3  # w sekundach
        mins, secs = divmod(est_time, 60)
        await progress_msg.edit(content=f"⏳ Wczytywanie domków: {current}/{total}\n[{bars}] {percent}% ⏱ {mins}m{secs}s")
    
    # końcowe ustawienie
    total = count_houses()
    await progress_msg.edit(content=f"✅ Wczytano {total} domków\n[{'█'*10}] 100%")
    await check_fast(ch)

async def check_fast(ch):
    for h in get_all():
        dt = parse_date(h[6])
        if dt and datetime.utcnow() - dt >= FAST_THRESHOLD:
            if h[0] not in alerted_houses:
                alerted_houses.add(h[0])
                await ch.send(
                    f"🔥 **FAST ALERT**\n"
                    f"🏚️ {h[1]} ({h[2]})\n"
                    f"📐 {h[4]} sqm\n"
                    f"👤 {h[5]}\n"
                    f"🕒 {h[6]}\n"
                    f"🗺️ {h[3]}"
                )

@tasks.loop(minutes=15)
async def monitor():
    ch = bot.get_channel(CHANNEL)
    await asyncio.to_thread(scrape)
    await check_fast(ch)

@bot.event
async def on_ready():
    print("Komornik online")
    ch = bot.get_channel(CHANNEL)
    await scrape_with_progress(ch)
    monitor.start()

@bot.command()
async def status(ctx):
    await ctx.send(f"🏠 W cache jest {count_houses()} domków.")

@bot.command()
async def listfast(ctx):
    for h in get_all():
        dt = parse_date(h[6])
        if dt and datetime.utcnow() - dt >= FAST_THRESHOLD:
            await ctx.send(
                f"🔥 Domek offline ≥13d20h\n"
                f"🏚️ {h[1]} ({h[2]})\n"
                f"📐 {h[4]} sqm\n"
                f"👤 {h[5]}\n"
                f"🕒 {h[6]}\n"
                f"🗺️ {h[3]}"
            )

# NOWA KOMENDA !10
@bot.command()
async def _10(ctx):
    houses = []
    for h in get_all():
        dt = parse_date(h[6])
        if dt and datetime.utcnow() - dt >= FAST_THRESHOLD:
            houses.append(h)
    if not houses:
        await ctx.send("Brak domków do przejęcia (≥13d20h).")
        return
    for h in houses[:10]:
        await ctx.send(
            f"🔥 Możliwy domek do przejęcia\n"
            f"🏚️ {h[1]} ({h[2]})\n"
            f"📐 {h[4]} sqm\n"
            f"👤 {h[5]}\n"
            f"🕒 {h[6]}\n"
            f"🗺️ {h[3]}"
        )

bot.run(TOKEN)
