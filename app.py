# 導入所需的模組
from flask import Flask, request, abort  # Flask是用來建立網頁伺服器的框架，request處理HTTP請求，abort用於中止請求
from linebot import LineBotApi, WebhookHandler  # LINE Bot的核心模組，LineBotApi用於發送訊息，WebhookHandler用於處理Webhook事件
from linebot.exceptions import InvalidSignatureError  # 用於處理LINE簽名驗證失敗的例外
from linebot.models import MessageEvent, TextMessage, TextSendMessage  # LINE訊息相關的模型，處理事件和訊息類型
import yfinance as yf  # Yahoo Finance模組，用於抓取股票資料

# 建立Flask應用實例
app = Flask(__name__)  # __name__是Python內建變數，表示當前模組名稱，用於初始化Flask

# 初始化LINE Bot的API和Webhook處理器
# 填入你的Channel Access Token和Channel Secret，這兩個值從LINE Developers取得
line_bot_api = LineBotApi('bP4+qoMkxVBTp/frpIaE4G1u4mvsPXWgyNIUJuIwdBqP8wHwZHTdEG64EYzgu0boK6ru/zS2n6ACBPp7XIUxlxSUHDrDfZmT2fQRHXhiLnonhByqaPilVH5ejhV2647pAZDg75xeH0mVIbN4Tkd6dQdB04t89/1O/w1cDnyilFU=')  # 用於與LINE伺服器通訊的API物件
handler = WebhookHandler('7bf4becaf162f5e885ab92d0afa53630')  # 用於驗證Webhook請求的處理器

# 定義首頁路由（測試用）
@app.route('/')  # 當用戶訪問根路徑（例如 http://localhost:5000/）時觸發
def home():
    return 'LINE Bot is running!'  # 回傳簡單訊息，確認伺服器運行正常

# 定義Webhook路由，接收LINE發來的訊息
@app.route('/callback', methods=['POST'])  # 設定路由為 /callback，只接受POST請求
def callback():
    # 從HTTP標頭中取得LINE的簽名，用於驗證請求來源
    signature = request.headers['X-Line-Signature']
    # 取得請求的原始內容（JSON格式），轉為文字
    body = request.get_data(as_text=True)
    
    # 嘗試處理Webhook請求
    try:
        handler.handle(body, signature)  # 用WebhookHandler驗證簽名並處理訊息
    except InvalidSignatureError:  # 如果簽名驗證失敗（可能是偽造請求）
        abort(400)  # 回傳400錯誤，終止請求
    return 'OK'  # 處理成功，回傳'OK'告訴LINE伺服器已收到訊息

# 處理用戶發來的文字訊息
@handler.add(MessageEvent, message=TextMessage)  # 當收到MessageEvent且訊息類型為TextMessage時觸發
def handle_message(event):
    # 從事件中提取用戶輸入的文字訊息（例如股票代碼）
    user_message = event.message.text

    # 使用yfinance抓取股票資料
    try:
        stock = yf.Ticker(user_message)  # 根據用戶輸入的股票代碼（例如2330.TW）創建股票物件
        stock_info = stock.history(period='1d')  # 抓取該股票當日的歷史資料
        if not stock_info.empty:  # 檢查是否成功取得資料
            close_price = stock_info['Close'].iloc[-1]  # 從資料中提取最新的收盤價
            # 格式化回應訊息，顯示股票代碼和收盤價（保留兩位小數）
            reply = f"{user_message} 今日收盤價: {close_price:.2f}"
        else:
            reply = "無法找到該股票資料，請檢查股票代碼！"  # 如果沒有資料，回傳錯誤訊息
    except Exception as e:  # 處理任何抓取資料時的錯誤（例如代碼格式錯誤）
        reply = "輸入格式錯誤，請輸入正確的股票代碼（例如：2330.TW）"  # 提示用戶輸入正確格式

    # 透過LINE API回傳訊息給用戶
    line_bot_api.reply_message(
        event.reply_token,  # reply_token是LINE提供的一次性token，用於回覆特定訊息
        TextSendMessage(text=reply)  # 創建文字訊息物件，內容為reply
    )

# 主程式入口
if __name__ == "__main__":  # 確保這段程式碼只在直接運行此檔案時執行（而不是作為模組導入時）
    app.run(host='0.0.0.0', port=5000)  # 啟動Flask伺服器，監聽所有IP（0.0.0.0），使用埠5000