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

def load_qdrant(collection_name: str) -> QdrantVectorStore:
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



# -----------------------------------------------------------------------------------------------------

def page_ask_llm():
    st.title("判例検索 AI")

    llm = select_model()

    try:
        qdrant = load_qdrant(COLLECTION_NAME)
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
                output: str = qa_chain.invoke(  # type: ignore
                    {
                        "context": format_docs(retrieved_docs),  # type: ignore
                        "query": query,
                    }
                )    # type: ignore
            st.session_state.retrieved_docs = retrieved_docs
            st.session_state.output = output

        if "output" in st.session_state:
            st.markdown("### 回答")
            st.write(st.session_state.output) # type: ignore

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
        st.markdown("ここに法律検索のコードを書く")
        st.markdown("データベースはSQLを検討中。。")
        