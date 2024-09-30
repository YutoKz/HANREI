from langchain_core.prompts import PromptTemplate

def prompts(template_name: str) -> PromptTemplate:
    if template_name == "qa_chain":
        return PromptTemplate.from_template(    # type: ignore
        """     
<context>
{context}
</context>

以上は、関連する判例の一部である。以下の質問に答えよ。
なお、回答する上では以下の条件を満たすこと。
1. 上記の判例のみを参考に回答し、事前に学習した法律知識を用いないこと。
2. 質問者の置かれた状況を考慮すること。
3. 回答の最後には判例から関連すると思われる法律の条, 項, 号を明記すること。 

質問：
{query}

回答：
        """)