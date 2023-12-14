
<img src="static/image/logo.png">

![Supported python versions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) 
[![CI](https://github.com/samadpls/Querypls/actions/workflows/unittests.yml/badge.svg)](https://github.com/samadpls/Querypls/actions/workflows/unittests.yml)
[![License](https://img.shields.io/badge/License-MIT%202.0-blue.svg)](LICENSE)
<img src='https://img.shields.io/github/stars/samadpls/querypls?color=red&label=stars&logoColor=black&style=social'>

# 💬 Querypls - Prompt to SQL 

Querypls is a web application that provides an interactive chat interface, simplifying SQL query generation. Users can effortlessly enter SQL queries and receive corresponding results. The application harnesses the capabilities of the language models from Hugging Face to generate SQL queries based on user input.

## Key Features

💬 Interactive chat interface for easy communication.  
🔍 Enter SQL queries and receive query results as responses.  
🤖 Utilizes language models from Hugging Face for advanced query generation ([Querypls-prompt2sql](https://huggingface.co/samadpls/querypls-prompt2sql)).  
💻 User-friendly interface for seamless interaction.  
🔒 Secure Google Authentication for OAuth2 integration.  
🔄 Chat history recording for easy reference.

![QueryplsDemo](https://github.com/samadpls/Querypls/assets/94792103/daa6e37d-a256-4fd8-9607-6e18cf41df3f)



# Acknowledgments

`Querypls` received a shoutout from [🦜 🔗 Langchain](https://www.langchain.com/) on their Twitter, reaching over **60,000 impressions**. Additionally, it was featured under the **Community Favorite Projects** section on `🦜 🔗 Langchain's blog`, leading to a significant increase in stars for this repository and a growing user base.
| [🔗 Langhchain Twitter Post](https://twitter.com/LangChainAI/status/1729959981523378297?t=Zdpw9ZQYvE3QS-3Bf-xaGw&s=19) | [🔗 Langhcain Blog Post](https://blog.langchain.dev/week-of-11-27-langchain-release-notes/) |
|----------|----------|
| [![Twitter Post](https://github.com/samadpls/Querypls/assets/94792103/045519c1-3f50-4d60-ab51-68669ce1f270)](https://twitter.com/LangChainAI/status/1729959981523378297?t=Zdpw9ZQYvE3QS-3Bf-xaGw&s=19) | [![Blog Post](https://github.com/samadpls/Querypls/assets/94792103/3d399715-bfa6-4ee3-a736-e692477c6f31)](https://blog.langchain.dev/week-of-11-27-langchain-release-notes/) |
> A big thank you to Langchain for their support and recognition!

---

## How to Contribute

1. Clone the repository:
    ```bash
    git clone https://github.com/samadpls/Querypls.git
    ```

2. Navigate to the project directory:
    ```bash
    cd Querypls
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file based on `.env_example` and set the necessary variables.

5. Run the application:
    ```bash
    streamlit run src/app.py
    ```

6. Open the provided link in your browser to use Querypls.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

`Made with 🤍 by samadpls`
