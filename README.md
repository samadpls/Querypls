
<img src="static/image/logo.png">

![Supported python versions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) 
[![Run Unittests](https://github.com/samadpls/Querypls/actions/workflows/unittests.yml/badge.svg)](https://github.com/samadpls/Querypls/actions/workflows/unittests.yml)
[![License](https://img.shields.io/badge/License-MIT%202.0-blue.svg)](LICENSE)
<img src='https://img.shields.io/github/stars/samadpls/querypls?color=red&label=stars&logoColor=black&style=social'>

# 💬 Querypls - Prompt to SQL 

Querypls is a web application that provides an interactive chat interface, simplifying SQL query generation. Users can effortlessly enter SQL queries and receive corresponding results. The application harnesses the capabilities of the language models from Hugging Face to generate SQL queries based on user input.

## Key Features

💬 Interactive chat interface for easy communication.  
🔍 Enter SQL queries and receive query results as responses.  
🤖 Utilizes language models from Hugging Face for advanced query generation ([Querypls-prompt2sql](https://huggingface.co/samadpls/querypls-prompt2sql)).  
💻 User-friendly interface for seamless interaction.  

![QueryplsDemo](https://github.com/samadpls/Querypls/assets/94792103/daa6e37d-a256-4fd8-9607-6e18cf41df3f)



# Acknowledgments

`Querypls` received a shoutout from [🦜 🔗 Langchain](https://www.langchain.com/) on their Twitter, reaching over **60,000 impressions**. Additionally, it was featured under the **Community Favorite Projects** section on `🦜 🔗 Langchain's blog`, leading to a significant increase in stars for this repository and a growing user base. The project was also highlighted in a [YouTube video](https://www.youtube.com/watch?v=htHVb-fK9xU), and it also caught the attention of Backdrop, expressing their interest and liking in an email, inviting the project to be a part of their hackathon.

| [🔗 Langhchain Twitter Post](https://twitter.com/LangChainAI/status/1729959981523378297?t=Zdpw9ZQYvE3QS-3Bf-xaGw&s=19) | [🔗 Langhcain Blog Post](https://blog.langchain.dev/week-of-11-27-langchain-release-notes/) | 
|----------|----------|
| [![Twitter Post](https://github.com/samadpls/Querypls/assets/94792103/045519c1-3f50-4d60-ab51-68669ce1f270)](https://twitter.com/LangChainAI/status/1729959981523378297?t=Zdpw9ZQYvE3QS-3Bf-xaGw&s=19) | [![Blog Post](https://github.com/samadpls/Querypls/assets/94792103/3d399715-bfa6-4ee3-a736-e692477c6f31)](https://blog.langchain.dev/week-of-11-27-langchain-release-notes/) | 
[🎥 YouTube Video](https://www.youtube.com/watch?v=htHVb-fK9xU) | [Backdrop Hackathon Invitation](https://backdropbuild.com/v2/directory) |
[![YouTube Video](https://img.youtube.com/vi/htHVb-fK9xU/0.jpg)](https://www.youtube.com/watch?v=htHVb-fK9xU) | <img src='https://github.com/samadpls/Querypls/assets/94792103/3e990638-e585-4082-bfc3-398469309dc8' height=400px> |
> A big thank you to Langchain for their support and recognition!

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


> [!Note]  
> Querypls, while powered by a 7B model of Satablility AI LLM Model, is currently limited in providing optimal responses for simple queries.

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

---

`Made with 🤍 by samadpls`
