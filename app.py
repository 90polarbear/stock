
   
# 導入所需模組
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import yfinance as yf
import os

# 建立Flask應用實例
app = Flask(__name__)

# 從環境變數中讀取LINE的Token和Secret
line_bot_api = LineBotApi('bP4+qoMkxVBTp/frpIaE4G1u4mvsPXWgyNIUJuIwdBqP8wHwZHTdEG64EYzgu0boK6ru/zS2n6ACBPp7XIUxlxSUHDrDfZmT2fQRHXhiLnonhByqaPilVH5ejhV2647pAZDg75xeH0mVIbN4Tkd6dQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('7bf4becaf162f5e885ab92d0afa53630')

# 首頁路由（測試用）
@app.route('/')
def home():
    return 'Taiwan Stock LINE Bot is running!'

# Webhook路由，接收LINE訊息
@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理用戶文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()  # 取得用戶輸入並去除多餘空格

    # 如果用戶輸入的是數字，自動加上 .TW 後綴（台灣股票代碼格式）
    if user_message.isdigit():
        stock_code = f"{user_message}.TW"
    else:
        stock_code = user_message  # 否則直接使用用戶輸入（允許手動輸入完整代碼）

    # 使用yfinance抓取股票資料
    try:
        stock = yf.Ticker(stock_code)
        stock_info = stock.history(period='1d')  # 抓取當日資料
        if not stock_info.empty:
            close_price = stock_info['Close'].iloc[-1]  # 最新收盤價
            open_price = stock_info['Open'].iloc[-1]   # 開盤價
            high_price = stock_info['High'].iloc[-1]   # 最高價
            low_price = stock_info['Low'].iloc[-1]     # 最低價
            # 格式化回應訊息，提供更豐富的資訊
            reply = (
                f"股票代碼: {stock_code}\n"
                f"今日收盤價: {close_price:.2f} 元\n"
                f"開盤價: {open_price:.2f} 元\n"
                f"最高價: {high_price:.2f} 元\n"
                f"最低價: {low_price:.2f} 元"
            )
        else:
            reply = f"找不到 {stock_code} 的股票資料，請確認代碼是否正確！"
    except Exception as e:
        reply = "輸入格式錯誤，請輸入台灣股票代碼（例如：2330 或 2330.TW）"

    # 回傳訊息給用戶
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

# 主程式入口
if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))  # Render動態埠號，預設5000
    app.run(host='0.0.0.0', port=port)