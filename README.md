# yt_SplatoonDiscordBot

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

|環境変数|既定値|説明|
|-|-|-|
|`SPLATOON_DISCORD_BOT_TOKEN`|省略不可|discord bot用のtoken。取得しておく必要があります。|
|`SPLATOON_DISCORD_BOT_INTERVAL`|7200| 戦績アップロードの間隔 (単位は秒)。デフォルトは2時間。|
|`SPLATOON_DISCORD_BOT_UPLOAD`|true|定期戦績チェックでstat.inkにアップロードするか(true)、localにjsonファイルを保存するのみか(false)。デフォルトは前者。値はBoolean型で解釈されます。|

## Bot稼働まで

[DiscordBot_Heroku_Stat.ink](https://github.com/TomoTom0/DiscordBot_Heroku_Stat.ink)より引用。ただし、Herokuは非対応です。


### 事前準備
- stat.ink : アカウント作成、API KEYコピー
- discord : アカウント作成、DISCORD BOT TOKENコピー、BOTのserverへの追加
    - 参考 [Discord Botアカウント初期設定ガイド for Developer](https://qiita.com/1ntegrale9/items/cb285053f2fa5d0cccdf)のうち**はじめに~サーバーへの登録**

### Bot起動まで
`git clone`などでダウンロードし、`pip3 install -r requirements.txt`で必要なライブラリをインストールします。最後に`python3 src/main.py`でdiscord botを起動します。terminalにエラーメッセージが出なければ大丈夫です。`screen`は必要に応じて利用してください。

### Intents設定

Discord Botでmessageなどを取り扱うには(招待リンク生成の項目で選択する)Permissionに加えて、現在はIntentsの設定も必要です。
[Discord.pyのReferenceページ](https://discordpy.readthedocs.io/en/stable/intents.html#privileged-intents)を参考に「Privileged Gateway Intents」の「MESSAGE CONTENT INTENT」を有効にしてください。

## How To Use

`?`をprefixとして`?COMMAND`で各種コマンドを実行できます。一部のコマンドはスペース区切りで引数が入力可能です。
また`?help`でbot自体のhelpおよびコマンド一覧を確認できます。さらに`?help COMMAND`で`COMMAND`の詳細を確認できます。

### BotへのNintendoアカウント登録

`?startIksm <STATINK_API_KEY>`
1. stat.inkのAPI KEYを用意しておきます。
2. botとのDMなどで`?startIksm <STATINK_API_KEY>`のように、`?startIksm`に続けてAPI KEYを入力して送信します。
(**botと同じサーバーに加入していれば、アカウントの設定にもよりますが、そのbotとDMを行うことが可能です。**)

> ※注意
**API KEYやTOKENなどと呼ばれるものは、すべからくアカウント名とパスワードのセットと等価です。他人にばれることはとても危険なことです。**
家族やごく親しい友人しかいないサーバーでは大丈夫かもしれませんが、できるだけbotとのDMで`?startIksm`は行ってください。

3. すると、botからURLが送られてくるのでそのリンクをタップします。
<img with="80%" src="img/discord_startIksm.png"/>
4. リンク先でログインすると、連携アカウントの選択画面になるので、
**「この人にする」を右クリック(スマホなら長押し)して、リンク先のURLをコピーします。**
<img with="80%" src="img/nintendo_select.png"/>

5. discordに戻り、コピーしたリンクを貼り付け、少し待つと`新たにアカウントが登録されました。`と表示されます。
<img with="80%" src="img/discord_startIksm2.png"/>

ここまでできれば、戦績の定期アップロードは自動で行われます。(デフォルトは2時間。環境変数`SPLATOON_DISCORD_BOT_INTERVAL`で設定されます。)

### 各種コマンド
`?help Splat`とBotに入力することでも確認できます。

|コマンド|引数|説明|
|-|-|-|
|`?startIksm`|`STAT_INK_API_KEY`| 新たにiksm_sessionを取得し、botにアカウントを登録します。 事前にstat.inkの登録を完了し、API KEYを取得しておいてください。|
|`?checkIksm`|`acc_name`|指定されたアカウントのiksm_sessionを表示します。|
|`?rmIksm`|`acc_name`|指定されたアカウントの情報を削除します。|
|`?showIksm`|なし|登録されているnintendoアカウント一覧を表示します。|
|`?upIksm`|なし|ただちに戦績チェックを行います。操作にはしばらく時間がかかります。|


## Future Works

Coming Soon...

## Botを自分好みに改造したくなったら
[Discord Bot 最速チュートリアル【Python&Heroku&GitHub】](https://qiita.com/1ntegrale9/items/aa4b373e8895273875a8#8-dynos%E3%81%AE%E8%A8%AD%E5%AE%9A)を参考にしてください。
(これだけでは不足していますが……)

botのupdateへの対応や既存のbotとの併用を便利にするため、main.pyに触れずともconfig.pyのみで独自の変更を加えられるようにしました。
本botが既定で対応していてかつ、config.pyで設定できる主な変数・関数は以下の通りです。もちろん、必要に応じた他の要素も追加可能です。

|変数/関数名|既定値/引数|説明|
|-|-|-|
|`command_prefix`|`?`|本botにコマンドを与えるときのprefix|
|`description`|既定値割愛|`?help`の際に表示される本botの説明|
|`_additional_on_ready`|`bot`|`on_ready`のはじめに実行される関数|
|`_additional_on_message_judge`|`bot, message`|`on_message`の1番目に実行される関数で、`message`に反応するべきかどうかを判断する。返り値が`False`ならば反応しない。|
|`_additional_on_message_remake`|`bot, message`|`on_message`の2番目に実行される関数で、`message`を適切に作り変える。返り値が`discord.Message`classの場合のみ`message`が置き換えられる。|
|`_additional_on_message`|`bot, message`|`on_message`の3番目に実行される関数|
|`_additional_on_command_error`|`bot, ctx`|`on_command_error`のはじめに実行される関数|
|`_additional_on_loop`|`bot`|`loop`のはじめに実行される関数|


積極的に変更されないことが予想される変数・関数は以下の通りです。

|変数/関数名|既定値/引数|説明|
|`DISCORD_TOKENS`|既定値割愛||
|`mode`|`main`|`mode`に`main`が含まれる場合のみ戦績の定期チェックは行われます|
|`intents`|||
|`const_paths`|||
|`intents`|||


## References

- frozenpandaman/s3s: https://github.com/frozenpandaman/s3s
- frozenpandaman/splatnet2statink: https://github.com/frozenpandaman/splatnet2statink

