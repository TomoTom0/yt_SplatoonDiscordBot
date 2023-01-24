# yt_SplatoonDiscordBot

Discord Bot on Python for Splatoon with s3s and stat.ink

[DiscordBot_Heroku_Stat.ink](https://github.com/TomoTom0/DiscordBot_Heroku_Stat.ink)の後継Repositoryです。

## Introduction

自分で使用しているDiscord BotのScriptを整理しました。
詳しい使い方や試験などは後々行います。

公開済みの[DiscordBot_Heroku_Stat.ink](https://github.com/TomoTom0/DiscordBot_Heroku_Stat.ink)が、仕様変更やSplatoon 2->3への移行およびそれに伴うs2s->s3sの移行へのため実用に耐えなくなったことを受け、このRepositoryを作成しました。

s3sを用いてstat.inkへ戦績のアップロードを行います。(optionとしてlocalへの保存、localからのuploadもできます。)

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


### 事前準備 (必須)
- **stat.ink** : アカウント作成、API KEYコピー
- **discord** : アカウント作成、開発者登録、Application作成、DISCORD BOT TOKENコピー、BOTのserverへの追加、BOTの設定編集
    - 参考 [Discord Botアカウント初期設定ガイド for Developer](https://qiita.com/1ntegrale9/items/cb285053f2fa5d0cccdf)のうち**はじめに~サーバーへの登録**

### Bot起動まで

`git clone`などでダウンロードし、`pip3 install -r requirements.txt`で必要なライブラリをインストールします。最後に`python3 src/main.py`でdiscord botを起動します。terminalにエラーメッセージが出なければ大丈夫です。`screen`や`nohup`などは必要に応じて利用してください。

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
|`?startIksm`|`STAT_INK_API_KEY`?| 新たにiksm_sessionを取得し、botにアカウントを登録します。 事前にstat.inkの登録を完了し、API KEYを取得しておいてください。引数が省略された場合、interactiveに入力が求められます。|
|`?checkIksm`|`acc_name`?|指定されたアカウントのiksm_sessionを表示します。引数が省略された場合、interactiveに入力が求められます。|
|`?rmIksm`|`acc_name`?|指定されたアカウントの情報を削除します。引数が省略された場合、interactiveに入力が求められます。|
|`?showIksm`|なし|登録されているnintendoアカウント一覧を表示します。|
|`?upIksm`|`acc_name`?|ただちに戦績チェックを行います。操作にはしばらく時間がかかります。`acc_name`が入力された場合、指定したアカウントのみ戦績チェックします。|
|`?upIksmFromLocal`|`acc_name`?|localの戦績をstat.inkにアップロードします。操作にはしばらく時間がかかります。`acc_name`が入力された場合、指定したアカウントのみ戦績チェックします。|

### Accessibility

**v1.2.1以降、新規登録されたNintendoアカウント情報へのアクセスに一定の制限を加えました。**
これは1つのBOTが複数のサーバーに加えられる状況を想定したものです。
既定の振る舞いは以下の表の通りです。

|`?startIksm`実行場所|アクセスが許可される場所|
|-|-|
|サーバー|登録されたサーバー、および登録したユーザーとのDM|
|DM|登録したユーザーとのDM|

アクセス権限のない場所においては、Discord Botとのコマンドにおいて当該アカウントは登録されていないものとして扱われます。
**v1.2.0以前に登録されていたNintendoアカウントについてはアクセスが無制限の状態です。**

アクセス制限の情報は`configs_s3s/access_permission.json`内で管理されています。テキストファイルとして修正することで反映されます。
`id`のリストとして`[-1]`が与えられた場合、その項目に関しては無制限となります。

|key|value|
|-|-|
|guild|サーバー(guild)のidのリスト|
|dm|discord userのidのリスト|
|author|discord botを通じてpermission_infoを編集できるuserのidのリスト (編集機能は未実装)|


## Future Works

Coming Soon...

## Botを自分好みに改造したくなったら
[Discord Bot 最速チュートリアル【Python&Heroku&GitHub】](https://qiita.com/1ntegrale9/items/aa4b373e8895273875a8#8-dynos%E3%81%AE%E8%A8%AD%E5%AE%9A)を参考にしてください。
(これだけでは不足していますが……)

botのupdateへの対応や既存のbotとの併用を便利にするため、main.pyに触れずともconfig.pyのみで独自の変更を加えられるようにしました。
本botが既定で対応していてかつ、config.pyで設定できる主な変数・関数は以下の通りです。もちろん、必要に応じた他の要素も追加可能です。
`ext_splat.py`などを参考に`Cog`も積極的に利用・追加してください。

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
|-|-|-|
|`DISCORD_TOKENS`|既定値割愛|`mode`ごとにDiscord bot tokenを使い分けたい場合のための辞書です|
|`mode`|`main`|`mode`に`main`が含まれる場合のみ戦績の定期チェックは行われます|
|`const_paths`|既定値割愛|各種ディレクトリやファイルのパスの辞書です|


## References

- frozenpandaman/s3s: https://github.com/frozenpandaman/s3s
- frozenpandaman/splatnet2statink: https://github.com/frozenpandaman/splatnet2statink

