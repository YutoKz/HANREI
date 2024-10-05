import streamlit as st

from langchain.docstore.document import Document
from langchain_core.runnables import RunnablePassthrough # type: ignore
from langchain_core.output_parsers import StrOutputParser

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

from langchain_qdrant import QdrantVectorStore 
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from datetime import datetime
from prompts import prompts     # type: ignore
from law import get_num_from_name # type: ignore
from law import get_num_from_name_keywords # type: ignore
from law import get_law_from_num # type: ignore

import os


QDRANT_PATH = "./local_qdrant"
COLLECTION_NAME = "database"

def select_model():
        #model = st.sidebar.radio("Choose a model:", ("GPT-4o mini", "(GPT-3.5-turbo)"))
        #if model == "(GPT-3.5-turbo)":
        #    model_name = "gpt-3.5-turbo"
        #else:
        #    model_name = "gpt-4o-mini"
    model_name = "gpt-4o-mini"
    st.session_state.model_name = model_name

    return ChatOpenAI(temperature=0, model=model_name)

def load_local_qdrant(collection_name: str) -> QdrantVectorStore:
    #try:
    #    client = QdrantClient(path=QDRANT_PATH)
    #except Exception as e:
    #    st.error(f"Failed to load Qdrant: {e}")
    #    return None
    client = QdrantClient(path=QDRANT_PATH)

    # すべてのコレクション名を取得
    collections = client.get_collections().collections
    collection_names = [collection.name for collection in collections]

    # コレクションが存在しなければ作成
    if collection_name not in collection_names:
        # コレクションが存在しない場合、新しく作成します
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )
        print('collection created')

    return QdrantVectorStore(
        client=client,
        collection_name=collection_name, 
        embedding=OpenAIEmbeddings()
    )

def load_cloud_qdrant(collection_name: str) -> QdrantVectorStore:
    """
        Qdrant CloudのQdrantVectorStore を出力
    """
    client = QdrantClient(url="https://417591d1-d134-46ce-9255-1e11bb2bc5dc.europe-west3-0.gcp.cloud.qdrant.io:6333", api_key=os.getenv("QDRANT_API_KEY"), timeout=300)

    # すべてのコレクション名を取得
    collections = client.get_collections().collections
    collection_names = [collection.name for collection in collections]

    # コレクションが存在しなければ作成
    if collection_name not in collection_names:
        # コレクションが存在しない場合、新しく作成します
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )
        print('collection created')
    
    return QdrantVectorStore.from_existing_collection(
        embedding=OpenAIEmbeddings(),   # qdrant の 公式turorial ではembeddingsとなっているが間違い 
        collection_name=collection_name,
        url="https://417591d1-d134-46ce-9255-1e11bb2bc5dc.europe-west3-0.gcp.cloud.qdrant.io:6333",
        api_key=os.getenv("QDRANT_API_KEY"),   # 環境変数で与えればOK、と理解
        timeout=300,
    )

def format_docs(docs: list[Document]) -> str:   # 出力の型合ってる？
    return "\n\n".join(doc.page_content for doc in docs)

def nengou(nengou_alphabet: str) -> str:
    if nengou_alphabet == "Reiwa":
        return "令和"
    elif nengou_alphabet == "Heisei":
        return "平成"
    elif nengou_alphabet == "Shouwa":
        return "昭和"
    elif nengou_alphabet == "Taishou":
        return "大正"
    elif nengou_alphabet == "Meiji":
        return "明治"
    else:
        return ""

def nengou_to_year(nengou_alphabet: str, year: int) -> int:
    if nengou_alphabet == "Reiwa":
        return year + 2018
    elif nengou_alphabet == "Heisei":
        return year + 1988
    elif nengou_alphabet == "Shouwa":
        return year + 1925
    elif nengou_alphabet == "Taishou":
        return year + 1911
    elif nengou_alphabet == "Meiji":
        return year + 1867
    else:
        return year
    
def str_to_list(string: str) -> list[list[str]]:
    lines = string.strip().split("\n")
    result = [line.split(",") for line in lines]
    return [[item.strip() for item in line] for line in result]


# -----------------------------------------------------------------------------------------------------

