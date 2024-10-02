import streamlit as st

from langchain.docstore.document import Document
from langchain_core.runnables import RunnablePassthrough
#from langchain_core.output_parsers import StrOutputParser

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

from langchain_qdrant import QdrantVectorStore 
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from prompts import prompts     # type: ignore

QDRANT_PATH = "./local_qdrant"
COLLECTION_NAME = "database"

def select_model():
    model = st.sidebar.radio("Choose a model:", ("GPT-4o mini", "(GPT-3.5-turbo)"))
    if model == "(GPT-3.5-turbo)":
        model_name = "gpt-3.5-turbo"
    else:
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

    #return Qdrant(
    return QdrantVectorStore(
        client=client,
        collection_name=collection_name, 
        embedding=OpenAIEmbeddings()
    )

def format_docs(docs: list[Document]) -> str:   # 出力の型合ってる？
    return "\n\n".join(doc.page_content for doc in docs)



# -----------------------------------------------------------------------------------------------------

def page_ask_llm():
    st.title("Ask LLM")

    llm = select_model()
    try:
        qdrant = load_qdrant(COLLECTION_NAME)
    except Exception as e:
        st.sidebar.error(f"Failed to load Qdrant: {e}")
        qdrant = None

    col_query, col_askButton = st.columns((5, 1), vertical_alignment="bottom")
    with col_query:
        query = st.text_input("What's your problem?", key="Query")
    with col_askButton:
        ask_button = st.button("Ask", key="Ask") 

    if qdrant and ask_button: # クエリが入力されたら
        qa_chain = (    # type: ignore
            {
                "context": qdrant.as_retriever(search_type="similarity", search_kwargs={"k":10}) | format_docs,  # type: ignore
                "query": RunnablePassthrough(),
            }
            | prompts("qa_chain")
            | llm 
            #| StrOutputParser()        # 一旦コメントアウト
        )

        output: str = qa_chain.invoke(query)    # type: ignore
        st.write(output) # type: ignore