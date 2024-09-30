import streamlit as st
from ask_llm import page_ask_llm # type: ignore

def init_page():
    st.set_page_config(
        page_title="HANREI",
        page_icon="👩‍⚖️"
    )

def main():
    init_page()

    selection = st.sidebar.radio("Menu", ["Ask LLM"])
    if selection == "Ask LLM":
        page_ask_llm()



if __name__ == '__main__':
    main()