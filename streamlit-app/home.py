import streamlit as st
from typing import List
import json
from ai_chatbot.llm.conversational import OpenAIConversationalLLM
from ai_chatbot.prompts.gpt_35_0125 import product_chatbot_prompt
from dotenv import load_dotenv


load_dotenv(override=True)


def load_products(product_path: str) -> List[str]:
    with open(product_path, "r") as fp:
        products = json.load(fp)
        products = [json.dumps(product) for product in products]
    return products


st.title("AI chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "model" not in st.session_state:
    model_config = {"model_name": "gpt-3.5-turbo-0125",
                    "temperature": 0.2,
                    "n_history": 3}
    model = OpenAIConversationalLLM(model_config=model_config, system_prompt=product_chatbot_prompt)
    st.session_state.model = model

if "products" not in st.session_state:
    product_data = load_products("data/products/product_list.txt")
    st.session_state.products = product_data[:3]


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("What is your question?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(user_input)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    response_stream = st.session_state.model.get_response(
        user_input=user_input,
        stream=True,
        **{"products": st.session_state.products})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in response_stream:
            full_response += chunk
            message_placeholder.markdown(full_response + "")
        message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

st.sidebar.title("About")
st.sidebar.info("This is a simple AI chatbot interface using Streamlit and OpenAI's GPT-3.5-turbo model "
                "for dibimbing.id AI chatbot course")
