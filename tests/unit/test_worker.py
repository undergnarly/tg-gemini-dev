import pytest
from unittest.mock import patch
from crewai import Agent, Task, Crew
from services.worker.main import researcher, writer, create_analysis_task, create_report_task, create_crew

def test_researcher_agent_creation():
    """Tests if the researcher agent is created correctly."""
    assert isinstance(researcher, Agent)
    assert researcher.role == 'Senior Research Analyst'

def test_writer_agent_creation():
    """Tests if the writer agent is created correctly."""
    assert isinstance(writer, Agent)
    assert writer.role == 'Professional Content Writer'

def test_analysis_task_creation():
    """Tests if the analysis task is created with the correct properties."""
    sample_text = "This is a test."
    task = create_analysis_task(sample_text)
    assert isinstance(task, Task)
    assert sample_text in task.description
    assert task.agent == researcher

def test_report_task_creation():
    """Tests if the report task is created with the correct properties."""
    task = create_report_task()
    assert isinstance(task, Task)
    assert task.agent == writer

def test_crew_creation():
    """Tests if the crew is assembled correctly."""
    crew = create_crew("some text")
    assert isinstance(crew, Crew)
    assert len(crew.agents) == 2
    assert crew.agents == [researcher, writer]
    assert len(crew.tasks) == 2
