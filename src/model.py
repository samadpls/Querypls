from langchain_community.llms import HuggingFaceHub
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.auth import *
from src.constant import *


def create_huggingface_hub():
    """Creates an instance of Hugging Face Hub with specified configurations.

    Returns:
        HuggingFaceHub: Instance of Hugging Face Hub.
    """
    return HuggingFaceHub(
        huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
        repo_id=REPO_ID,
        model_kwargs={"temperature": 0.7, "max_new_tokens": 180},
    )
