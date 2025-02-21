import google.generativeai as genai
import requests
from io import BytesIO
from PIL import Image
import json
from datetime import datetime

# 設定 Gemini API Key（請填入你的 Key）
API_KEY = "AIzaSyBXsSAGWzwahc4g8V-pxMLTlcKTcilVf_E"
genai.configure(api_key=API_KEY)

# 建立 Gemini 模型
model = genai.GenerativeModel("gemini-1.5-pro")
image_url = "https://gw.alicdn.com/imgextra/i4/2697170250/O1CN01ZrPpnV1DiY1v7IzQB_!!4611686018427383114-2-item_pic.png_.webp"

mode = "photo"  # 模式從這裡改 photo / record_info / record_life / chat

# prompt在函式裡面
def analyze_image_from_url(image_url):
    try:
        # 嘗試下載圖片
        response = requests.get(image_url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            print(f"無法下載圖片，HTTP 狀態碼: {response.status_code}")
            return
        
        # 嘗試開啟圖片
        image = Image.open(BytesIO(response.content))
        # image.show()

        # 發送請求給 Gemini API
        time_now = datetime.now().strftime("%H:%M")
        prompt = """
        請分析這張圖片的內容，判斷它屬於以下四種數據中的哪一種：
        1. 血壓 ( 收縮壓(mmHg)、舒張壓(mmHg)、脈搏(次/min) )
        2. 血糖 ( 血糖(mg/dL) )
        3. 體溫 ( 體溫(度C)、時間(YYYY-MM-DD, HH-MM) )
        4. 血脂 ( 血脂(mmol/L) )

        然後根據主題擷取相關的數值，並用長得像python字典格式的樣子輸出。例如：
        {
        "type": "血壓",
        "systolic": 120,
        "diastolic": 80,
        "pulse": 72,
        "time": "08:00"
        "luv_from_ai": "Some words of concern for patients..."
        }
        {
        "type": "血糖",
        "glucose": 120,
        "time": "08:00"
        "luv_from_ai": "Some words of concern for patients..."
        }
        {
        "type": "體溫",
        "temperature": 120,
        "time": "08:00"
        "luv_from_ai": "Some words of concern for patients..."
        }
        {
        "type": "血脂",
        "lipids": 120,
        "time": "08:00"
        "luv_from_ai": "Some words of concern for patients..."
        }
        回傳的 `type` 僅會是「血壓」、「血糖」、「體溫」或「血脂」中的一種，請不要用其他的格式回傳，也不要回傳其他的資訊。
        luv_from_ai是AI根據這個數據對病患的關心，可以是任何中文文字，語氣請友愛一點，像是一個關心病人的醫生一樣，如果情況正常也可以鼓勵、稱讚病患。
        請回傳純粹的文字，不要加上任何額外的說明文字，例如``` ``` 、 ```json``` 、 ```yaml``` 、 ```python``` 、 ```diff``` 、 ```up等等，
        time的部分千萬不要取用圖片裡面的時間，用我提供的時間:
        """
        response = model.generate_content(
            [prompt, "現在時間是：" + time_now, image]
        )

        res = response.text
        dic_data = json.loads(res)

        '''
        for key, value in dic_data.items():
            print(f"{key}: {value}")
        print("\n")
        '''

        if (dic_data["type"] == "血壓"):
            res = f"收縮壓: {dic_data['systolic']}\n舒張壓: {dic_data['diastolic']}\n脈搏: {dic_data['pulse']}\n時間: {dic_data['time']}\n{dic_data['luv_from_ai']}"
            return res
        elif (dic_data["type"] == "血糖"):
            res = f"血糖: {dic_data['glucose']}\n時間: {dic_data['time']}\n{dic_data['luv_from_ai']}"
            return res
        elif (dic_data["type"] == "體溫"):
            res = f"體溫: {dic_data['temperature']}\n時間: {dic_data['time']}\n{dic_data['luv_from_ai']}"
            return res
        elif (dic_data["type"] == "血脂"):
            res = f"血脂: {dic_data['lipids']}\n時間: {dic_data['time']}\n{dic_data['luv_from_ai']}"
            return res
        

    except Exception as e:
        print(f"發生錯誤: {e}")

def record_info():
    
    return 0

def record_life():
    chat = model.start_chat()
    prompt = """
        你是一個喜歡聽我我分享生活點滴的AI醫生，接下來我會傳給你一些訊息，
        請你在分析訊息後提供一段像是python字典格式的樣子回應。例如：
        {
            "title": "我剛剛吃了一頓豐盛的晚餐",
            "time": "08:00",
            "luv_from_ai": "Some words of concern for patients..."
        }
        title是這段訊息的主旨，不用照抄訊息，請陳述事實，
        例如訊息如果是「我剛剛吃了一頓豐盛的晚餐」，title就可以是「吃了晚餐」，
        luv_from_ai是你根據這段訊息提供的暖心回復，可以是任何中文文字。
        請回傳純粹的文字，不要加上任何額外的說明文字，例如``` ``` 、 ```json``` 、 ```yaml``` 、 ```python``` 、 ```diff``` 、 ```up等等，
        time的部分千萬不要取用圖片裡面的時間，用我提供的時間:
    """
    time_now = datetime.now().strftime("%H:%M")
    chat.send_message([prompt, "現在時間是：" + time_now])

    while True:
        user_msg = input("你: ")
        if user_msg == "bye":
            break
        response = chat.send_message([user_msg, time_now])
        dic_data = json.loads(response.text)
        res = f"好的，已記錄\n活動: {dic_data['title']}\n時間: {dic_data['time']}\n{dic_data['luv_from_ai']}"
        print(res)

def chat(UserInput):
    chat = model.start_chat()
    prompt = """
        你是一個喜歡跟我聊天的AI醫生，接下來我們來聊聊天吧!
    """
    chat.send_message(prompt)

    
    user_input = UserInput
    response = chat.send_message(user_input)
    res = f"{response.text}"
    return res


def AI_response(mode, text, image_url):
    if mode == "record_info":
        return record_info(text)
    elif mode == "record_life":
        return record_life(text)
    elif mode == "chat":
        return chat(text) 
