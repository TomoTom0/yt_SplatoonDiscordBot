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
from functions import asyncio_run
import glob2

# from discord_slash import cog_ext, SlashContext

import config

config_dir = config.const_paths["config_dir"]
config_dir3 = config.const_paths["config_dir3"]
DM_IS_REQUIRED = config.DM_IS_REQUIRED


class Splat(commands.Cog):
    "Splatoonに関するコマンドがいくつもあります。"

    def __init__(self, bot):
        self.bot = bot

    def obtainAccessInfo(self, ctx):
        placeIsGuild = ctx.channel.guild is not None
        access_info = {
            "check": True,
            "place": "guild" if placeIsGuild is True else "dm",
            "id": ctx.guild.id if placeIsGuild is True else ctx.author.id
        }
        return access_info

    def obtainInfoAllAcc(self, access_info={}):
        acc_name_sets = iksm_discord.obtainAccNames(access_info=access_info)
        content = f"{len(acc_name_sets)} accounts are registered:\n" +\
            "\t\t"+"\n\t\t".join([
                "**{}** :\t`{}`\t\ton {}".format(
                    num+1, acc["name"], iksm_discord.obtainDate(acc["time"]))
                for num, acc in enumerate(acc_name_sets)])
        return content

    async def waitInputAcc(self, ctx, access_info={}):
        acc_name_sets = iksm_discord.obtainAccNames(access_info=access_info)
        await ctx.send(self.obtainInfoAllAcc(access_info=access_info))

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

    # # command
    # ## start

    @commands.command(description="", pass_context=True)
    async def startIksm(self, ctx: commands.Context, STAT_INK_API_KEY=""):
        """新たにiksm_sessionを取得し、botにアカウントを登録します。\nstat.inkの登録を完了し、API KEYを取得しておいてください。"""
        
        if DM_IS_REQUIRED and ctx.channel.guild is not None:
            content="セキュリティの観点から`?startIksm`はBotとのDMで実行してください。"
            await ctx.send(content)
            return
        
        # 各種API KEYの入力確認
        # 例外としてskipはOK。skipの場合、戦績のuploadはされません。
        config_json = None
        if len(STAT_INK_API_KEY) != 43 and STAT_INK_API_KEY != "skip":
            content = "stat.inkの有効なAPI KEY(43文字)を入力してください。\n" +\
                "すでにs3sで生成したconfig.jsonが存在する場合は、その内容をコピペすることも可能です。\n"+\
                "stat.inkと連携する必要がない場合は`skip`\n" +\
                "コマンドを終了したい場合は`stop`と入力してください。"
            await ctx.send(content)

            def check_msg(msg):
                authorIsValid = (msg.author.id == ctx.message.author.id)
                contentIsCommand = msg.content in ["stop", "skip"]
                try:
                    contentIsJson = True
                    json.loads(msg.content)
                except Exception as e:
                    contentIsJson = False
                contentIsValidLength = (len(STAT_INK_API_KEY) == 43)
                contentIsValid = contentIsCommand or contentIsValidLength or contentIsJson
                return authorIsValid and contentIsValid
            try:
                input_msg = await ctx.bot.wait_for("message", check=check_msg, timeout=600)
                msg_content = input_msg.content
            except asyncio.TimeoutError:
                await ctx.channel.send("The command has been timeout, and please retry.")
                return
            input_content = msg_content
            if input_content == "stop":
                await ctx.channel.send("The command has been canceled.")
                return
            elif len(input_content)==43 or input_content in ["skip"]:
                STAT_INK_API_KEY = input_content
            else:
                try:
                    tmp_json = json.loads(input_content)
                    config_json=tmp_json
                except Exception:
                    config_json=None                    
                    STAT_INK_API_KEY = input_content
        if config.IsHeroku and not os.getenv("HEROKU_APIKEY", False):
            await ctx.channel.send("Herokuの環境変数としてHerokuのAPI KEYが入力されていません。\nコマンドを終了します。")
            return
        try:
            if config_json is not None:
                def check_msg_accName(msg):
                    authorIsValid = (msg.author.id == ctx.message.author.id)
                    contentIsValid = len(msg.content)>0
                    return authorIsValid and contentIsValid
                try:
                    text_content="config.txtの内容が読み込まれました。\n"+\
                        "**登録するアカウント名**を入力してください。\n"+\
                        "Nintendoアカウントの名前と一致している必要はありません。"
                    await ctx.channel.send(text_content)
                    input_msg = await ctx.bot.wait_for("message", check=check_msg_accName, timeout=600)
                    msg_content = input_msg.content
                except asyncio.TimeoutError:
                    await ctx.channel.send("The command has been timeout, and please retry.")
                    return
                acc_name = msg_content
                acc_name_set = iksm_discord.write_config(config_data_s3s=config_json, acc_name=acc_name, isHeroku=False)
            else:
                # print(STAT_INK_API_KEY)
                makeConfig = iksm_discord.MakeConfig()
                acc_name_set = await makeConfig.make_config_discord(STAT_INK_API_KEY, ctx)
                acc_name = acc_name_set["name"]
            if acc_name_set is None:
                await ctx.send("エラーが発生しました。詳細はbotのログを確認してください。")
                return
        except Exception as e:
            error_message = f"エラーが発生しました。\n{traceback.format_exc()}"
            print(error_message)
            await ctx.channel.send(error_message)
            return
        # convert config from s2s to s3s

        success_message = "新たに次のアカウントが登録されました。\n" +\
            f"\t\t`{acc_name}`\n" +\
            ("\nこの後botは再起動されます。次の操作はしばらくお待ちください。" if config.IsHeroku else "")
        await ctx.channel.send(success_message)
        # access_permission.json編集
        permission_info = {
            "dm": [ctx.author.id],
            "guild": [ctx.channel.guild.id if ctx.channel.guild is not None else 0],
            "author": [ctx.author.id]
        }
        iksm_discord.updateAccessInfo(
            acc_name_key_in=acc_name_set["key"], permission_info_in=permission_info)

    # ## rm
    @commands.command(description="", pass_context=True)
    async def rmIksm(self, ctx: commands.Context, acc_name=""):
        """指定されたアカウントの情報を削除します。"""
        def removeConfigFile(acc_name_key: str):
            if False and config.IsHeroku:  # for Heroku
                before_config_tmp = json.loads(os.getenv("iksm_configs", "{}"))
                before_config_jsons = eval(before_config_tmp) if type(
                    before_config_tmp) == str else before_config_tmp
                json_files = {
                    k: before_config_jsons[k] for k in before_config_jsons.keys() if k != acc_name_key}
                res = config.update_env(
                    {"iksm_configs": json.dumps(json_files)})
            else:
                for tmp_path in [f"{config_dir}/{acc_name_key}_config.txt", f"{config_dir3}/{acc_name_key}_config.txt"]:
                    if not os.path.isfile(tmp_path):
                        continue
                    print(f"{tmp_path} will be removed")
                    try:
                        os.remove(tmp_path)
                    except Exception as e:
                        print(f"{e}: {e.args}")
                        
        # check
        access_info = self.obtainAccessInfo(ctx)
        if acc_name == "":
            acc_name_set = await self.waitInputAcc(ctx, access_info=access_info)
            if acc_name_set is None:
                return
            acc_name = acc_name_set["name"]
        else:
            acc_name_set = await iksm_discord.checkAcc(ctx, acc_name, access_info=access_info)
        if acc_name_set.get("name") == "":
            return
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
        access_info = self.obtainAccessInfo(ctx)
        acc_name_sets = iksm_discord.obtainAccNames(access_info=access_info)
        content = f"{len(acc_name_sets)} accounts are registered:\n" +\
            "\t\t"+"\n\t\t".join([
                "**{}** :\t`{}`\t\ton {}".format(
                    num+1, acc.get("name", "ERROR"), iksm_discord.obtainDate(acc.get("time", 0)))
                for num, acc in enumerate(acc_name_sets)])
        await ctx.channel.send(content)

    @commands.command(description="", pass_context=True)
    async def upIksm(self, ctx: commands.Context, acc_name=""):
        """ただちにstat.inkへ戦績をアップロードします。"""
        await ctx.send("stat.inkへのアップロードを開始します。")
        access_info = self.obtainAccessInfo(ctx)
        acc_name_set = await iksm_discord.checkAcc(ctx, acc_name, access_info=access_info)
        await ctx.send("バックグラウンドで処理しています。詳細はログを確認してください。")
        await iksm_discord.auto_upload_iksm(acc_name_key_in=acc_name_set.get("key", None), fromLocal=False, ctx=ctx)

    @commands.command(description="", pass_context=True)
    async def toggleIksm(self, ctx: commands.Context):
        """S3S (Stat.inkへの戦績アプロード) の定期実行の有効無効を切り替えます。"""
        auto_s3s_key="SPLATOON_DISCORD_BOT_AUTO_S3S"
        auto_s3s_is_valid = iksm_discord.obtainBoolEnv(auto_s3s_key, True)
        auto_s3s_is_valid_Jap={True:"有効", False:"無効"}[not auto_s3s_is_valid]
        os.environ[auto_s3s_key]=str(not auto_s3s_is_valid)

        msg_content = "S3S (Stat.inkへの戦績アプロード) の定期実行を\n"+\
                f"    **{auto_s3s_is_valid_Jap}**\n"+\
                "に切り替えます。"
        await ctx.channel.send(msg_content)
                
    @commands.command(description="", pass_context=True)
    async def exportIksm(self, ctx: commands.Context, acc_name=""):
        """指定されたアカウントのconfig.jsonの内容を出力します。"""
        access_info = self.obtainAccessInfo(ctx)
        if acc_name == "":
            acc_name_set = await self.waitInputAcc(ctx, access_info=access_info)
            if acc_name_set is None:
                return
            acc_name = acc_name_set["name"]
        else:
            acc_name_set = await iksm_discord.checkAcc(ctx, acc_name, access_info=access_info)
            if acc_name_set["name"] == "":
                return
        acc_info = iksm_discord.obtainAccInfo(
            acc_name_set["key"], access_info=access_info)
        if acc_info is None:
            await ctx.channel.send(f"`{acc_name}` is not regitered or cannot be seen")
        await ctx.channel.send(f"`This is the content of {acc_name}'s config.txt:\n")
        await ctx.channel.send(f"```json\n{json.dumps(acc_info, indent=2)}\n```")
    
    @commands.command(description="", pass_context=True)
    async def gitPull(self, ctx: commands.Context, repo_name=""):
        """指定されたRepositoryの内容をgit pullで更新します。"""
        repo_paths_input=glob2.glob(f"**/{repo_name}/.git")
        if len(repo_name)==0 or len(repo_paths_input)==0:
            repo_paths_tmp=glob2.glob("**/.git")
            if len(repo_paths_tmp)==0:
                await ctx.channel.send("有効なRepositoryのディレクトリが存在しません。")
                return
        
        access_info = self.obtainAccessInfo(ctx)
        
    
