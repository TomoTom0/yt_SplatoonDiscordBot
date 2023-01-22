#! /usr/bin/env python3
import discord
from discord.ext import commands, tasks

#import os
import sys
import asyncio
import datetime
import traceback

import iksm_discord
import config

def _empty_func(**kwargs):
    return

async def main():
    DISCORD_TOKEN = config.DISCORD_TOKEN
    BOT_MODE = config.BOT_MODE
    extensions_dict = config.extensions_dict
    description = config.description
    intents = config.intents
    COMMAND_PREFIX = config.COMMAND_PREFIX
    SPLAT_UPLOAD_INTERVAL = config.SPLAT_UPLOAD_INTERVAL  # 900*8
    additional_functions_dict = config.additional_functions_dict

    bot = commands.Bot(command_prefix=COMMAND_PREFIX,
                       description=description, intents=intents)

    """
    ctxのinstance: 実質global
    """
    commands.Context.extensions_dict = extensions_dict
    commands.Context.extensions = extensions_dict.get("default", [])

    # 起動時に動作する処理
    @bot.event
    async def on_ready():
        await additional_functions_dict.get("on_ready", _empty_func)(bot)
        print(f"Logged in as\n{bot.user.name}\n{bot.user.id}\n------")
        sys.stdout.flush()

    # メッセージ受信時に動作する処理
    @bot.event
    async def on_message(message_orig):
        flag_continue = await additional_functions_dict.get("on_message_judge", _empty_func)(bot, message_orig)
        message_new = await additional_functions_dict.get("on_message_remake", _empty_func)(bot, message_orig)
        if flag_continue is False:
            return
        elif isinstance(message_new, discord.Message):
            message = message_new
        else:
            message = message_orig

        await additional_functions_dict.get("on_message", _empty_func)(bot, message_orig)

        # メッセージ送信者がBotだった場合は無視する
        if message.author.bot is True:
            return

        # bot.commandにmessageを流す
        try:
            await bot.process_commands(message)
        except Exception as e:
            error_message = f"エラーが発生しました。\n{traceback.format_exc()}"
            print(error_message)
        sys.stdout.flush()

    @bot.event
    async def on_command_error(exception: Exception, ctx: commands.Context):
        await additional_functions_dict.get("on_command_error", _empty_func)(bot, ctx)
        print(traceback.format_exc())

    startup_extensions = commands.Context.extensions
    for extension in startup_extensions:
        try:
            await bot.load_extension(extension)
        except Exception as e:
            exc = f"{e}: {e.args}"
            print(f"Failed to load extension {extension}\n{exc}")
    sys.stdout.flush()


    @tasks.loop(seconds=SPLAT_UPLOAD_INTERVAL)
    async def loop():
        await additional_functions_dict.get("loop", _empty_func)(bot)
        next_interval = await iksm_discord.autoUpload_OneCycle(SPLAT_UPLOAD_INTERVAL)
        loop.change_interval(seconds=next_interval)
        sys.stdout.flush()

    @loop.before_loop
    async def wait_for_loop():
        nowtime = datetime.datetime.now()
        next_interval = iksm_discord.obtain_nextInterval(SPLAT_UPLOAD_INTERVAL)
        print(f"{nowtime} / Next Splatoon Results Check: in {next_interval} sec")
        sys.stdout.flush()
        await asyncio.sleep(next_interval)

    if "main" in BOT_MODE:
        loop.start()
    await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    # start the client
    asyncio.run(main())
