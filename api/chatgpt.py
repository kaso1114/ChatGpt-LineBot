import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

PROMPT = f'you are assistant, a helpful assistant'

class ChatGPT:
    def __init__(self) -> None:
        self.model = os.getenv("OPENAI_MODEL", default = "gpt-3.5-turbo")
        self.messages = []
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", default = 0.7))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", default = 1024))
        # self.frequency_penalty = float(os.getenv("OPENAI_FREQUENCY_PENALTY", default = 2.0))
        # self.presence_penalty = float(os.getenv("OPENAI_PRESENCE_PENALTY", default = 0.0))

        self.max_user_msg = 6
        self.reset_msg()

    def reset_msg(self):
        self.messages = [{'role': 'system', 'content': PROMPT}]

    def add_msg(self, text):
        self.messages.append({'role': 'user', 'content': text})

    def get_response(self):
        if (len(self.messages)-1)/2 >= self.max_user_msg:
            self.messages.pop()     # pop assistant
            self.messages.pop()     # pop user
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            # top_p=0.6,
            # frequency_penalty=2.0,  # 降低出现频繁的单词的权重
            # presence_penalty=0.0,  # 降低不常出现的单词的权重
        )
        content = response["choices"][0]["message"]["content"]
        self.messages.append({'role': 'assistant', 'content': content})
        return content
