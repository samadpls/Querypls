import pytest
from src.services.csv_analysis_tools import CSVAnalysisTools, CSVAnalysisContext


def test_load_csv_data():
    tools = CSVAnalysisTools()
    csv_content = "name,age\nJohn,30\nJane,25"
    result = tools.load_csv_data(csv_content, "test_session")
    assert result["status"] == "success"
    assert "name" in result["columns"]
    assert "age" in result["columns"]


def test_get_csv_info():
    tools = CSVAnalysisTools()
    csv_content = "name,age\nJohn,30\nJane,25"
    tools.load_csv_data(csv_content, "test_session")
    info = tools.get_csv_info("test_session")
    assert info["status"] == "success"
    assert "shape" in info
    assert "columns" in info
    assert "dtypes" in info
