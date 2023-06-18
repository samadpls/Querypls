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
st.set_page_config(page_title="Querypls",
                   page_icon="./logo/logo.png",
                   layout="centered",
                   initial_sidebar_state="auto") 
def main():
    with open('styles.css') as f:
        st.markdown(f"<style>{f.read()}</style>",unsafe_allow_html=True)
    st.markdown("""<a href='https://github.com/samadpls/Querypls'><img src='https://img.shields.io/github/stars/samadpls/querypls?color=red&label=star%20me&logoColor=red&style=social'></a>""",unsafe_allow_html=True) 
    img , heading =  st.columns([1,8]) # using columns to display the heading and image
    with img:
        st.image("logo/logo.png",width=70) # logo
    with heading:
        st.title('Querypls - SQL Query Provider')  # heading
    

    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm_chain = LLMChain(prompt=prompt, llm=llm)

    question = st.text_area("Enter your SQL query:")

    try:
        if st.button("Run"):
            if question.strip():  # Check if the question is not empty
                import re
                response = llm_chain.run(question)
                st.markdown("### Response:")
                cleaned_response = re.sub(r"<\/?code>|<\/?pre>", "", response)
                st.markdown(cleaned_response,unsafe_allow_html=True)
            else:
                st.success("Hi there! I'm Querypls, created by Abdul Samad Siddiqui. How can I assist you with your SQL queries?")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


    st.markdown('`Made with 🤍 by samadpls`')   

if __name__ == "__main__":
    main()
