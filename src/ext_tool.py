import discord
from discord.ext import commands
# import pprint
import random
import os
import re
from iksm_discord import asyncio_run
import config

class Tool(commands.Cog):
    "サイコロやランダム選択"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="「?dice 2 6」で「3, 5」などが得られます。", pass_context=True)
    async def dice(self, ctx, dice_num="0", dice_max="0"):
        """
        サイコロを振ることができます。TRPGで使われるNdN記法もどき。
        2個の6面サイコロの結果がほしい場合は「?dice 2 6」と入力してください。"""
        if re.findall(r"\d+d\d+", dice_num):
            dice_num_int, dice_max_int = map(dice_num.split("d"))
        elif dice_max == "0" and dice_num.isnumeric():
            dice_max_int = int(dice_num)
            dice_num_int = 1
        elif dice_num.isnumeric() and dice_max.isnumeric():
            dice_num_int = int(dice_num)
            dice_max_int = int(dice_max)
        else:
            dice_num_int = 1
            dice_max_int = 6

        dice_num_int = dice_num_int if dice_num_int > 0 else 1
        dice_max_int = dice_max_int if dice_max_int > 0 else 6

        results = [random.randint(1, dice_max_int)
                   for _ in range(dice_num_int)]
        content = "ダイスロール！\n  " + \
            "".join([str(s) + (", " if num % 10 != 9 else "\n  ")
                    for num, s in enumerate(results)])
        await ctx.send(content)

    @commands.command(description="", pass_context=True)
    async def cmd(self, ctx, *cmds):
        "subprocessで実行する"
        returncode, stdout, stderr = await asyncio_run(cmd=" ".join(cmds), ctx=ctx, flag_alwaysSend=True)



class Extension(commands.Cog):
    "Extensionの調整・再読み込みを行います。"

    def __init__(self, bot):
        self.bot = bot

    async def manageExtension(self, ext_name, ctx, mode="reload"):
        try:
            if mode == "reload":
                await ctx.bot.reload_extension(ext_name)
            elif mode == "load":
                await ctx.bot.load_extension(ext_name)
            elif mode == "unload":
                await ctx.bot.unload_extension(ext_name)
        except Exception as e:
            exc = f"{e}: {e.args}"
            content = f"Failed to {mode} extension {ext_name}\n{exc}"
            await ctx.send(content)

    async def manageExtensions(self, extensions_new, ctx):
        extensions_old = list(ctx.bot.extensions.keys())
        extensions_dict = {
            "reload": list(set(extensions_old) & set(extensions_new)),
            "unload": list(set(extensions_old) - set(extensions_new)),
            "load": list(set(extensions_new) - set(extensions_old))
        }
        for mode, extensions in extensions_dict.items():
            for ext_name in extensions:
                await self.manageExtension(ext_name, ctx, mode)

    async def showExtensions(self, ctx):
        extensions_now = {
            "loaded": list(ctx.bot.extensions.keys()),
            "default": ctx.extensions_dict.get("default", []),
            "add": ctx.extensions_dict.get("add", [])
        }
        content = "\n\n".join(f"  `{k}`: "+", ".join(v)
                              for k, v in extensions_now.items())
        await ctx.send(content)

    @commands.command(description="", pass_context=True)
    async def reExt(self, ctx):
        await self.manageExtensions(list(ctx.bot.extensions.keys()), ctx)
        await ctx.send("Extensions has been reloaded")

    @commands.command(description="", pass_context=True)
    async def initExt(self, ctx):
        await ctx.send("Initializing extensions is processing...")
        extensions_new = ctx.extensions_dict.get("default", [])
        await self.manageExtensions(extensions_new, ctx)
        await ctx.send("Finished.")

    @commands.command(description="", pass_context=True)
    async def addExt(self, ctx):
        await ctx.send("Adding extensions is processing...")
        extensions_new = ctx.extensions_dict.get("default", [])+ctx.extensions_dict.get("add", [])
        await self.manageExtensions(extensions_new, ctx)
        await ctx.send("Finished.")

    @commands.command(description="", pass_context=True)
    async def showExt(self, ctx):
        await self.showExtensions(ctx)

    

async def setup(bot):
    await bot.add_cog(Tool(bot))
    await bot.add_cog(Extension(bot))