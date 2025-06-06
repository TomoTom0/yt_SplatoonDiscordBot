import os
import datetime
import discord
from discord.ext import commands
import asyncio
import s3s_wrapper
import random

import logging
logging.basicConfig(level=logging.INFO)

def load_dotenv_file(path='.env'):
    env = {}
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env[key] = value
    return env

envs = load_dotenv_file()
TOKEN = envs.get('DISCORD_TOKEN') or os.getenv('DISCORD_TOKEN')
INTERVAL = int(envs.get('UPLOAD_INTERVAL') or os.getenv('UPLOAD_INTERVAL') or 300)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='?', intents=intents)

@bot.command(name='Hello')
async def hello(ctx):
    print(f'Received command: {ctx.message.content}')
    await ctx.send('Hello!')

@bot.command(name='rand')
async def rand(ctx):
    """Generate random numbers interactively within a specified range."""
    def check_author(m):
        return m.author == ctx.author and m.channel == ctx.channel
    await ctx.send("最小値を入力してください。")
    try:
        min_msg = await bot.wait_for('message', check=check_author, timeout=60)
        min_val = int(min_msg.content)
    except Exception:
        await ctx.send("無効な入力です。コマンドを終了します。")
        return
    await ctx.send("最大値を入力してください。")
    try:
        max_msg = await bot.wait_for('message', check=check_author, timeout=60)
        max_val = int(max_msg.content)
    except Exception:
        await ctx.send("無効な入力です。コマンドを終了します。")
        return
    if min_val > max_val:
        await ctx.send("最小値が最大値より大きいです。コマンドを終了します。")
        return
    await ctx.send("生成する個数を入力してください。")
    try:
        count_msg = await bot.wait_for('message', check=check_author, timeout=60)
        count = int(count_msg.content)
    except Exception:
        await ctx.send("無効な入力です。コマンドを終了します。")
        return
    if count < 1:
        await ctx.send("個数は1以上である必要があります。コマンドを終了します。")
        return
    numbers = [str(random.randint(min_val, max_val)) for _ in range(count)]
    await ctx.send("生成された乱数: " + ", ".join(numbers))

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user}")
    bot.loop.create_task(periodic_upload())

async def periodic_upload():
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            await s3s_wrapper.upload_once()
        except Exception as e:
            logging.error(f"Error during periodic upload: {e}")
        await asyncio.sleep(INTERVAL)

if __name__ == '__main__':
    bot.run(TOKEN)