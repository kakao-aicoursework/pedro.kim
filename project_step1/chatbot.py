import openai

class ChatbotSession:
    def __init__(
        self,
        chatbot,
        system_prompt,
        user_prompt=None,
        gpt_model=None,
        temperature=None,
        functions=None,
        function_call="auto"
    ):
        if gpt_model is None:
            raise TypeError("gpt_model cannot be None")
        self.chatbot = chatbot
        self.gpt_model = gpt_model
        self.temperature = temperature
        self.functions = functions
        self.function_call = function_call
        self.conversations = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
        if user_prompt is not None and isinstance(user_prompt, str):
            self.conversations.append({
                "role": "user",
                "content": user_prompt
            })

    def respond_to_user_dialogue(self, user_dialogue):
        self.conversations.append({
            "role": "user",
            "content": user_dialogue
        })
        argument_map = {}
        if self.temperature is not None:
            argument_map["temperature"] = self.temperature
        if self.functions is not None:
            argument_map["functions"] = self.functions
            if self.function_call is not None:
                argument_map["function_call"] = self.function_call
        response = openai.ChatCompletion.create(
            model=self.gpt_model,
            messages=self.conversations,
            **argument_map
        )
        if response.choices[0].message.content:
            self.conversations.append({
                "role": "assistant",
                "content": response.choices[0].message.content
            })
        # TODO: add support for function calls
        return response

class Chatbot:
    DEFAULT_GPT_MODEL = "gpt-3.5-turbo"
    DEFAULT_TEMPERATURE = 0.1

    def __init__(self, system_prompt, functions=None):
        self.system_prompt = system_prompt
        self.sessions = []
        self.functions = functions

    def create_session(
        self,
        user_prompt=None,
        gpt_model=None,
        temperature=None
    ):
        if gpt_model is None:
            gpt_model = self.DEFAULT_GPT_MODEL
        if temperature is None:
            temperature = self.DEFAULT_TEMPERATURE
        session = ChatbotSession(
            self,
            self.system_prompt,
            user_prompt,
            gpt_model,
            temperature
        )
        self.sessions.append(session)
        return session
