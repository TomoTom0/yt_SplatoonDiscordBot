import os
import sys
import discord
import glob2
from dotenv import load_dotenv

# read .env
env_files=sorted(glob2.glob("../../**/.env"))
if len(env_files) > 0:
    load_dotenv(env_files[0])

# とりあえずHerokuには非対応
IsHeroku = False

# 環境変数からDiscord bot tokenを読み取る
DISCORD_TOKENS = {
    "main": os.environ["SPLATOON_DISCORD_BOT_TOKEN"],
    "test": os.environ.get("SPLATOON_DISCORD_BOT_TOKEN_TEST", os.environ["SPLATOON_DISCORD_BOT_TOKEN"])
}

# dir_path_present = os.path.dirname(__file__)
const_paths = {
    "config_dir": "/tmp" if IsHeroku else f"{os.path.dirname(__file__)}/../configs_s2s",
    "config_dir3": "/tmp" if IsHeroku else f"{os.path.dirname(__file__)}/../configs_s3s",
    "splat_dir": f"{os.path.dirname(__file__)}/../splatnet2statink",
    "splat_dir3": f"{os.path.dirname(__file__)}/../s3s",
    "out_root": f"{os.path.dirname(__file__)}/../out/splat_results",
    "done_root": f"{os.path.dirname(__file__)}/../out/done_results",
    "access_json_path": f"{os.path.dirname(__file__)}/../configs_s3s/access_permission.json"
}

ignored_channels_dict = {
    "main": str(os.environ.get("SPLATOON_DISCORD_BOT_IGNORED_CHANNELS_MAIN", "")).split(","),
    "test": str(os.environ.get("SPLATOON_DISCORD_BOT_IGNORED_CHANNELS_TEST", "")).split(",")
}

noticed_channels_dict = {
    "main": str(os.environ.get("SPLATOON_DISCORD_BOT_NOTICED_CHANNELS_MAIN", "")).split(","),
    "test": str(os.environ.get("SPLATOON_DISCORD_BOT_NOTICED_CHANNELS_TEST", "")).split(",")
}

_interval_tmp_str = str(os.environ.get("SPLATOON_DISCORD_BOT_INTERVAL", 7200))
SPLAT_UPLOAD_INTERVAL = 7200 if not _interval_tmp_str.isdecimal() or int(
    _interval_tmp_str) < 900 else int(_interval_tmp_str)


SPLAT_UPLOAD_IS_TRUE = bool(os.environ.get(
    "SPLATOON_DISCORD_BOT_UPLOAD", True))
_splatOption3_dict = {True: "-r", False: "-o"}
SPLAT_OPTION3 = _splatOption3_dict[SPLAT_UPLOAD_IS_TRUE]

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

COMMAND_PREFIX = "?"

# --------------

python_args = sys.argv


DM_IS_REQUIRED = "DM" in python_args

# main
BOT_MODE = "test" if "test" in python_args else "main"
DISCORD_TOKEN = DISCORD_TOKENS[BOT_MODE]
extensions_dict = {  # cogの導入
    "default": ["ext_splat"]
}

description = f"stat.inkへ戦績自動アップロードを行うbotです。\nまずはstat.inkのAPI KEYを用意してください。\n" +\
    "詳しい使い方はこちら -> https://github.com/TomoTom0/yt_SplatoonDiscordBot"

# --------- additional functions -----------


async def _additional_on_ready(bot):
    return


async def _additional_on_message_judge(bot, message):
    ignored_channels=ignored_channels_dict.get(BOT_MODE, [])
    noticed_channels=noticed_channels_dict.get(BOT_MODE, [])
    channel_id=str(message.channel.id)
    
    if len(noticed_channels)>0:
        if channel_id in noticed_channels:
            return True
        else:
            return False
    else:
        if channel_id in ignored_channels:
            return False
        else:
            return True


async def _additional_on_message_remake(bot, message):
    message_new = message
    return message_new


async def _additional_on_message(bot, message):
    return


async def _additional_on_command_error(bot, ctx):
    return


async def _additional_loop(bot):
    return

additional_functions_dict = {
    "on_ready": _additional_on_ready,
    "on_message": _additional_on_message,
    "on_message_judge": _additional_on_message_judge,
    "on_message_remake": _additional_on_message_remake,
    "on_command_error": _additional_on_command_error,
    "loop": _additional_loop
}
# --------------------------------
