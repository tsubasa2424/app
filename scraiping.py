import requests
import time

# ビットバンクAPIのエンドポイント
bitbank_url_xlm = "https://public.bitbank.cc/xlm_jpy/ticker"
bitbank_url_flr = "https://public.bitbank.cc/flr_jpy/ticker"

# LINE Notifyのアクセストークン
line_notify_token = 'FfPPwLVNuDUxyjo7S3jM4luNLJ0v871aNtS0HPyeh4g'

# LINE NotifyのURL
line_notify_url = 'https://notify-api.line.me/api/notify'

# 価格変動を監視するための基準価格
previous_price_xlm = None
previous_price_flr = None

# 価格変動の閾値（0.0001%）
threshold = 10  # 10%を小数にした値

def get_price(api_url):
    """ビットバンクAPIから価格を取得する"""
    response = requests.get(api_url)
    data = response.json()
    return float(data['data']['last'])

def send_line_notify(message):
    """LINE Notifyにメッセージを送信する"""
    headers = {
        'Authorization': f'Bearer {line_notify_token}'
    }
    data = {
        'message': message
    }
    requests.post(line_notify_url, headers=headers, data=data)

def check_price():
    """XLMとFLRの価格をチェックし、変動があれば通知する"""
    global previous_price_xlm, previous_price_flr

    # XLMの価格取得
    xlm_price = get_price(bitbank_url_xlm)
    # FLRの価格取得
    flr_price = get_price(bitbank_url_flr)

    # 初回実行時にはprevious_priceがないので設定
    if previous_price_xlm is None:
        previous_price_xlm = xlm_price
    if previous_price_flr is None:
        previous_price_flr = flr_price

    # XLMの価格変動をチェック
    if abs(xlm_price - previous_price_xlm) / previous_price_xlm >= threshold:
        message = f"ステラルーメン（XLM）の価格が変動しました: {previous_price_xlm}円 -> {xlm_price}円"
        send_line_notify(message)
        previous_price_xlm = xlm_price

    # FLRの価格変動をチェック
    if abs(flr_price - previous_price_flr) / previous_price_flr >= threshold:
        message = f"フレア（FLR）の価格が変動しました: {previous_price_flr}円 -> {flr_price}円"
        send_line_notify(message)
        previous_price_flr = flr_price

# メインループで定期的に価格をチェック
while True:
    check_price()
    time.sleep(60)  # 60秒ごとにチェック
