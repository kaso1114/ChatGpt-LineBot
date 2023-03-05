import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
PROMPT = f'You are a helpful assistant. 你用繁體中文回答'

class ChatGPT:
    def __init__(self) -> None:
        self.messages = []
        self.model = os.getenv("OPENAI_MODEL", default = "gpt-3.5-turbo")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", default = 1))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", default = 2048))

        self.max_user_msg = 4
        self.last_prompt_tokens = 0
        self.last_completion_tokens = 0
        self.last_total_tokens = 0
        self.reset_msg()

    def reset_msg(self):
        self.messages = [{'role': 'system', 'content': PROMPT}]

    def add_msg(self, text):
        if (len(self.messages)-1)/2 >= self.max_user_msg:
            self.messages.pop()     # pop assistant
            self.messages.pop()     # pop user
        self.messages.append({'role': 'user', 'content': text})

    def get_response(self):
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        # Get content
        content = response["choices"][0]["message"]["content"]
        self.messages.append({'role': 'assistant', 'content': content})

        # Get token
        self.last_prompt_tokens = response["usage"]["prompt_tokens"]
        self.last_completion_tokens = response["usage"]["completion_tokens"]
        self.last_total_tokens = response["usage"]["total_tokens"]
        return content
