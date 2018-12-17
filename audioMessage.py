from linebot import LineBotApi
from linebot.models import *
import requests


from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.cloud import storage

import pydub

import datetime

channel_access_token = '*****'
line_bot_api = LineBotApi(channel_access_token)


def create_message(userId, messageId, postedDatetime):
    # 音声ファイルをLINE側から取得
    message_content = line_bot_api.get_message_content(messageId)
    with open('./audio/'+messageId+'.m4a', 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    # m4aをwavに変換（要: ffmpeg）
    sound = pydub.AudioSegment.from_file('./audio/'+messageId+'.m4a', "m4a")
    sound.export('./audio/'+messageId+'.wav', format="wav")


    # 音声ファイルをCloud Storageに保存
    bucket_name = 'casual-diary-audio'
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    new_blob = bucket.blob(messageId+'.wav')
    new_blob.upload_from_filename('./audio/'+messageId+'.wav')
    audio_url = 'gs://casual-diary-audio/' + messageId+'.wav'
    audio_url_from_https = 'https://storage.googleapis.com/***buget_name***/' + messageId+'.wav'


    # Speech To Textをする
    client = speech.SpeechClient()
    audio = types.RecognitionAudio(uri=audio_url)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
        language_code='ja-JP'
    )
    response = client.recognize(config, audio)
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    ans = ''
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        ans = ans + result.alternatives[0].transcript + '\n'
    ans = ans.rstrip('\n')


    # サーバへPOST
    # todo
    today = datetime.datetime.fromtimestamp(postedDatetime / 1000).strftime("%b %d %H:%M:%S %Y GMT")
    year = int(datetime.datetime.fromtimestamp(postedDatetime / 1000).strftime("%Y"))
    month = int(datetime.datetime.fromtimestamp(postedDatetime / 1000).strftime("%m"))
    day = int(datetime.datetime.fromtimestamp(postedDatetime / 1000).strftime("%d"))
    youbi = datetime.datetime.fromtimestamp(postedDatetime / 1000).strftime("%a")
    datetime.datetime.fromtimestamp(postedDatetime / 1000).strftime("%b %d %H:%M:%S %Y GMT")

    data = {
        'userid': userId,
        'path': audio_url_from_https,
        'year': year,
        'month': month,
        'day': day,
        'article': ans
    }
    response = requests.post('**database-endpoint-uri***', data=data)


    # Flex Msg
    if len(ans) is not 0:
        bubble = BubbleContainer(
            type="bubble",
            body=BoxComponent(
                type="box",
                layout='vertical',
                contents=[
                    TextComponent(type="text", text=str(year)+'/'+str(month)+'/'+str(day)+' '+youbi+'.', weight="bold", color="#1DB446", size="sm"),
                    TextComponent(type="text", text="日記を登録しました👍", weight="bold", margin="md"),
                    TextComponent(type="text", text="修正が必要な場合は、\n下のボタンから修正してください", size="xs", color="#aaaaaa", wrap=True, margin="md"),
                    SeparatorComponent(margin="md"),
                    TextComponent(type="text", text=ans, wrap=True, margin="md"),
                    SeparatorComponent(margin="md")
                ]
            ),
            footer=BoxComponent(
                type="box",
                layout="vertical",
                contents=[
                    ButtonComponent(type="button", style="link", height="sm",
                                    action=URIAction(type="uri", label="修正する", uri="*****")),
                    SpacerComponent(type="spacer", size="sm")
                ]
            )
        )
        ans_alt_text = "日記を登録しました👍\n\n"+ans
        message = FlexSendMessage(alt_text=ans_alt_text, contents=bubble)
        return message
    else:
        message = TextSendMessage(text="ごめんね... うまく認識できなかったみたい...\nもう一回、試してくれないかな？")
        return message
