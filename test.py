import google.generativeai as genai
import requests
from io import BytesIO
from PIL import Image
import json
from datetime import datetime

# 設定 Gemini API Key（請填入你的 Key）
API_KEY = ""
genai.configure(api_key=API_KEY)

# 建立 Gemini 模型
model = genai.GenerativeModel("gemini-1.5-pro")
image_url = "https://gw.alicdn.com/imgextra/i4/2697170250/O1CN01ZrPpnV1DiY1v7IzQB_!!4611686018427383114-2-item_pic.png_.webp"

mode = "photo"

# prompt在這裡面
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
        date的部分一律用:
        """
        response = model.generate_content(
            [prompt, time_now, image]
        )

        res = response.text
        dic_data = json.loads(res)

        '''
        for key, value in dic_data.items():
            print(f"{key}: {value}")
        print("\n")
        '''

        if (dic_data["type"] == "血壓"):
            print(f"收縮壓: {dic_data['systolic']}")
            print(f"舒張壓: {dic_data['diastolic']}")
            print(f"脈搏: {dic_data['pulse']}")
            print(f"時間: {dic_data['time']}")
            print(f"{dic_data['luv_from_ai']}")
        elif (dic_data["type"] == "血糖"):
            print(f"血糖: {dic_data['glucose']}")
            print(f"時間: {dic_data['time']}")
            print(f"{dic_data['luv_from_ai']}")
        elif (dic_data["type"] == "體溫"):
            print(f"體溫: {dic_data['temperature']}")
            print(f"時間: {dic_data['time']}")
            print(f"{dic_data['luv_from_ai']}")
        elif (dic_data["type"] == "血脂"):
            print(f"血脂: {dic_data['lipids']}")
            print(f"時間: {dic_data['time']}")
            print(f"{dic_data['luv_from_ai']}")
        

    except Exception as e:
        print(f"發生錯誤: {e}")

# 測試：輸入你的圖片網址

if mode == "photo":
    while True:
        image_url = input("\n請輸入圖片網址: ")
        if image_url == "bye":
            break
        analyze_image_from_url(image_url)
