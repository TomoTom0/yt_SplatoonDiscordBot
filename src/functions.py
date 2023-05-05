import os
import sys
import shutil
import requests
import config
import asyncio
from discord.ext import commands

# # Basic

async def asyncio_run(cmd: str, ctx=None, flag_alwaysSend=False):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f"[{cmd!r} exited with {proc.returncode}]")
    text_content=f"```bash\n[stdout]\n{stdout.decode()}\n\n[stderr]\n{stderr.decode()}\n```"

    if stdout:
        print(f"[stdout]\n{stdout.decode()}")
    if stderr:
        print(f"[stderr]\n{stderr.decode()}")
    if (flag_alwaysSend is True or proc.returncode !=0) and isinstance(ctx, commands.Context):        
        await ctx.channel.send(text_content)

    sys.stdout.flush()
    return proc.returncode, stdout, stderr

async def _print_error(error_content: str, ctx=None):
    if isinstance(ctx, commands.Context):
        await ctx.channel.send(error_content)
    if callable(postWebhook_all):
        await postWebhook_all(content=error_content)

# # about iksm_discord

def obtainBoolEnv(key="SPLATOON_DISCORD_BOT_UPLOAD", default=True):
    return bool(os.environ.get(key, default))

def obtainSplatOption3(splat_upload_is_true=None):
    if splat_upload_is_true is None:
        splat_upload_is_true = obtainBoolEnv()
    _splatOption3_dict = {True: "-r", False: "-o"}
    return _splatOption3_dict[splat_upload_is_true]

# # Webhook

async def postWebhook_all(**kwargs):
    for url in config.error_webhooks_dict.get(config.BOT_MODE):
        await postWebhook(url, **kwargs)
    

async def postWebhook(url, **kwargs):
    # discord webhook
    if url.startswith("https://discord.com/api/webhooks/"):
        content=kwargs.get("content")
        if not isinstance(content, str) or len(content)==0:
            print(f"Error occured with posting webhook to {url} about {kwargs}", flush=True)
            return False
        body = {"content":content}
        res = requests.post(url=url, json=body)
        print(res, flush=True)
        return True