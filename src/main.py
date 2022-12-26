#! /usr/bin/env python3
import discord
from discord.ext import commands, tasks

import os # shutil, sys
import asyncio
import datetime
import traceback

import iksm_discord
import config


async def main():

    TOKEN = config.DISCORD_TOKENS["main"]
    extensions_dict = {  # cogの導入
        "main":["ext_splat"]
    }
    mode="main"

    intents = discord.Intents.default()
    intents.messages = True
    #intents.message_content = True

    description = f"stat.inkへ戦績自動アップロードを行うbotです。\nまずはstat.inkのAPI KEYを用意してください。\n"+\
    "詳しい使い方はこちら -> https://github.com/TomoTom0/SplatoonDiscordBot"

    bot = commands.Bot(command_prefix="?", description=description, intents=intents)

    """
    ctxのinstance -> 実質global
    """
    commands.Context.extensions_dict = extensions_dict
    commands.Context.extensions = extensions_dict["main"]

    # 起動時に動作する処理
    @bot.event
    async def on_ready():
        print(f"Logged in as\n{bot.user.name}\n{bot.user.id}\n------")

    # メッセージ受信時に動作する処理
    @bot.event
    async def on_message(message):
        # メッセージ送信者がBotだった場合は無視する
        if message.author.bot is True:
            return

        # bot.commandにmessageを流す
        try:
            await bot.process_commands(message)
        except Exception as e:
                error_message = f"エラーが発生しました。\n{traceback.format_exc()}"
                print(error_message)

    @bot.event  # error時に定期的にupload
    async def on_command_error(exception: Exception, ctx: commands.Context):
        print(traceback.format_exc())

    startup_extensions=commands.Context.extensions
    for extension in startup_extensions:
        try:
            await bot.load_extension(extension)
        except Exception as e:
            exc = f"{e}: {e.args}"
            print(f"Failed to load extension {extension}\n{exc}")

    interval=config.interval # 900*8
    @tasks.loop(seconds=interval)
    async def loop():
        next_interval=await iksm_discord.autoUpload_OneCycle(interval)
        loop.change_interval(seconds=next_interval)

    @loop.before_loop
    async def wait_for_loop():
        nowtime = datetime.datetime.now()
        next_interval=iksm_discord.obtain_nextInterval(interval)
        print(f"{nowtime} / Next Iksm Check : in {next_interval} sec")
        await asyncio.sleep(next_interval)

    if mode == "main":
        loop.start()
    await bot.start(TOKEN)


if __name__ == "__main__":  # cogを導入
    # start the client
    asyncio.run(main())