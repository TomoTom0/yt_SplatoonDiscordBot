import discord
from discord.ext import commands
import os
import re
import json
import datetime
import sys
import iksm_discord
import traceback
import asyncio

# from discord_slash import cog_ext, SlashContext

import config
guild_ids = config.guild_ids

config_dir = config.const_paths["tmp_dir"]
config_dir3 = config.const_paths["tmp_dir3"]


class Splat(commands.Cog):
    "Splatoonに関するコマンドがいくつもあります。"

    def __init__(self, bot):
        self.bot = bot

    def obtainInfoAllAcc(self):
        acc_name_sets = iksm_discord.obtainAccNames()
        content = f"{len(acc_name_sets)} accounts are registered:\n" +\
            "\t\t"+"\n\t\t".join([
                "**{}** :\t`{}`\t\ton {}".format(
                    num+1, acc["name"], iksm_discord.obtainDate(acc["time"]))
                for num, acc in enumerate(acc_name_sets)])
        return content

    async def waitInputAcc(self, ctx):
        acc_name_sets = iksm_discord.obtainAccNames()
        await ctx.send(self.obtainInfoAllAcc())

        def check_msg(msg):
            authorIsValid = (msg.author.id == ctx.message.author.id)
            contentIsCommand = msg.content in ["stop"]
            contentIsValidInt = msg.content in [
                str(num+1) for num in range(len(acc_name_sets))]
            contentIsValid = contentIsCommand or contentIsValidInt
            return authorIsValid and contentIsValid
        content = f"Select the account with the number(`1-{len(acc_name_sets)}`)\n" +\
            "If you want to cancel the command, please input `stop`"
        await ctx.send(content)
        try:
            input_msg = await ctx.bot.wait_for("message", check=check_msg, timeout=600)
            if input_msg.content == "stop":
                await ctx.channel.send("The command has been canceled.")
                return None
            acc_name_set = acc_name_sets[int(input_msg.content)-1]
            return acc_name_set
        except asyncio.TimeoutError:
            await ctx.channel.send("The command has been timeout, and please retry.")
            return None

    # start

    @commands.command(description="", pass_context=True)
    async def startIksm(self, ctx: commands.Context, STAT_INK_API_KEY=""):
        """新たにiksm_sessionを取得し、botにアカウントを登録します。\nstat.inkの登録を完了し、API KEYを取得しておいてください。"""
        # 各種API KEYの入力確認
        # 例外としてskipはOK。skipの場合、戦績のuploadはされません。
        if len(STAT_INK_API_KEY) != 43 and STAT_INK_API_KEY != "skip":
            content = "stat.inkの有効なAPI KEY(43文字)を入力してください。\n" +\
                "stat.inkと連携する必要がない場合は`skip`\n" +\
                "コマンドを終了したい場合は`stop`と入力してください。"
            await ctx.send(content)

            def check_msg(msg):
                authorIsValid = (msg.author.id == ctx.message.author.id)
                contentIsCommand = msg.content in ["stop", "skip"]
                contentIsValidLength = (len(STAT_INK_API_KEY) == 43)
                contentIsValid = contentIsCommand or contentIsValidLength
                return authorIsValid and contentIsValid
            try:
                input_msg = await ctx.bot.wait_for("message", check=check_msg, timeout=600)
                msg_content = input_msg.content
                if msg_content == "stop":
                    await ctx.channel.send("The command has been canceled.")
                    return
                else:
                    STAT_INK_API_KEY = msg_content
            except asyncio.TimeoutError:
                await ctx.channel.send("The command has been timeout, and please retry.")
                return
        if config.IsHeroku and not os.getenv("HEROKU_APIKEY", False):
            await ctx.channel.send("Herokuの環境変数としてHerokuのAPI KEYが入力されていません。\nコマンドを終了します。")
            return
        # try:
        try:
            print(STAT_INK_API_KEY)
            makeConfig = iksm_discord.makeConfig()
            acc_name = await makeConfig.make_config_discord(STAT_INK_API_KEY, ctx)
            if acc_name is None:
                await ctx.send("エラーが発生しました。詳細はbotのログを確認してください。")
                return
        except Exception as e:
            error_message = f"エラーが発生しました。\n{traceback.format_exc()}"
            print(error_message)
            await ctx.channel.send(f"エラーが発生しました。詳細はbotのログを確認してください。")
            return
        # convert config from s2s to s3s

        success_message = "新たに次のアカウントが登録されました。\n" +\
            f"\t\t`{acc_name}`\n" +\
            ("\nこの後botは再起動されます。次の操作はしばらくお待ちください。" if config.IsHeroku else "")
        await ctx.channel.send(success_message)
        # except Exception as e:
        #    error_message = f"エラーが発生しました。\n{traceback.format_exc()}"
        #    await ctx.channel.send(error_message)

    # check
    @commands.command(description="", pass_context=True)
    async def checkIksm(self, ctx: commands.Context, acc_name=""):
        """指定されたアカウントのiksm_sessionを表示します。"""
        if acc_name == "":
            acc_name_set = await self.waitInputAcc(ctx)
            if acc_name_set is None:
                return
            acc_name = acc_name_set["name"]
        else:
            acc_name_set = await iksm_discord.checkAcc(ctx, acc_name)
            if acc_name_set["name"] == "":
                return
        acc_info = iksm_discord.obtainAccInfo(acc_name_set["key"])
        await ctx.channel.send(f"`{acc_name}`'s iksm_session is following:\n")
        await ctx.channel.send(acc_info["session_token"])

    # rm
    @commands.command(description="", pass_context=True)
    async def rmIksm(self, ctx: commands.Context, acc_name=""):
        """指定されたアカウントの情報を削除します。"""
        def removeConfigFile(acc_name_key: str):
            if config.IsHeroku:  # for Heroku
                before_config_tmp = json.loads(os.getenv("iksm_configs", "{}"))
                before_config_jsons = eval(before_config_tmp) if type(
                    before_config_tmp) == str else before_config_tmp
                json_files = {
                    k: before_config_jsons[k] for k in before_config_jsons.keys() if k != acc_name_key}
                res = config.update_env(
                    {"iksm_configs": json.dumps(json_files)})
            else:
                os.remove(f"{config_dir}/{acc_name_key}_config.txt")
                os.remove(f"{config_dir3}/{acc_name_key}_config.txt")

        # check
        if acc_name == "":
            acc_name_set = await self.waitInputAcc(ctx)
            if acc_name_set is None:
                return
            acc_name = acc_name_set["name"]
        else:
            acc_name_set = await iksm_discord.checkAcc(ctx, acc_name)
        await ctx.channel.send(f"Do you want to remove `{acc_name}`'s config file?(`yes/no`)")

        def check_msg(msg):
            authorIsValid = (msg.author.id == ctx.message.author.id)
            contentIsValid = msg.content in ["yes", "no"]
            return authorIsValid and contentIsValid
        try:
            input_msg = await ctx.bot.wait_for("message", check=check_msg, timeout=600)
            if input_msg.content == "yes":
                removeConfigFile(acc_name_set["key"])
                await ctx.channel.send("Removed.")
            elif input_msg.content == "no":
                await ctx.channel.send("The command has been canceled.")
        except asyncio.TimeoutError:
            await ctx.channel.send("The command has been timeout, and please retry.")
            return

    # show
    @commands.command(description="", pass_context=True)
    async def showIksm(self, ctx: commands.Context):
        """登録されているnintendoアカウント一覧を表示します。"""
        acc_name_sets = iksm_discord.obtainAccNames()
        content = f"{len(acc_name_sets)} accounts are registered:\n" +\
            "\t\t"+"\n\t\t".join([
                "**{}** :\t`{}`\t\ton {}".format(
                    num+1, acc["name"], iksm_discord.obtainDate(acc["time"]))
                for num, acc in enumerate(acc_name_sets)])
        await ctx.channel.send(content)

    @commands.command(description="", pass_context=True)
    async def upIksm(self, ctx):
        """ただちにstat.inkへ戦績をアップロードします。"""
        await ctx.send("stat.inkへのアップロードを開始します。")
        await iksm_discord.auto_upload_iksm()
        await ctx.send("バックグラウンドで処理しています。詳細はログを確認してください。")

    @commands.command(description="", pass_context=True)
    async def upIksmFromLocal(self, ctx):
        """Localに保存されていた戦績のjsonファイルをstat.inkへアップロードします。"""
        await ctx.send("stat.inkへ戦績jsonファイルのアップロードを開始します。")
        await iksm_discord.auto_upload_iksm(fromLocal=True)
        await ctx.send("バックグラウンドで処理しています。詳細はログを確認してください。")


async def setup(bot):
    await bot.add_cog(Splat(bot))
