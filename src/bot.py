import os
import datetime
import discord
from discord.ext import commands
import asyncio
import s3s_wrapper
import random
import json
import sys
from pathlib import Path
import re

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

async def read_stream(stream, output_list):
    """
    ストリーム（stdoutやstderr）から継続的に1行ずつ読み取り、
    指定されたリストに内容を追加するヘルパー関数。
    """
    while True:
        line = await stream.readline()
        if not line:
            # ストリームが閉じられたらループを抜ける
            break
        # UTF-8でデコードし、リストに追加
        output_list.append(line.decode('utf-8', errors='ignore'))

# Command to register s3s via Discord Bot
@bot.command(name='register')
async def register(ctx):
    """Interactively register s3s via Discord Bot."""
    # Determine s3s script path
    base_dir = Path(__file__).parent.parent
    script_path = (base_dir / 's3s' / 's3s.py').resolve()
    if not script_path.exists():
        await ctx.send(f"s3s script not found at {script_path}")
        return
    # Spawn subprocess for registration
    # Use 'script' to allocate a pty for interactive prompts
    process = await asyncio.create_subprocess_exec(
        'script', '-qfc', f"{sys.executable} {str(script_path)} -nso -r", '/dev/null',
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    def check_author(m):
        return m.author == ctx.author and m.channel == ctx.channel
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    await ctx.send("Starting s3s registration.")
     # 標準出力と標準エラーの内容を保存するためのリスト
    # stdout_lines = []
    stderr_lines = []

    # stdoutとstderrを非同期で読み取るタスクを開始
    # stdout_task = asyncio.create_task(read_stream(process.stdout, stdout_lines))
    # stderr_task = asyncio.create_task(read_stream(process.stderr, stderr_lines))
    # Handle interactive prompts (API key, locale, login)
    while True:
        try:
            data = await process.stdout.readuntil(b': ')
        except asyncio.IncompleteReadError as e:
            data = e.partial
        except Exception:
            break
        if not data:
            break
        print(f"Received data: {data.decode(errors='ignore')}")
        decoded = ansi_escape.sub('', data.decode(errors='ignore'))
        await ctx.send(decoded)
        # Determine answer: if prompt is empty (locale input), send default empty line
        if decoded.strip() == "":
            answer_content = ""
        else:
            try:
                user_msg = await bot.wait_for('message', check=check_author, timeout=120)
                answer_content = user_msg.content
            except asyncio.TimeoutError:
                process.kill()
                await ctx.send("Registration timed out.")
                return
        print(f"Sending answer: {answer_content}")
        try:
            process.stdin.write((answer_content + '\n').encode())
            await process.stdin.drain()
        except Exception as e:
            print(f"Error writing to stdin: {e}")
            print("\n".join(stderr_lines))
            await ctx.send("Registration process ended unexpectedly.")
            break
    returncode = await process.wait()
    if returncode == 0:
        await ctx.send("s3s registration completed successfully.")
    else:
        await ctx.send(f"s3s registration failed with return code {returncode}.")
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