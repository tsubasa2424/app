import os
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify
import json

# LINEのアクセストークンとユーザーIDを設定
LINE_ACCESS_TOKEN = 'UH9/CGcVZt4bnQKn3DX72uPH1i6AC0uKxSEWa2divzG7kyK3MfkOl1kc2K7bKhbbw0oIWnAk2K+/Mq/GJIq6RcBKBCPK025VD0S7ZPazgxcEI+fbA/ceLzDWorMGUFUPyaAyB/voU2GTKn23KUw8gwdB04t89/1O/w1cDnyilFU='  # LINE Messaging APIのアクセストークン
LINE_USER_ID = 'U54ced3c74a481bf1a1c1700647a90f35'  # LINEユーザーID（個別に通知したい相手）

# 仮想通貨の価格情報
user_settings = {}  # ユーザー設定の格納場所（ユーザーID、通貨、価格）

# Flaskアプリケーションの設定
app = Flask(__name__)


# LINEに通知を送信する関数
def send_line_notify(message, user_id):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": "Bearer " + LINE_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.status_code


# 仮想通貨の現在の価格を取得する関数（ビットバンクAPIを使用）
def get_current_price(currency):
    url = f"https://public.bitbank.cc/{currency}_jpy/ticker"
    response = requests.get(url)
    data = response.json()
    if data["status"] == "success":
        return float(data["data"]["last"])
    else:
        return None


# ユーザーが通貨名と目標価格を設定するエンドポイント
@app.route("/set_price", methods=["POST"])
def set_price():
    data = request.json
    user_id = data.get("user_id")
    currency = data.get("currency")
    target_price = data.get("price")

    if user_id and currency and target_price:
        user_settings[user_id] = {"currency": currency, "price": target_price}
        return jsonify({"message": f"設定完了: {currency}の目標価格は{target_price}円です。"})
    else:
        return jsonify({"error": "無効なデータです。"})


# 価格が目標に達したかどうかをチェックする関数
def check_price():
    for user_id, settings in user_settings.items():
        currency = settings["currency"]
        target_price = settings["price"]

        # 定期的に価格をチェック
        current_price = get_current_price(currency)  # 実際にはAPIを使って価格を取得
        print(f"Current price of {currency}: {current_price}円")

        if current_price is None:
            print(f"{currency}の価格取得に失敗しました。")
            continue

        if current_price >= target_price:
            send_line_notify(f"【お知らせ】{currency}が目標価格に達しました！現在の価格は{current_price}円です。", user_id)
        else:
            print(f"{currency}の価格が目標価格に達していません。")


# 定期的に価格をチェックするためにスケジューラーを設定
def start_price_check():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_price, 'interval', seconds=60)  # 60秒ごとに価格チェック
    scheduler.start()


if __name__ == "__main__":
    start_price_check()  # 価格監視を開始
    app.run(debug=True, port=5000)
