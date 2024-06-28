from typing import Dict, Generator
from string import Template
from openai import OpenAI


class OpenAIConversationalLLM:
    def __init__(self,
                 model_config: Dict,
                 system_prompt: str | Template = ""):
        self.system_prompt = system_prompt
        self.model_config = model_config
        self.conversation_history = []
        self._client = OpenAIConversationalLLM._create_client()

    @classmethod
    def _create_client(cls):
        client = OpenAI()
        return client

    def modify_system_prompt(self, **kwargs) -> str:
        if isinstance(self.system_prompt, str):
            return self.system_prompt
        elif isinstance(self.system_prompt, Template):
            return self.system_prompt.substitute(**kwargs)

    def limit_conversation_history(self):
        n_history = self.model_config.get("n_history", 5)
        if (len(self.conversation_history)/2) > n_history:
            del self.conversation_history[:2]

    def get_response(self, user_input: str, stream: bool = False, **kwargs) -> str | Generator:
        system_prompt = self.modify_system_prompt(**kwargs)
        messages = ([{"role": "system", "content": system_prompt}]
                    + self.conversation_history
                    + [{"role": "user", "content": user_input}])

        response = self._client.chat.completions.create(
            model=self.model_config["model_name"],
            messages=messages,
            temperature=self.model_config["temperature"],
            stream=stream
        )
        if stream:
            def response_generator():
                full_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        yield content
                self.conversation_history.extend([
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": full_response}
                ])
                self.limit_conversation_history()

            return response_generator()

        else:
            content = response.choices[0].message.content
            self.conversation_history.extend([{"role": "user", "content": user_input},
                                              {"role": "assistant", "content": content}])
            self.limit_conversation_history()
            return content