def page_ask_llm():
    st.title("判例検索 AI")

    llm = select_model()

    try:
        qdrant = load_local_qdrant(COLLECTION_NAME)
    except Exception as e:
        st.error("ヒント：プロンプト入力時はクリックしたのち、処理が終わるまで待ってからAskボタンを押してください。")
        st.error(f"Failed to load Qdrant: {e}")
        qdrant = None


    tab_ask, tab_law = st.tabs(["Ask ChatGPT", "Search Law"])

    with tab_ask:
        st.markdown("### 質問")
        col_query, col_askButton = st.columns((10, 1), vertical_alignment="bottom")
        with col_query:
            query = st.text_area("ChatGPT へ質問：", key="Query", placeholder="あなたの置かれた状況について説明してください。")
        with col_askButton:
            ask_button = st.button("Ask", key="Ask") 

        if qdrant and ask_button: # クエリが入力されたら
            with st.spinner("Retrieving docs from VectorDB..."):
                retrieved_docs: list[Document] = qdrant.as_retriever(search_type="similarity", search_kwargs={"k":10}).invoke(query)
                
            with st.spinner("ChatGPT is thinking..."):
                qa_chain = (    # type: ignore
                    prompts("qa_chain")
                    | llm 
                    | StrOutputParser()        # 
                )
                answer: str = qa_chain.invoke(  # type: ignore
                    {
                        "context": format_docs(retrieved_docs),  # type: ignore
                        "query": query,
                    }
                )    # type: ignore
            st.session_state.retrieved_docs = retrieved_docs
            st.session_state.answer = answer

        if "answer" in st.session_state:
            st.markdown("### 回答")
            st.write(st.session_state.answer) # type: ignore

        if "retrieved_docs" in st.session_state:
            # 類似文章を表示
            st.markdown("---")
            st.markdown("### 関連する判例")
                #st.markdown("[関連度順]")
            col_sort, col_reverse = st.columns((1, 1))
            with col_sort:
                selectbox_sort = st.selectbox("Sort by:", ["関連度順", "日付順"])   # type: ignore
            with col_reverse:
                selectbox_reverse = st.selectbox("Reverse:", ["降順", "昇順"])
            if selectbox_sort == "関連度順":
                for i, doc in enumerate(st.session_state.retrieved_docs):   # type: ignore
                    with st.expander(f"{nengou(doc.metadata.get("date_era"))}{doc.metadata.get("date_year")}年{doc.metadata.get("date_month")}月{doc.metadata.get("date_day")}日    {doc.metadata.get("court_name")}    **{doc.metadata.get("case_name")}**"):     # type: ignore
                        st.markdown(f"事件番号：{doc.metadata.get('case_number')}")  # type: ignore
                        st.markdown("..." + doc.page_content + "...")
                        st.markdown(f"裁判所HP 裁判例結果詳細：{doc.metadata.get('detail_page_link')}") # type: ignore
                        st.markdown(f"PDF Link：{doc.metadata.get('full_pdf_link')}")   # type: ignore
            elif selectbox_sort == "日付順":
                list_date = []
                for i, doc in enumerate(st.session_state.retrieved_docs):   # type: ignore
                    list_date.append(datetime.strptime(f"{nengou_to_year(doc.metadata.get('date_era'), doc.metadata.get('date_year'))}-{doc.metadata.get('date_month')}-{doc.metadata.get('date_day')}", "%Y-%m-%d"))   # type: ignore
                copied_docs = st.session_state.retrieved_docs.copy()
                sorted_docs: list[Document] = [x for _, x in sorted(zip(list_date, copied_docs), key=lambda pair: pair[0], reverse=True if selectbox_reverse == "降順" else False)]  # type: ignore

                for i, doc in enumerate(sorted_docs):   # type: ignore
                    with st.expander(f"{nengou(doc.metadata.get("date_era"))}{doc.metadata.get("date_year")}年{doc.metadata.get("date_month")}月{doc.metadata.get("date_day")}日    {doc.metadata.get("court_name")}    **{doc.metadata.get("case_name")}**"):      # type: ignore
                        st.markdown(f"事件番号：{doc.metadata.get('case_number')}")   # type: ignore
                        st.markdown("..." + doc.page_content + "...")
                        st.markdown(f"裁判所HP 裁判例結果詳細：{doc.metadata.get('detail_page_link')}")  # type: ignore
                        st.markdown(f"PDF Link：{doc.metadata.get('full_pdf_link')}")   # type: ignore

    with tab_law:
        # st.session_state.answer で言及されている法令を抽出、条文をAPIで取得して表示する
        st.markdown("### 関連する法令")
        st.markdown("e-GOV APIを使用して法令の条文を取得")
        if "answer" in st.session_state:
            ## 法令抽出
            extract_law_chain = (   # type: ignore
                prompts("extract_law")
                | llm
                | StrOutputParser()
                | str_to_list
            )
            extracted_laws: list[list[str]] = extract_law_chain.invoke({"context": st.session_state.answer})  # type: ignore
            st.markdown(extracted_laws)      # これで、言及された法律の名称、条、項、号のリストが取得できた

            ## 法令の検索
            ## 言及された法令の名称が辞書内の法令に、　完全一致するならそれを表示　/　部分一致なら名称のみでキーワード検索、結果を表示
            for law in extracted_laws:   # law = [法令名, 条, 項, 号]
                if len(law) != 4 or law[0] == "":  # type: ignore
                    continue
                
                law_str: str = " ".join([law[0], law[1]])  # type: ignore
                if law[1] != "":
                    law_str += "条"
                law_str += law[2]  # type: ignore
                if law[2] != "":
                    law_str += "項" # type: ignore
                law_str += law[3] # type: ignore
                if law[3] != "":
                    law_str += "号" # type: ignore

                st.markdown(f"##### {law_str}")

                num_from_name = get_num_from_name(law[0])  # type: ignore
                
                ### 名称完全一致
                if num_from_name != "": 
                    # 法令番号から条文を取得
                    with st.spinner("Retrieving law from API..."):
                        with st.expander(law_str):      # type: ignore
                            law_contents = get_law_from_num(num_from_name)  # type: ignore
                            st.markdown(law_contents)   # type: ignore

                ### 名称部分一致
                else:
                    # 法令名をキーワードとして、関連しそうな法令番号を取得
                    num_from_name_keywords: dict[str, str] = get_num_from_name_keywords([law[0]])   # type: ignore

                    # それぞれの条文を取得
                    for i, (name, num) in enumerate(num_from_name_keywords.items()):    # type: ignore
                        with st.spinner("Retrieving law from API..."):    
                            if i >= 5:
                                break
                            with st.expander(f"{name}"):
                                law_contents = get_law_from_num(num)    # type: ignore
                                st.markdown(law_contents)   # type: ignore


        
if __name__ == '__main__':
    load_cloud_qdrant(collection_name=COLLECTION_NAME)