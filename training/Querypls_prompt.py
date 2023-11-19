
# !pip install langchain huggingface_hub > /dev/null

import os
huggingfacehub_api_token ="YOUR_API_TOKEN"

pip install huggingface_hub

pip install langchain

from langchain import HuggingFaceHub

repo_id = "tiiuae/falcon-7b-instruct"
llm = HuggingFaceHub(huggingfacehub_api_token=huggingfacehub_api_token,
                     repo_id=repo_id,
                     model_kwargs={"temperature":0.6, "max_new_tokens":100})

from langchain import PromptTemplate, LLMChain

template  ="""Act as a SQL expert developer. I'll type question you'll reply with what the SQL code should look. I want you to only reply with the code output inside one unique code block, and nothing else. Do not write explanations. Do not type commands unless I instruct you to do so.
{question}
"""
prompt = PromptTemplate(template=template, input_variables=["question"])
llm_chain = LLMChain(prompt=prompt,llm=llm)

question = """
Create views for following purposes,To display each designation and number of employees with that particular designation.
"""

print(llm_chain.run(question))
