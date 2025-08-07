import io
import pandas as pd
from typing import Dict, Any, Optional
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider
from pydantic import BaseModel, Field

from config.settings import get_settings
from services.jupyter_service import CSVAnalysisService
from utils.prompt import CSV_ANALYSIS_PROMPT, CODE_FIX_PROMPT, CSV_AGENT_PROMPT


class CSVAnalysisContext(BaseModel):
    session_id: str
    csv_content: str
    csv_headers: list
    sample_data: list


class PythonCodeResponse(BaseModel):
    python_code: str = Field(description="Generated Python code for data analysis")
    explanation: str = Field(description="Explanation of what the code does")
    expected_output: str = Field(description="What output is expected from the code")
    libraries_used: list = Field(description="List of Python libraries used")


class CodeExecutionResult(BaseModel):
    status: str = Field(description="Execution status: success, error, or retry")
    output: str = Field(description="Output from code execution")
    error_message: Optional[str] = Field(description="Error message if execution failed")
    execution_time: float = Field(description="Time taken to execute the code")
    attempt: int = Field(description="Attempt number")


class CSVAnalysisTools:
    def __init__(self):
        self.settings = get_settings()
        self.csv_service = CSVAnalysisService()
        
        self.code_generation_model = GroqModel(
            self.settings.groq_model_name,
            provider=GroqProvider(api_key=self.settings.groq_api_key)
        )
        
        self.code_generation_agent = Agent(
            self.code_generation_model,
            instructions=CSV_ANALYSIS_PROMPT,
            output_type=PythonCodeResponse
        )
        
        self.code_fixing_model = GroqModel(
            self.settings.groq_model_name,
            provider=GroqProvider(api_key=self.settings.groq_api_key)
        )
        
        self.code_fixing_agent = Agent(
            self.code_fixing_model,
            instructions=CODE_FIX_PROMPT,
            output_type=PythonCodeResponse
        )
    
    def load_csv_data(self, csv_content: str, session_id: str) -> Dict[str, Any]:
        return self.csv_service.load_csv_data(session_id, csv_content)
    
    def generate_analysis_code(self, user_query: str, csv_context: CSVAnalysisContext) -> PythonCodeResponse:
        prompt = f"""
CSV Headers: {csv_context.csv_headers}
Sample Data: {csv_context.sample_data[:3]}
User Query: {user_query}

Generate Python code that:
1. Uses pandas for data manipulation
2. Creates visualizations if requested
3. Returns clear output
4. Handles the CSV data properly
"""
        
        result = self.code_generation_agent.run_sync(prompt)
        return result.output
    
    def execute_analysis_code(self, python_code: str, session_id: str, max_retries: int = 3) -> CodeExecutionResult:
        result = self.csv_service.execute_analysis(session_id, python_code, max_retries)
        
        return CodeExecutionResult(
            status=result["status"],
            output=result.get("output", ""),
            error_message=result.get("error_message"),
            execution_time=result.get("execution_time", 0.0),
            attempt=result.get("attempt", 1)
        )
    
    def fix_code_error(self, original_code: str, error_message: str, csv_context: CSVAnalysisContext) -> PythonCodeResponse:
        prompt = f"""
Original Code:
{original_code}

Error Message:
{error_message}

CSV Headers: {csv_context.csv_headers}
Sample Data: {csv_context.sample_data[:3]}

Please fix the code to resolve the error and ensure it works correctly.
"""
        
        result = self.code_fixing_agent.run_sync(prompt)
        return result.output
    
    def get_csv_info(self, session_id: str) -> Dict[str, Any]:
        return self.csv_service.get_csv_info(session_id)
    
    def close_session(self, session_id: str):
        self.csv_service.close_session(session_id)


def create_csv_analysis_agent() -> Agent:
    settings = get_settings()
    
    model = GroqModel(
        settings.groq_model_name,
        provider=GroqProvider(api_key=settings.groq_api_key)
    )
    
    agent = Agent(
        model,
        instructions=CSV_AGENT_PROMPT,
        output_type=str
    )
    
    csv_tools = CSVAnalysisTools()
    
    @agent.tool
    async def load_csv_data(ctx: RunContext[None], csv_content: str, session_id: str) -> str:
        result = csv_tools.load_csv_data(csv_content, session_id)
        if result["status"] == "success":
            return f"CSV loaded successfully! Shape: {result['shape']}, Columns: {result['columns']}"
        else:
            return f"Error loading CSV: {result['message']}"
    
    @agent.tool
    async def generate_analysis_code(ctx: RunContext[None], user_query: str, session_id: str) -> str:
        csv_info = csv_tools.get_csv_info(session_id)
        if csv_info["status"] != "success":
            return f"Error: {csv_info['message']}"
        
        csv_context = CSVAnalysisContext(
            session_id=session_id,
            csv_content="",
            csv_headers=csv_info["columns"],
            sample_data=csv_info["sample_data"]
        )
        
        result = csv_tools.generate_analysis_code(user_query, csv_context)
        return f"""Generated Python Code:
```python
{result.python_code}
```

Explanation: {result.explanation}
Expected Output: {result.expected_output}
Libraries Used: {', '.join(result.libraries_used)}"""
    
    @agent.tool
    async def execute_analysis_code(ctx: RunContext[None], python_code: str, session_id: str) -> str:
        result = csv_tools.execute_analysis_code(python_code, session_id)
        
        if result.status == "success":
            return f"""✅ Code executed successfully!
Execution Time: {result.execution_time:.2f}s
Attempt: {result.attempt}

Output:
{result.output}"""
        else:
            return f"""❌ Code execution failed!
Attempt: {result.attempt}
Error: {result.error_message}

Output:
{result.output}"""
    
    @agent.tool
    async def fix_code_error(ctx: RunContext[None], original_code: str, error_message: str, session_id: str) -> str:
        csv_info = csv_tools.get_csv_info(session_id)
        if csv_info["status"] != "success":
            return f"Error: {csv_info['message']}"
        
        csv_context = CSVAnalysisContext(
            session_id=session_id,
            csv_content="",
            csv_headers=csv_info["columns"],
            sample_data=csv_info["sample_data"]
        )
        
        result = csv_tools.fix_code_error(original_code, error_message, csv_context)
        return f"""🔧 Fixed Code:
```python
{result.python_code}
```

Explanation: {result.explanation}
Expected Output: {result.expected_output}"""
    
    @agent.tool
    async def get_csv_info(ctx: RunContext[None], session_id: str) -> str:
        result = csv_tools.get_csv_info(session_id)
        if result["status"] == "success":
            return f"""📊 CSV Information:
Shape: {result['shape']}
Columns: {result['columns']}
Data Types: {result['dtypes']}
Sample Data: {result['sample_data'][:2]}"""
        else:
            return f"Error: {result['message']}"
    
    return agent 