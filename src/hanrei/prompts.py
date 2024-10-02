from langchain_core.prompts import PromptTemplate

def prompts(template_name: str) -> PromptTemplate:
    if template_name == "qa_chain":
        return PromptTemplate.from_template(    # type: ignore
        """     
<context>
{context}
</context>

以上は、関連する判例の一部である。これらを参照しながら以下の質問に答えよ。
なお、回答する上では以下の条件を満たすこと。
1. 質問者の置かれた状況を考慮すること。
2. 関連する判例のみを参考に回答し、事前に学習した法律知識を用いないこと。
3. 関連する判例のうち、関連する箇所を引用すること。
4. 提示した判例から関連すると思われる法律があればその条, 項, 号を回答の最後に明記すること。 
5. 上記の判例に言及する際は、「過去の判例によれば、」という表現を用いること。

質問：
{query}

回答：
        """)
    else:
        raise ValueError(f"Invalid template name: {template_name}")