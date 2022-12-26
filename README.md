# SplatoonDiscordBot

Discord Bot on Python for Splatoon with s3s and stat.ink

## Introduction

自分で使用しているDiscord BotのScriptを整理しました。
詳しい使い方や試験などは後々行います。

公開済みの[DiscordBot_Heroku_Stat.ink](https://github.com/TomoTom0/DiscordBot_Heroku_Stat.ink)が、仕様変更やSplatoon 2->3への移行およびそれに伴うs2s->s3sの移行へのため実用に耐えなくなったことを受け、このRepositoryを作成しました。

s3sを用いてstat.inkへ戦績のアップロードを行います。(現在はlocalへの戦績保存のみ)

## Environments

NASやGCPなどでの使用を想定しています。
Herokuの無料枠はなくなってしまったそうです。

### 環境変数(Environmental Variables)

- SPLATOON_DISCORD_BOT_TOKEN: discord bot用のtoken。取得しておく必要がある。
- SPLATOON_DISCORD_BOT_INTERVAL: 戦績アップロードの間隔 (単位は秒)。デフォルトは7200秒( = 2時間)。

### Bot稼働まで

[DiscordBot_Heroku_Stat.ink](https://github.com/TomoTom0/DiscordBot_Heroku_Stat.ink)も参考に。ただし、Herokuは非対応です。

## How To Use

Coming Soon...

### ユーザー情報を登録する

### ユーザー情報を参照・編集・削除する

### 戦績を今すぐアップロードする

### その他


## Future Works

Coming Soon...

## References

- frozenpandaman/s3s: https://github.com/frozenpandaman/s3s
- frozenpandaman/splatnet2statink: https://github.com/frozenpandaman/splatnet2statink

