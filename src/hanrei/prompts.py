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
4. 提示した判例から関連すると思われる法律があればその条, 項, 号を回答の最後に明記すること。必要に応じ、略称を正式名称になおすこと。 
5. その他、関連する基準や判例があればそれらも明記すること。
6. 上記の判例に言及する際は、「過去の判例によれば、」という表現を用いること。

質問：
{query}

回答：
        """)
    
    elif template_name == "extract_law":
        return PromptTemplate.from_template(    # type: ignore
        """
<context>
{context}
</context>

以上の文章で言及されている法律を抽出せよ。
法律の名称については、必要に応じて略称を正式名称になおすこと。
なお、出力の形式は以下に示す例に従うこと。
該当する項目がない場合は空欄とせよ。

例（法令の名称, 条, 項, 号）：
著作権法, 30, , \n
商法, 10, 2,

結果：
        """)
    

    else:
        raise ValueError(f"Invalid template name: {template_name}")