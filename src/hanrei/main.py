import streamlit as st
from streamlit_navigation_bar import st_navbar # type: ignore

from home import page_home  # type: ignore
from ask_llm import page_ask_llm # type: ignore


def init_page():
    st.set_page_config(
        page_title="判例検索AI",
        page_icon="👩‍⚖️"
    )

def main():
    init_page()

    ## GitHub のリンク
    st.sidebar.page_link("https://github.com/YutoKz/HANREI/tree/develop", label="GitHub", icon="🐈️")

    page = st.sidebar.radio(
        "Navigation",
        ["Home", "Ask ChatGPT", "DataBase"]
    )

    if page == "Home":
        page_home()
    elif page == "Ask ChatGPT":
        page_ask_llm()
    #elif page == "DataBase":
        



if __name__ == '__main__':
    main()


#navigation bar を使った場合 (互換性に難ありと判断)
#
#def main():
#    #init_page()
#
#    # navigation bar
#    st.set_page_config(initial_sidebar_state="collapsed")
#
#    pages = ["Home", "Ask ChatGPT", "GitHub"]
#    urls = {"GitHub": "https://github.com/YutoKz/HANREI/tree/develop"}
#    logo_path = "./data/awl_white.svg"
#    styles = {
#        "nav": {
#            "background-color": "black",
#            "justify-content": "center",
#        },
#        "img": {
#            "padding-right": "14px",
#        },
#        "span": {
#            "color": "white",
#            "padding": "14px",
#            "family-font": "Arial",
#        },
#        "active": {
#            "background-color": "gray",
#            "color": "var(--text-color)",
#            "font-weight": "normal",
#            "padding": "14px",
#        }
#    }
#    options = {
#        "show_sidebar": False,
#    }
#
#    page = st_navbar(
#        pages,
#        logo_path=logo_path,
#        urls=urls,
#        styles=styles,
#        options=options,    # type: ignore
#    )
#
#    functions = {   # type: ignore
#        "Home": page_home,
#        "Ask ChatGPT": page_ask_llm,
#    }
#    go_to = functions.get(page)     # type: ignore
#    if go_to:
#        go_to()
#