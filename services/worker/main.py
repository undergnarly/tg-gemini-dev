import os
import logging
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY is not set in the environment or .env file")

# --- Agent Definitions ---

researcher = Agent(
  role='Senior Research Analyst',
  goal='Uncover groundbreaking technologies and analyze complex topics.',
  backstory="""You're a renowned Senior Research Analyst, known for your ability to demystify complex subjects
  and identify emerging trends. You have a knack for finding the most relevant information and presenting it clearly.""",
  verbose=True,
  allow_delegation=False,
)

writer = Agent(
  role='Professional Content Writer',
  goal='Craft compelling and easy-to-understand content from technical findings.',
  backstory="""You are a professional writer with a talent for making complex topics accessible.
  You can transform dense, technical information into engaging narratives that resonate with a broad audience.""",
  verbose=True,
  allow_delegation=True
)

# --- Task Definitions ---

def create_analysis_task(text_input: str) -> Task:
    """Creates a task for the research agent to analyze the given text."""
    return Task(
      description=(
          "Analyze the following text and identify the key points, main topic, and sentiment. "
          f"Here is the text to analyze:\n\n---\n{text_input}\n---"
      ),
      expected_output='A concise bullet-point summary of the key findings, topic, and sentiment.',
      agent=researcher
    )

def create_report_task() -> Task:
    """Creates a task for the writer agent to compile a report."""
    return Task(
      description=(
          "Using the analysis provided by the researcher, compile a brief, easy-to-read report. "
          "The report should be structured with a clear title, a summary of the analysis, and a concluding thought."
      ),
      expected_output='A well-formatted report in Markdown that is ready for publication.',
      agent=writer
    )

# --- Crew Definition ---

def create_crew(text_input: str) -> Crew:
    """Creates and configures the CrewAI team."""
    analysis_task = create_analysis_task(text_input)
    report_task = create_report_task()

    return Crew(
      agents=[researcher, writer],
      tasks=[analysis_task, report_task],
      process=Process.sequential,
      verbose=2
    )

def run_crew(text_input: str) -> str:
    """
    Initializes and runs the Crew to process the given text.
    Returns the result from the crew's execution.
    """
    logger.info(f"Initializing crew to analyze text: '{text_input[:50]}...'")
    crew = create_crew(text_input)
    result = crew.kickoff()
    logger.info("Crew finished processing.")
    return result

if __name__ == '__main__':
    sample_text = "The new open-interpreter library is showing great promise for local code execution in AI agent systems."
    logger.info("--- Running Standalone Worker Test ---")
    final_result = run_crew(sample_text)
    print("\n--- Final Result ---")
    print(final_result)
    print("--- End of Test ---") 