import json
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
        if self.functions:
            functions_trimmed = []
            for d in self.functions:
                d_copy = d.copy()
                for k in list(d_copy.keys()):
                    if k.startswith("_"):
                        d_copy.pop(k)
                functions_trimmed.append(d_copy)
            argument_map["functions"] = functions_trimmed
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
        elif response.choices[0].message.function_call:
            call_info = response.choices[0].message.function_call.to_dict()
            for d in self.functions:
                if d["name"] == call_info["name"]:
                    response = d["_actual_function"](user_dialogue, **json.loads(call_info["arguments"]))
                    break
            self.conversations.append({
                "role": "assistant",
                "content": response.choices[0].message.content
            })
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
            temperature,
            self.functions
        )
        self.sessions.append(session)
        return session
