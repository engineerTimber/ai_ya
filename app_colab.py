import google.generativeai as genai
import pyimgur
from flask import Flask, request, abort, send_from_directory
import os
from health_gemini import AI_response, analyze_image_from_url
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TemplateMessage, 
    ConfirmTemplate, 
    ButtonsTemplate, 
    CarouselColumn, 
    CarouselTemplate, 
    ImageCarouselColumn, 
    ImageCarouselTemplate, 
    MessageAction, 
    URIAction, 
    PostbackAction, 
    DatetimePickerAction, 
    TextMessage,
    ImageMessage,
    TemplateMessage, 
    ButtonsTemplate, 
    PostbackAction, 
    MessagingApiBlob
)


from linebot.v3.webhooks import (
    MessageEvent,
    PostbackEvent, 
    TextMessageContent,
    ImageMessageContent
)

pic_saved_times={
    "temp":0, 
    "pressure":0, 
    "glucose":0
}
mode = "chat"
# #init()
# # 設定 Gemini API Key（請填入你的 Key）
# API_KEY = "AIzaSyBXsSAGWzwahc4g8V-pxMLTlcKTcilVf_E"
# genai.configure(api_key=API_KEY)

# # 建立 Gemini 模型
# model = genai.GenerativeModel("gemini-1.5-pro")
# image_url = "https://gw.alicdn.com/imgextra/i4/2697170250/O1CN01ZrPpnV1DiY1v7IzQB_!!4611686018427383114-2-item_pic.png_.webp"
# chat = model.start_chat()
def glucose_graph(client_id, imgpath):
	im = pyimgur.Imgur(client_id)
	upload_image = im.upload_image(imgpath, title="Uploaded with PyImgur")
	return upload_image.link

app = Flask(__name__)
configuration = Configuration(access_token='PDk06iwqPcO0+ky00Kt6sMWX3QmktMI4GKM1GQLjxt5Y3KZ8fUaARp1SFE9cCqdSaEFaAoL0jKvSKOc91p9SNfVVUFUY3zMu+aQicuJYTERN0LLtdA9VaBg6iPAlSPOSV9viJ+nlkyC1EA2ZyJgD6AdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('8458e379374f6f522d4d080d32ba8fcf')
ngrok_url = "https://3429-140-113-136-212.ngrok-free.app"
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@handler.add(MessageEvent, message=TextMessageContent) #有文字訊息傳過來時
def message_text(event):
    text = event.message.text
    with ApiClient(configuration) as api_client:
        line_bot_api=MessagingApi(api_client)
        
        #buttons template
        if text == "AI醫生": #串接gemini、按鈕：三個模式
            buttons_template = ButtonsTemplate(
                thumbnailImageUrl='https://i.imgur.com/AUiYMhT.jpeg', 
                title='我可以為你做什麼嗎', 
                text='也可以直接回答喔!', 
                actions=[
                    PostbackAction(label='紀錄數值', data='data_record', displayText='紀錄數值'), 
                    PostbackAction(label='記錄生活', data='life_record', displayText='記錄生活'), 
                    PostbackAction(label='醫生我不舒服', data='IneedDoctor', displayText='請直接開啟對話框和ai家醫師說話喔!'), 
                ]
            )
            template_message = TemplateMessage(
                alt_text = "this is a buttons template", 
                template=buttons_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token = event.reply_token, 
                    messages=[template_message]
                )
            )
        elif text == "健康數據": #改成圖表輪播(血壓、血糖...)
            #畫畫，得到三個連結(體溫、血壓、血糖)
            image_carousel_template = ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        imageUrl = 'https://i.imgur.com/Q08WMBx.png', 
                        action=URIAction(
                            label='您的體溫圖表', 
                            uri= 'https://docs.google.com/spreadsheets/d/1kyOvakRBRtJGJ8ckNVKqw9SjstWz7Vck_7MKamg1AQ4/edit?usp=sharing'
                        )
                    ), 
                    ImageCarouselColumn(
                        imageUrl = 'https://i.imgur.com/Q08WMBx.png', 
                        action=URIAction(
                            label='您的血糖圖表', 
                            uri= 'https://docs.google.com/spreadsheets/d/1kyOvakRBRtJGJ8ckNVKqw9SjstWz7Vck_7MKamg1AQ4/edit?usp=sharing'
                        )
                    ), 
                    ImageCarouselColumn(
                        imageUrl = 'https://i.imgur.com/Q08WMBx.png', 
                        action=URIAction(
                            label='綜合資訊', 
                            uri= 'https://docs.google.com/spreadsheets/d/1kyOvakRBRtJGJ8ckNVKqw9SjstWz7Vck_7MKamg1AQ4/edit?usp=sharing'
                        )
                    ), 
                    ImageCarouselColumn(
                        imageUrl = 'https://imgur.com/a/3ZbAutF', 
                        action=URIAction(
                            label='國人慢性病比率', 
                            uri='https://www.hpa.gov.tw/4705/16550/n'
                        )
                    )
                ]
            )
            image_carousel_message=TemplateMessage(
                alt_text='圖片輪播範本', 
                template=image_carousel_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token = event.reply_token, 
                    messages=[image_carousel_message]
                )
            )
        
        elif text == "提醒": #製作鬧鐘、做可以自動提醒的，不了，因為LINE NOTIFY要被關掉了，也沒有錢錢買PUSH功能
            confirm_template = ConfirmTemplate(
                text = "你今天吃藥了嗎~",
                actions=[
                    PostbackAction(label='吃藥了！', data='drug_eatten', displayText='我超棒!!!'),  #可能gemini可以給鼓勵？
                    #PostbackAction(label='否', data='10min_drug_reminder', displayText='十分鐘後提醒我'), #設計程式十分鐘後提醒
                    DatetimePickerAction(label="再提醒我", data="drug_reminder", mode="time")
                         ]
            )
            template_message=  TemplateMessage(
                alt_text='confirm alt text', 
                template=confirm_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token, 
                    messages=[template_message]
                )
            )
        elif text == "record":
            temp_time.append("23:00")
            temp_data.append(36.2)

        else:
            AI_text = AI_response(mode=mode, text=event.message.text)

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=AI_text)]
                )
            )
        

