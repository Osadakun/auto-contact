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

app = Flask(__name__)

line_bot_api = LineBotApi(config.ACCESS_TOKEN)
handler = WebhookHandler(config.CHANNEL_SECRET)

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
    print(type(status))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)