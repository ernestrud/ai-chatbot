from typing import Dict
from string import Template
from openai import OpenAI


class OpenAIStatelessLLM:
    def __init__(self,
                 model_config: Dict,
                 system_prompt: str | Template = ""):
        self.system_prompt = system_prompt
        self.model_config = model_config
        self._client = OpenAIStatelessLLM._create_client()

    @classmethod
    def _create_client(cls):
        client = OpenAI()
        return client

    def modify_system_prompt(self, **kwargs) -> str:
        if isinstance(self.system_prompt, str):
            return self.system_prompt
        elif isinstance(self.system_prompt, Template):
            return self.system_prompt.substitute(**kwargs)

    def get_response(self, user_input: str, **kwargs) -> str:
        system_prompt = self.modify_system_prompt(**kwargs)
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}]
        response = self._client.chat.completions.create(
            model=self.model_config["model_name"],
            messages=messages,
            temperature=self.model_config["temperature"]).choices[0].message.content
        return response
