from linebot.models import (
    TextSendMessage,
)
import random
import requests
import datetime
import json


def create_message(user_message, userId, postedDatetime):
    if user_message == "日記を話す！":
        today = datetime.datetime.fromtimestamp(postedDatetime / 1000).strftime("%b %d %H:%M:%S %Y GMT")
        year = int(datetime.datetime.fromtimestamp(postedDatetime / 1000).strftime("%Y"))
        month = int(datetime.datetime.fromtimestamp(postedDatetime / 1000).strftime("%m"))
        day = int(datetime.datetime.fromtimestamp(postedDatetime / 1000).strftime("%d"))
        youbi = datetime.datetime.fromtimestamp(postedDatetime / 1000).strftime("%a")
        datetime.datetime.fromtimestamp(postedDatetime / 1000).strftime("%b %d %H:%M:%S %Y GMT")

        data = {
            'userid': userId,
            'year': year,
            'month': month,
            'day': day
        }

        response = requests.post('***database-endpoint-url***', data=data)
        res = json.loads(response.text)
        if res['IsExist'] == False:
            # まだ今日の日記はない
            msg = "右下のマイクのアイコンから、日記の内容をおはなししてね"
            return TextSendMessage(text=msg)
        else:
            # すでに今日の日記がある
            msg = "今日の日記はすでに登録しているよ...？\n\n"+"もう一回登録するときは右下のマイクのアイコンから、日記の内容をおはなししてね"
            return TextSendMessage(text=msg)

    else:
        msgs = ["よくわからないﾋﾟｯ...", "もういっかい、確かめてほしいﾋﾟｯ..."]
        msg = random.choice(msgs)
        message = TextSendMessage(text=msg)

    return message
