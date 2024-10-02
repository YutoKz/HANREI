"""

    JSON 形式の判例データを、Qdrantにアップロードするためのスクリプト
    一旦はローカルに保存されたJSONファイルを読み込んでアップロードする方法を取るが、
    本来はAPIを通じてGitHubからデータにアクセスする方法が望ましい

    
    データセットリンク：
        https://github.com/japanese-law-analysis/data_set/blob/master/precedent/

    JSONの形式(判例2020)：
        {
            "trial_type": "LowerCourt",
            "date": {
                "era": "Reiwa",
                "year": 2,
                "month": 11,
                "day": 6
            },
            "case_number": "令和1(う)412",
            "case_name": "不正作出支払用カード電磁的記録供用，窃盗",
            "court_name": "福岡高等裁判所",
            "result": "破棄自判",
            "lawsuit_id": "89875",
            "detail_page_link": "https://www.courts.go.jp/app/hanrei_jp/detail4?id=89875",
            "full_pdf_link": "https://www.courts.go.jp/app/files/hanrei_jp/875/089875_hanrei.pdf",
            "contents": "令和元年(う)第412号　..."
        }

    ベースコード：
        text = '\n\n'.join([page.extract_text() for page in pdf_reader.pages])
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            model_name="gpt-3.5-turbo",
            # 適切な chunk size は質問対象のPDFによって変わるため調整が必要
            # 大きくしすぎると質問回答時に色々な箇所の情報を参照することができない
            # 逆に小さすぎると一つのchunkに十分なサイズの文脈が入らない
            chunk_size=1000,
            chunk_overlap=0,
        )
        text_list = text_splitter.split_text(text)    <- chunkのリスト
        if text_list:
            with st.spinner("Loading ..."):
                qdrant.add_texts(text_list, metadatas=[{"type": "Paper", "source": url} for _ in text_list])
"""

import os
import json

import streamlit as st

from langchain_qdrant import QdrantVectorStore 
from langchain.text_splitter import RecursiveCharacterTextSplitter

from ask_llm import load_qdrant # type: ignore


QDRANT_PATH = "./local_qdrant"
COLLECTION_NAME = "database"

def upload_json_to_qdrant(json_folder_path: str):
    """
        JSON形式の判例データをQdrantにアップロードする

        Args:
            json_folder_path (str): JSONファイルが 直下に 格納されているフォルダ
    """
    try:
        qdrant = load_qdrant(COLLECTION_NAME)
    except Exception as e:
        # st.sidebar.error(f"Failed to load Qdrant: {e}")      もしstreamlitを使う場合はコメントアウトを外す
        qdrant = None
    
    if qdrant:
        # text_splitter 生成
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            model_name="gpt-3.5-turbo",
            # 適切な chunk size は質問対象のPDFによって変わるため調整が必要
            # 大きくしすぎると質問回答時に色々な箇所の情報を参照することができない
            # 逆に小さすぎると一つのchunkに十分なサイズの文脈が入らない
            chunk_size=1000,
            chunk_overlap=0,
        )

        num_datas = len(os.listdir(json_folder_path))
        for i, json_file in enumerate(os.listdir(json_folder_path)):
            print(f"{i}/{num_datas}    {json_file}")
            if not json_file.endswith(".json") or json_file.endswith("list.json"):
                continue   
            
            with open(json_folder_path + "/" + json_file, "r", encoding="utf-8") as f:
                json_data = json.load(f)

                # 各要素を取得
                trial_type          = json_data.get("trial_type")
                date_era            = json_data["date"].get("era")
                date_year           = json_data["date"].get("year")
                date_month          = json_data["date"].get("month")
                date_day            = json_data["date"].get("day")
                case_number         = json_data.get("case_number")
                case_name           = json_data.get("case_name")
                court_name          = json_data.get("court_name")
                result              = json_data.get("result")
                lawsuit_id          = json_data.get("lawsuit_id")
                detail_page_link    = json_data.get("detail_page_link")
                full_pdf_link       = json_data.get("full_pdf_link")
                contents            = json_data.get("contents")

                # contents を text_splitter により分割
                # データセットには判決文のないものがある模様
                if contents:
                    splitted_contents = text_splitter.split_text(contents)

                # qdrantにアップロード
                metadata_dict = {
                    "trial_type": trial_type,
                    "date_era": date_era,
                    "date_year": date_year,
                    "date_month": date_month,
                    "date_day": date_day,
                    "case_number": case_number,
                    "case_name": case_name,
                    "court_name": court_name,
                    "result": result,
                    "lawsuit_id": lawsuit_id,
                    "detail_page_link": detail_page_link,
                    "full_pdf_link": full_pdf_link
                }

                if splitted_contents:
                    qdrant.add_texts(splitted_contents, metadatas=[metadata_dict for _ in splitted_contents])





if __name__ == '__main__':
    upload_json_to_qdrant(json_folder_path="./data/japanese-law-analysis/precedent/2020")
