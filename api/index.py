try:
    from api.chatgpt import ChatGPT     # For online
except:
    from chatgpt import ChatGPT     # For debug, sh run.sh

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, Sender
import os

VERSION = 'v0.7'
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

    if event.message.text == "清除":
        working_status = True
        chatgpt.reset_msg()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"我是ChatGPT {VERSION}，已清除對話內容，若不需要我，請說「安靜」或「閉嘴」", sender=Sender(icon_url=icon_url))
        )
        return

    if event.message.text == "啟動":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"我是ChatGPT {VERSION}，只記近{chatgpt.max_user_msg}次對話，若不需要我，請說「安靜」或「閉嘴」", sender=Sender(icon_url=icon_url))
        )
        return

    if event.message.text == "安靜" or event.message.text == "閉嘴":
        working_status = False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"感謝使用ChatGPT {VERSION}，若需要我，請說「啟動」謝謝~", sender=Sender(con_url=icon_url))
        )
        chatgpt.reset_msg()
        return

    if working_status:
        chatgpt.add_msg(event.message.text)
        gpt_msg = chatgpt.get_response()
        text = gpt_msg + f"\n\nTokens: {chatgpt.last_total_tokens} ({chatgpt.last_prompt_tokens}+{chatgpt.last_completion_tokens})"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text, sender=Sender(icon_url=icon_url))
        )


if __name__ == "__main__":
    app.run()
