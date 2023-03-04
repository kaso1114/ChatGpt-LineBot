try:
    from api.chatgpt import ChatGPT     # For online
except:
    from chatgpt import ChatGPT     # For debug, sh run.sh

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, Sender
import os

VERSION = 'v1.2'
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFALUT_TALKING", default = "true").lower() == "true"
icon_url = "https://cdn.dribbble.com/userupload/3963239/file/original-87c1101f959e7c30f19c6fd0c4f5173a.png?compress=1&resize=752x"

app = Flask(__name__)
chatgpt = ChatGPT()

# domain root
@app.route('/')
def home():
    return VERSION

@app.route("/webhook", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global working_status

    if event.message.type != "text":
        return

    if event.message.text == "啟動":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"我是ChatGPT {VERSION} ，若不需要我，請說 「安靜」 謝謝~", sender=Sender("ChatGPT", icon_url=icon_url))
        )
        return

    if event.message.text == "安靜":
        working_status = False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="感謝使用ChatGPT，若需要我，請說 「啟動」 謝謝~", sender=Sender("ChatGPT", icon_url=icon_url))
        )
        chatgpt.reset_msg()
        return

    if working_status:
        chatgpt.add_msg(event.message.text)
        reply_msg = chatgpt.get_response()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_msg, sender=Sender("ChatGPT", icon_url=icon_url))
        )


if __name__ == "__main__":
    app.run()
