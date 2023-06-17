import streamlit as st
from langchain import PromptTemplate, LLMChain
import os
from langchain import HuggingFaceHub

huggingfacehub_api_token ='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'
repo_id = "tiiuae/falcon-7b-instruct"
llm = HuggingFaceHub(huggingfacehub_api_token=huggingfacehub_api_token,
                     repo_id=repo_id,
                     model_kwargs={"temperature":0.6, "max_new_tokens":150})
template = """
You are samadpls SQL provider. I want you act as a SQL terminal in front of an example database. You can type queries, and I will reply with what the terminal would show. My responses will be in the form of a table of query results, enclosed in a single code block, and without any explanations. I will not type commands unless instructed to do so. When you need to provide instructions or information in English, please use curly braces {{like this}}.

{question}
"""
def main():
    with open('styles.css') as f:
        st.markdown(f"<style>{f.read()}</style>",unsafe_allow_html=True)
    st.title("SQL Provider")

    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm_chain = LLMChain(prompt=prompt, llm=llm)

    question = st.text_area("Enter your SQL query:")
    
    if st.button("Run"):
        response = llm_chain.run(question)
        st.markdown("### Response:")
        styled_responses = response.replace("</code></pre>", "").replace("<pre><code>", "")
        # styled_response = f'<div style="color: white; background-color: #666666; padding: 10px; border-radius: 10px;">{styled_responses}</div>'
        st.markdown(styled_responses)

    st.markdown('`Made with ❤ by samadpls`')   

if __name__ == "__main__":
    main()
