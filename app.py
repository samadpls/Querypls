import streamlit as st
from langchain import PromptTemplate, LLMChain
import os
from langchain import HuggingFaceHub

huggingfacehub_api_token =st.secrets['key']
repo_id = "tiiuae/falcon-7b-instruct"
llm = HuggingFaceHub(huggingfacehub_api_token=huggingfacehub_api_token,
                     repo_id=repo_id,
                     model_kwargs={"temperature":0.6, "max_new_tokens":180})

template = st.secrets['prompt']
def main():
    with open('styles.css') as f:
        st.markdown(f"<style>{f.read()}</style>",unsafe_allow_html=True)
    img , heading =  st.columns([1,8]) # using columns to display the heading and image
    with img:
        st.image("logo/logo.png",width=70) # logo
    with heading:
        st.title('Querypls - SQL Query Provider')  # heading


    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm_chain = LLMChain(prompt=prompt, llm=llm)

    question = st.text_area("Enter your SQL query:")
    
    if st.button("Run"):
        response = llm_chain.run(question)
        st.markdown("### Response:")
        styled_responses = response.replace("</code>", "").replace("<code>", "").replace("<pre>","").replace("</pre>","")
        # styled_response = f'<div style="color: white; background-color: #666666; padding: 10px; border-radius: 10px;">{styled_responses}</div>'
        st.markdown(styled_responses)

    st.markdown('`Made with 🤍 by samadpls`')   

if __name__ == "__main__":
    st.set_page_config(page_title="Querypls",page_icon="./logo/logo.png",layout="centered",initial_sidebar_state="auto") 
    main()
