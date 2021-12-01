#-*- cording: utf-8 -*-
from linebot.models import *

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
import function
import config
import os
from flask import Flask, render_template, g, request, abort
from datetime import datetime, timedelta, timezone
import pytz

app = Flask(__name__)

line_bot_api = LineBotApi(config.ACCESS_TOKEN)
handler = WebhookHandler(config.CHANNEL_SECRET)

JST = timezone(timedelta(hours=+9), 'JST')
today = datetime.now(JST)
print("----------")
print(today)
print("----------")

days = {"Sun":"日","Mon":"月","Tue":"火","Wed":"水","Thu":"木","Fri":"金","Sat":"土"}

def hello_world():
    return "HelloWorld!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

@handler.add(FollowEvent)
def handle_follow(event):           # 友達追加時に発火
    UserID = event.source.user_id
    line_bot_api.reply_message(event.reply_token,
		[
			TextSendMessage(text='minatoJBSC【公式】です。\n友達追加ありがとうございます!!'),
			TextSendMessage(text='これからは練習の休み、遅刻の連絡はこのアカウントからお願いします。'),
			TextSendMessage(text='本日の練習をお休みする場合は「休み」、遅れて参加の場合は「遅刻」と送信して下さい。')
		]
	)
    function.SQL_add(config.DB_URL,UserID)

@handler.add(UnfollowEvent)
def handle_unfollow(event):         # 友達削除時に発火
    UserID = event.source.user_id
    function.SQL_delete(config.DB_URL,UserID)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):          # メッセージが送信されてきたら発火，statusによって送信内容を変化させる
    UserID = event.source.user_id
    text = event.message.text
    status = function.CheckStatus(config.DB_URL,UserID)
    if (status == "連絡待ち"):
        if (text =="休み")or(text =="休")or(text =="やすみ"):
            function.ChangeContent(config.DB_URL,UserID,text)
            tmp = "休み"
            function.ChangeStatus(config.DB_URL,UserID,tmp)
            line_bot_api.reply_message(event.reply_token,
				[
					TextSendMessage(text='お休みですね。\n理由を選択して送信して下さい。\n「家庭都合」、「体調不良」、「怪我」、「その他」')
				]
            )
        elif (text =="遅刻")or(text =="遅")or(text =="ちこく"):
            function.ChangeContent(config.DB_URL,UserID,text)
            tmp = "遅刻"
            function.ChangeStatus(config.DB_URL,UserID,tmp)
            line_bot_api.reply_message(event.reply_token,
				[
					TextSendMessage(text='遅刻ですね。\nどれくらい遅れそうか送信して下さい。')
				]
			)
        else:
            line_bot_api.reply_message(event.reply_token,
				[
					TextSendMessage(text='申し訳ありませんその言葉は理解しかねます。\n「休み」もしくは「遅刻」と送信して下さい。')
				]
			)
    elif (status == "休み"):
        function.ChangeReason(config.DB_URL,UserID,text)
        tmp = "名前"
        function.ChangeStatus(config.DB_URL,UserID,tmp)
        line_bot_api.reply_message(event.reply_token,
		    [
				TextSendMessage(text='了解しました。\nお子さんの名前をフルネームで送信して下さい。')
			]
		)
    elif (status == "遅刻"):
        function.ChangeReason(config.DB_URL,UserID,text)
        tmp = "名前"
        function.ChangeStatus(config.DB_URL,UserID,tmp)
        line_bot_api.reply_message(event.reply_token,
		    [
				TextSendMessage(text='了解しました。\nお子さんの名前をフルネームで送信して下さい。')
			]
		)
    elif (status == "名前"):
        function.ChangeName(config.DB_URL,UserID,text)
        tmp = "補足"
        function.ChangeStatus(config.DB_URL,UserID,tmp)
        line_bot_api.reply_message(event.reply_token,
			[
				TextSendMessage(text='その他補足事項等があれば入力し送信して下さい。\n特になければ「なし」で送信して下さい。')
			]
		)
    elif (status == "補足"):
        function.ChangeRemarks(config.DB_URL,UserID,text)
        tmp = "最終確認"
        function.ChangeStatus(config.DB_URL,UserID,tmp)
        res = function.CheckInfo(config.DB_URL,UserID)
        we = days[today.strftime("%a")]
        line_bot_api.reply_message(event.reply_token,
			[
				TextSendMessage(text="%d/%d(%s)\n%s\n%s:%s\n%s" %(today.month,today.day,we,res[4],res[2],res[3],res[5])),
				TextSendMessage(text="上記で登録します。よろしければ「はい」を、訂正がある場合は「いいえ」を送信して下さい。")
			]
		)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)