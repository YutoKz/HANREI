import json
import requests
from xml.etree import ElementTree
import re
import streamlit as st

def create_name_num_json():
    """
        法令名と法令番号の対応をjsonファイルに保存、辞書として扱えるように。
    """
    with open("./data/japanese-law-analysis/law/list.json", "r", encoding="utf-8") as f:
        original_json: list[dict] = json.load(f) # type: ignore
    
    name_num_dict = {}
    for data in original_json:                      # type: ignore
        name_num_dict[data["name"]] = data["num"]
    
    with open("./data/japanese-law-analysis/law/name_num.json", "w", encoding="utf-8") as file:
        json.dump(name_num_dict, file, ensure_ascii=False, indent=4)

# 参考：https://qiita.com/Lisphilar/items/39ad23ac7ade21313911
def get_num_from_name_keywords(keywords: list[str]) -> dict[str, str]:
    """
        keywordsに含まれる文字列を一つでも含む
        法令名と法令番号を取得
    """
    with open("./data/japanese-law-analysis/law/name_num.json", "r", encoding="utf-8") as file:
        name_num_dict = json.load(file)

    return {name: num for (name, num) in name_num_dict.items() if any(keyword in name for keyword in keywords)}

def get_num_from_name(name: str) -> str:
    with open("./data/japanese-law-analysis/law/name_num.json", "r", encoding="utf-8") as file:
        name_num_dict = json.load(file)
    
    if name in name_num_dict:
        return name_num_dict[name]
    else:
        return ""

def get_law_from_num(num: str):
    url = f"https://elaws.e-gov.go.jp/api/1/lawdata/{num}"
    r = requests.get(url)
    root = ElementTree.fromstring(r.content.decode(encoding="utf-8"))
    contents = [e.text.strip() for e in root.iter() if e.text]
    contents = [t for t in contents if t]
    contents = [s for s in contents if s.endswith("。")]
    gcp = "".join(contents)
    gcp = gcp.translate(str.maketrans({"「": "", "」": ""}))
    return re.sub("（[^（|^）]*）", "", gcp)

# ------------------------------------------------------------------------

def page_search_law():
    st.title("法令検索")
    st.markdown("e-Gov APIを利用して法令を検索します")

    if "law_name" not in st.session_state:
        st.session_state.law_name = ""

    st.session_state.law_name = st.text_input("法令名")
    if st.session_state.law_name:
        law_dict: dict[str, str] = get_num_from_name_keywords([st.session_state.law_name])
        if len(law_dict.items()) > 0:
            for i, (name, num) in enumerate(law_dict.items()):    # type: ignore
                with st.spinner("Retrieving law from API..."):    
                    if i >= 10:
                        break
                    with st.expander(f"{name}"):
                        law_contents = get_law_from_num(num)    # type: ignore
                        st.markdown(law_contents)   # type: ignore
        else:
            st.error("該当する法令が見つかりませんでした")



if __name__ == '__main__':
    #create_name_num_json()
    output = get_num_from_name("著作権法")
    print(output)