@handler.add(MessageEvent, message=ImageMessageContent) #如果使用者傳的訊息是圖片的話->改成叫gemini辨識
def handle_image_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api=MessagingApi(api_client)
        blob_api = MessagingApiBlob(api_client)

        message_content=blob_api.get_message_content(event.message.id)
        local_save = './static/' + event.message.id + '.png'
        # 確保 'static' 目錄存在
        if not os.path.exists("static"):
            os.makedirs("static")

        with open(local_save, 'wb') as fd:
            fd.write(message_content)

        img_url = glucose_graph('e66a891867741a6',local_save)
        text = analyze_image_from_url(img_url)
        print(text)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=text)] #event.message.text:聊天室傳來的文字
                )
            )


        #連接AI判別該圖形的類別 網址：img_url



@handler.add(PostbackEvent) #按鈕發送訊息!
def handle_postback(event):
    with ApiClient(configuration) as api_client:
        line_bot_api=MessagingApi(api_client)
        data = event.postback.data
        if data == 'drug_eatten':
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="哇!你真棒~只有自己能治癒自己的身體，除了你以外誰都不行!\n請繼續保持喔!!!")]
                )
            )
        elif data == "drug_reminder":
            selectied_time=event.postback.params['time']
            reply_text = f"好的，我會在{selectied_time}提醒您吃藥"
            #TODO 在github action 的指定時間提醒吃藥(目前先不用做)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)]
                )
            )
        elif data == "data_record":
            mode = "record_info"
            print(f"mode={mode}")
        elif data == "life_record":
            mode = "record_life"
            print(f"mode={mode}")
        elif data == "IneedDoctor":
            mode = "chat"
            print(f"mode={mode}")
        #gemini!!!

if __name__ == "__main__":
    app.run(debug = True) 

    #把debug關掉可以防止訊息主動傳兩遍