class SubSplat(commands.Cog):
    "Splatoonに関する補助的なコマンド"

    def __init__(self, bot):
        self.bot = bot

    # ## check
    @commands.command(description="", pass_context=True)
    async def checkIksm(self, ctx: commands.Context, acc_name=""):
        """指定されたアカウントのiksm_sessionを表示します。"""
        access_info = self.obtainAccessInfo(ctx)
        if acc_name == "":
            acc_name_set = await self.waitInputAcc(ctx, access_info=access_info)
            if acc_name_set is None:
                return
            acc_name = acc_name_set["name"]
        else:
            acc_name_set = await iksm_discord.checkAcc(ctx, acc_name, access_info=access_info)
            if acc_name_set["name"] == "":
                return
        acc_info = iksm_discord.obtainAccInfo(
            acc_name_set["key"], access_info=access_info)
        if acc_info is None:
            await ctx.channel.send(f"`{acc_name}` is not regitered or cannot be seen")
        await ctx.channel.send(f"`{acc_name}`'s iksm_session is following:\n")
        await ctx.channel.send(acc_info["session_token"])

    @commands.command(description="", pass_context=True)
    async def upIksmFromLocal(self, ctx: commands.Context, acc_name=""):
        """Localに保存されていた戦績のjsonファイルをstat.inkへアップロードします。"""
        await ctx.send("stat.inkへ戦績jsonファイルのアップロードを開始します。")
        access_info = self.obtainAccessInfo(ctx)
        acc_name_set = await iksm_discord.checkAcc(ctx, acc_name, access_info=access_info)
        await iksm_discord.auto_upload_iksm(acc_name_key_in=acc_name_set.get("key", None), fromLocal=True, ctx=ctx)
        await ctx.send("バックグラウンドで処理しています。詳細はログを確認してください。")
    

async def setup(bot):
    await bot.add_cog(Splat(bot))
    await bot.add_cog(SubSplat(bot))
