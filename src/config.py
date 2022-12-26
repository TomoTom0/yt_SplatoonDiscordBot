import os

# とりあえずHerokuには非対応
IsHeroku = False

# 環境変数からDiscord bot tokenを読み取る
DISCORD_TOKENS = {
    "main": os.environ["SPLATOON_DISCORD_BOT_TOKEN"]}

dir_path_present=os.path.dirname(__file__)
const_paths = {
    "tmp_dir": "/tmp" if IsHeroku else f"{dir_path_present}/../configs_s2s",
    "tmp_dir3": "/tmp" if IsHeroku else f"{dir_path_present}/../configs_s3s",
    "splat_dir": f"{dir_path_present}/../splatnet2statink",
    "splat_dir3": f"{dir_path_present}/../s3s"
}

interval_tmp_str=str(os.environ.get("SPLATOON_DISCORD_BOT_INTERVAL: ", 900*8))
interval=900*8 if not interval_tmp_str.isdecimal() or int(interval_tmp_str) < 900 else int(interval_tmp_str)
