import streamlit as st


def page_home():
    st.title("HOME")

    # readmeの内容をここに表示できるように
    with open("README.md", "r", encoding="utf-8") as f:
        readme_text = f.read()

    splitted_readme_text = readme_text.split("## 開発", 1)


    tab_readme_overview, tab_readme_dev = st.tabs(["Overview", "Development"])

    with tab_readme_overview:
        st.markdown(splitted_readme_text[0], unsafe_allow_html=True)

    
    with tab_readme_dev:
        st.markdown("## 開発" + splitted_readme_text[1], unsafe_allow_html=True)


    