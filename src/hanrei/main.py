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
    
    st.sidebar.markdown("##### プロンプト例")
    st.sidebar.markdown("- 保険金詐欺に関する判例にはどのようなものがありますか？")
    st.sidebar.markdown("- Youtubeに違法にアップロードされた動画を視聴してしまいました。私は罪に問われますか？心配です。")



if __name__ == '__main__':
    main()