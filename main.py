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

app = Flask(__name__)

line_bot_api = LineBotApi(config.ACCESS_TOKEN)
handler = WebhookHandler(config.CHANNEL_SECRET)

JST = timezone(timedelta(hours=+9), 'JST')
today = datetime.now(JST)           # そのままだと9時間の時差があるため修正する

days = {"Sun":"日","Mon":"月","Tue":"火","Wed":"水","Thu":"木","Fri":"金","Sat":"土"}       # 英語で曜日が渡されてくるため辞書を用いて日本語に変換する
ack_list = ["完了","やり直し"]                                              # 以下conf_listまではクイックリプライ機能のボタンを使用する際に用いられるパラメータ
contact_list = ["休み","遅刻","大会"]
reason_list = ["体調不良","家庭都合","怪我","その他"]
time_list = ["５〜１０分ほど","１０〜１５分ほど","１５〜２０分ほど","２０分以上"]
name_list = []
select_list = []
remarks_list = ["なし"]
conf_list = ["はい","いいえ"]
children = ""

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

    return 'OK'

@handler.add(FollowEvent)           # 友達追加時に発火
def handle_follow(event):
    UserID = event.source.user_id
    line_bot_api.reply_message(event.reply_token,
		[
			TextSendMessage(text="minatoJBSC【公式】です。\n友達追加ありがとうございます!!"),
			TextSendMessage(text="まず初めにお子さんの名前（１人）をフルネームで入力してください。")
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
    if (status == "登録中"):        # 子供の名前を登録する
        if(len(text) > 0) and (text != "完了") and (text != "やり直し"):
            name_list.append(text)
            items = [QuickReplyButton(action=MessageAction(label="%s" %(ack), text="%s" %(ack))) for ack in ack_list]
            messages = TextSendMessage(text="兄弟がいる場合は続けて送信してください\nお子さんの名前の入力が完了したら、「完了」のボタンを，間違えてしまった場合は「やり直し」を押してください。", quick_reply=QuickReply(items=items))
            line_bot_api.reply_message(event.reply_token, messages=messages)
        elif (text == "完了"):
            function.SetName(config.DB_URL,UserID,name_list)
            tmp = "人の指定"
            function.ChangeStatus(config.DB_URL,UserID,tmp)
            name_list.clear()
            # res = function.GetName(config.DB_URL,UserID)
            # for i in range(2):                # Pythonはタプルの値を書き換えるのはエラーが出るため，リストに追加し直す
            #     name_list.append((res[i]))
            # if (None in name_list):
            #     name_list.remove(None)
            # if (len(name_list) == 2):
            #     name_list.append("２人とも")
            # items = [QuickReplyButton(action=MessageAction(label="%s" %(name), text="%s" %(name))) for name in name_list]
            # line_bot_api.reply_message(event.reply_token,
			# 	[
			# 		TextSendMessage(text = '名前の登録が完了しました。ありがとうございます。'),
            #         TextSendMessage(text="連絡したいお子さんの名前を選択してください。", quick_reply=QuickReply(items=items))
            #     ]
			# )
        elif (text == "やり直し"):
            name_list.clear()
            line_bot_api.reply_message(event.reply_token,
		        [
                    TextSendMessage(text="名前の登録をやり直します。"),
			        TextSendMessage(text="まず初めにお子さんの名前（１人）をフルネームで教えてください。")
		        ]
	        )

    elif (status == "人の指定"):
        res = function.GetName(config.DB_URL,UserID)
        for i in range(2):                # Pythonはタプルの値を書き換えるのはエラーが出るため，リストに追加し直す
            name_list.append((res[i]))
        if (None in name_list):
            name_list.remove(None)
        if (len(name_list) == 2):
            name_list.append("２人とも")
        items = [QuickReplyButton(action=MessageAction(label="%s" %(name), text="%s" %(name))) for name in name_list]
        line_bot_api.reply_message(event.reply_token,
			[
                TextSendMessage(text="連絡したいお子さんの名前を選択してください。", quick_reply=QuickReply(items=items))
            ]
		)

    elif (status == "連絡待ち"):            # 誰に対する連絡なのかを尋ねる
        global children
        if (text == "２人とも"):
            name_list.remove("２人とも")
            tmp = "連絡内容"
            function.ChangeStatus(config.DB_URL,UserID,tmp)
            for i in name_list:
                children += i + " "
            items = [QuickReplyButton(action=MessageAction(label="%s" %(contact), text="%s" %(contact))) for contact in contact_list]
            line_bot_api.reply_message(event.reply_token,
				[
                    TextSendMessage(text="連絡したい内容を以下から選択してください。", quick_reply=QuickReply(items=items))
				]
			)
        else:
            children += text
            tmp = "連絡内容"
            function.ChangeStatus(config.DB_URL,UserID,tmp)
            items = [QuickReplyButton(action=MessageAction(label="%s" %(contact), text="%s" %(contact))) for contact in contact_list]
            line_bot_api.reply_message(event.reply_token,
				[
                    TextSendMessage(text="連絡したい内容を以下から選択してください。", quick_reply=QuickReply(items=items))
				]
			)

    elif (status == "連絡内容"):            # なんの連絡かを待っている
        if (text =="休み"):
            function.ChangeContent(config.DB_URL,UserID,text)
            tmp = "名前"
            function.ChangeStatus(config.DB_URL,UserID,tmp)
            items = [QuickReplyButton(action=MessageAction(label="%s" %(reason), text="%s" %(reason))) for reason in reason_list]
            line_bot_api.reply_message(event.reply_token,
				[
					TextSendMessage(text='お休みですね。\n理由を以下から選択して下さい。\n「家庭都合」、「体調不良」、「怪我」、「その他」')
				]
            )
        elif (text =="遅刻"):
            function.ChangeContent(config.DB_URL,UserID,text)
            tmp = "名前"
            function.ChangeStatus(config.DB_URL,UserID,tmp)
            items = [QuickReplyButton(action=MessageAction(label="%s" %(time), text="%s" %(time))) for time in time_list]
            line_bot_api.reply_message(event.reply_token,
				[
					TextSendMessage(text='遅刻ですね。\nどれくらい遅れそうか以下から選択して下さい。')
				]
			)
        elif (text == "大会連絡"):
            function.ChangeContent(config.DB_URL,UserID,text)
        else:
            line_bot_api.reply_message(event.reply_token,
				[
					TextSendMessage(text='申し訳ありませんその言葉は理解しかねます。\n「休み」もしくは「遅刻」と送信して下さい。')
				]
			)

    # elif (status == "休み"):            # 休みの場合
    #     function.ChangeReason(config.DB_URL,UserID,text)
    #     tmp = "名前"
    #     function.ChangeStatus(config.DB_URL,UserID,tmp)
    #     line_bot_api.reply_message(event.reply_token,
	# 	    [
	# 			TextSendMessage(text='了解しました。\nお子さんの名前をフルネームで送信して下さい。')
	# 		]
	# 	)

    # elif (status == "遅刻"):            # 遅刻の場合
    #     function.ChangeReason(config.DB_URL,UserID,text)
    #     tmp = "名前"
    #     function.ChangeStatus(config.DB_URL,UserID,tmp)
    #     line_bot_api.reply_message(event.reply_token,
	# 	    [
	# 			TextSendMessage(text='了解しました。\nお子さんの名前をフルネームで送信して下さい。')
	# 		]
	# 	)

    elif (status == "名前"):            # 名前を聞く
        # function.ChangeName(config.DB_URL,UserID,text)
        tmp = "補足"
        function.ChangeStatus(config.DB_URL,UserID,tmp)
        items = [QuickReplyButton(action=MessageAction(label="%s" %(remarks), text="%s" %(remarks))) for remarks in remarks_list]
        line_bot_api.reply_message(event.reply_token,
			[
				TextSendMessage(text='その他補足事項等があれば入力し送信して下さい。\n特になければなしを選択して下さい。')
			]
		)

    elif (status == "補足"):            # 補足事項があれば記入してもらう
        function.ChangeRemarks(config.DB_URL,UserID,text)
        tmp = "最終確認"
        function.ChangeStatus(config.DB_URL,UserID,tmp)
        res = function.CheckInfo(config.DB_URL,UserID)
        we = days[today.strftime("%a")]
        items = [QuickReplyButton(action=MessageAction(label="%s" %(conf), text="%s" %(conf))) for conf in conf_list]
        line_bot_api.reply_message(event.reply_token,
			[
				TextSendMessage(text="%d/%d(%s)\n%s\n%s:%s\n%s" %(today.month,today.day,we,res[4],res[2],res[3],res[5])),
				TextSendMessage(text="上記で登録します。よろしければ「はい」を、訂正がある場合は「いいえ」を送信して下さい。")
			]
		)

    elif (status == "最終確認"):
        if (text == "はい"):            # 登録内容に間違いがなければ監督へ送信
            tmp = "連絡待ち"
            function.ChangeStatus(config.DB_URL,UserID,tmp)
            line_bot_api.reply_message(event.reply_token,
				[
					TextSendMessage(text='連絡を受け付けました。ありがとうございました。'),
                    TextSendMessage(text="連絡したいお子さんの名前を選択してください。", quick_reply=QuickReply(items=items))
				]
			)
        elif (text == "いいえ"):        # 登録内容に間違いがあれば．．．ごめんなさい始めからです．
            tmp = "連絡待ち"
            function.ChangeStatus(config.DB_URL,UserID,tmp)
            line_bot_api.reply_message(event.reply_token,
				[
					TextSendMessage(text = 'お手数ですが初めからやり直して下さい。'),
                    TextSendMessage(text="連絡したいお子さんの名前を選択してください。", quick_reply=QuickReply(items=items))
				]
			)
        else:
            res = function.CheckInfo(config.DB_URL,UserID)
            we = days[today.strftime("%a")]
            line_bot_api.reply_message(event.reply_token,
			    [
				    TextSendMessage(text="%d/%d(%s)\n%s\n%s:%s\n%s" %(today.month,today.day,we,children,res[2],res[3],res[5])),
				    TextSendMessage(text="上記で登録します。よろしければ「はい」を、訂正がある場合は「いいえ」を送信して下さい。")
			    ]
		    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))            # Heroku側が空いたポートを探してくれる 固定ポートにするとアプリ落ちる
    app.run(host="0.0.0.0", port=port)