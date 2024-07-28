# !pip install langchain huggingface_hub > /dev/null

import os

huggingfacehub_api_token = "YOUR_API_TOKEN"

# pip install huggingface_hub

# pip install langchain

from langchain import HuggingFaceHub

repo_id = "tiiuae/falcon-7b-instruct"
llm = HuggingFaceHub(
    huggingfacehub_api_token=huggingfacehub_api_token,
    repo_id=repo_id,
    model_kwargs={"temperature": 0.6, "max_new_tokens": 100},
)

from langchain import PromptTemplate, LLMChain

template = ""
prompt = PromptTemplate(template=template, input_variables=["question"])
llm_chain = LLMChain(prompt=prompt, llm=llm)

question = ""

print(llm_chain.run(question))
