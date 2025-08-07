"""
Jupyter service for executing Python code with CSV data analysis.
"""

import os
import jupyter_client
import inspect
import time
import re
import pandas as pd
from typing import Dict, Any, Optional
from dataclasses import dataclass

from config.constants import EXECUTION_TIMEOUT, MAX_RETRIES


def clean_error_message(error_msg: str) -> str:
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    cleaned_msg = ansi_escape.sub('', error_msg)
    lines = cleaned_msg.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    cleaned_msg = '\n'.join(lines)
    return cleaned_msg


@dataclass
class ExecutionResult:
    output: str
    status: str
    error_message: Optional[str] = None
    execution_time: float = 0.0


class SimpleJupyterClient:
    def __init__(self):
        self.clients: Dict[str, Any] = {}
        self.globals: Dict[str, Dict[str, Any]] = {}

    def create_new_session(self, session_id: str = "default", kernel_name: str = 'python3') -> str:
        if session_id in self.clients:
            return session_id

        km = jupyter_client.KernelManager(kernel_name=kernel_name)
        km.start_kernel()
        client = km.client()
        self.clients[session_id] = client
        self.globals[session_id] = {}

        for key, value in os.environ.items():
            self.execute_code(f"{key} = '{value}'", session_id)
        
        self.execute_code("import pandas as pd", session_id)
        self.execute_code("import numpy as np", session_id)
        self.execute_code("import matplotlib.pyplot as plt", session_id)
        self.execute_code("import seaborn as sns", session_id)
        
        return session_id

    def execute_code(self, code: str, session_id: str = "default") -> ExecutionResult:
        if session_id not in self.clients:
            raise ValueError(f"Session {session_id} not found")

        client = self.clients[session_id]
        start_time = time.time()

        msg_id = client.execute(code)
        output = []
        timeout = time.time() + EXECUTION_TIMEOUT
        status = "Success"
        error_message = None

        while True:
            try:
                msg = client.get_iopub_msg(timeout=1)
                if 'parent_header' not in msg or msg['parent_header'].get('msg_id') != msg_id:
                    continue

                msg_type = msg.get('msg_type', '')
                content = msg.get('content', {})

                if msg_type == 'execute_result':
                    output.append(str(content.get('data', {}).get('text/plain', '')))
                elif msg_type == 'stream':
                    output.append(content.get('text', ''))
                elif msg_type == 'error':
                    error_traceback = "\n".join(content.get('traceback', []))
                    cleaned_error = clean_error_message(error_traceback)
                    output.append(f"Error: {cleaned_error}")
                    error_message = cleaned_error
                    status = 'Fail'
                elif msg_type == 'status' and content.get('execution_state') == 'idle':
                    break
            except Exception as e:
                pass

        execution_time = time.time() - start_time

        return ExecutionResult(
            output='\n'.join(output).strip(),
            status=status,
            error_message=error_message,
            execution_time=execution_time
        )

    def import_function(self, func, session_id: str = "default") -> ExecutionResult:
        if session_id not in self.globals:
            raise ValueError(f"Session {session_id} not found")

        func_code = inspect.getsource(func)
        func_name = func.__name__

        result = self.execute_code(func_code, session_id)
        if result.status == "Success":
            self.globals[session_id][func_name] = func

        return result

    def close_session(self, session_id: str = "default"):
        if session_id not in self.clients:
            raise ValueError(f"Session {session_id} not found")

        client = self.clients[session_id]
        client.stop_channels()
        del self.clients[session_id]
        del self.globals[session_id]

    def close_all_sessions(self):
        for session_id in list(self.clients.keys()):
            self.close_session(session_id)


class CSVAnalysisService:
    def __init__(self):
        self.jupyter_client = SimpleJupyterClient()
        self.csv_data: Dict[str, pd.DataFrame] = {}
        self.csv_headers: Dict[str, list] = {}
    
    def load_csv_data(self, session_id: str, csv_content: str, filename: str = "data.csv") -> Dict[str, Any]:
        try:
            self.jupyter_client.create_new_session(session_id)
            
            csv_code = f"""
import pandas as pd
import io

csv_content = '''{csv_content}'''
df = pd.read_csv(io.StringIO(csv_content))
print("CSV loaded successfully!")
print(f"Shape: {{df.shape}}")
print("\\nColumns:")
print(df.columns.tolist())
print("\\nFirst few rows:")
print(df.head())
"""
            
            result = self.jupyter_client.execute_code(csv_code, session_id)
            
            if result.status == "Success":
                df = pd.read_csv(io.StringIO(csv_content))
                self.csv_data[session_id] = df
                self.csv_headers[session_id] = df.columns.tolist()
                
                return {
                    "status": "success",
                    "message": "CSV loaded successfully",
                    "shape": df.shape,
                    "columns": df.columns.tolist(),
                    "sample_data": df.head().to_dict('records')
                }
            else:
                return {
                    "status": "error",
                    "message": result.error_message or "Failed to load CSV"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def execute_analysis(self, session_id: str, python_code: str, max_retries: int = MAX_RETRIES) -> Dict[str, Any]:
        for attempt in range(max_retries):
            try:
                result = self.jupyter_client.execute_code(python_code, session_id)
                
                if result.status == "Success":
                    return {
                        "status": "success",
                        "output": result.output,
                        "execution_time": result.execution_time,
                        "attempt": attempt + 1
                    }
                else:
                    if attempt == max_retries - 1:
                        return {
                            "status": "error",
                            "error_message": result.error_message,
                            "output": result.output,
                            "attempt": attempt + 1
                        }
                    continue
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    return {
                        "status": "error",
                        "error_message": str(e),
                        "attempt": attempt + 1
                    }
                continue
        
        return {
            "status": "error",
            "error_message": "Max retries exceeded",
            "attempt": max_retries
        }
    
    def get_csv_info(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.csv_data:
            return {"status": "error", "message": "No CSV data loaded for this session"}
        
        df = self.csv_data[session_id]
        return {
            "status": "success",
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.to_dict(),
            "sample_data": df.head().to_dict('records')
        }
    
    def close_session(self, session_id: str):
        self.jupyter_client.close_session(session_id)
        if session_id in self.csv_data:
            del self.csv_data[session_id]
        if session_id in self.csv_headers:
            del self.csv_headers[session_id] 