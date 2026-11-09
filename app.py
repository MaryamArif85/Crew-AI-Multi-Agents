import os
from dotenv import load_dotenv
import litellm
litellm.drop_params = True

# Crew Orchestrator 
from crewai import Agent, Task, Crew, Process, LLM

# Load API key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Please add GEMINI_API_KEY to your .env file")

# Initialize Gemini 3.6 Flash through CrewAI's LLM wrapper
llm = LLM(
    model="gemini/gemini-3.6-flash",
    api_key=GEMINI_API_KEY,
    temperature=0.3,
    timeout=120,
    max_retries=3
)

# -----------------------------
# AGENTS
# -----------------------------

researcher = Agent(
    role="AI Researcher",
    goal="Research topics and provide accurate information.",
    backstory="You are an expert researcher specializing in AI and technology.",
    llm=llm,
    verbose=True
)

analyst = Agent(
    role="Research Analyst",
    goal="Analyze research and identify important insights.",
    backstory="You are an expert analyst who evaluates information critically.",
    llm=llm,
    verbose=True
)

writer = Agent(
    role="Professional Writer",
    goal="Create a detailed and professional final report.",
    backstory="You are an expert technical and business writer.",
    llm=llm,
    verbose=True
)

# -----------------------------
# TASKS
# -----------------------------

research_task = Task(
    description="""
    Research this topic: {topic}

    Include:
    1. Introduction
    2. Key concepts
    3. Current developments
    4. Applications
    5. Benefits
    6. Challenges
    7. Future opportunities

    Do not invent facts or references.
    """,
    expected_output="A detailed research report.",
    agent=researcher
)

analysis_task = Task(
    description="""
    Analyze the research findings.

    Identify:
    1. Important insights
    2. Strengths and weaknesses
    3. Risks
    4. Opportunities
    5. Recommendations

    Do not introduce unsupported claims.
    """,
    expected_output="A detailed analytical report.",
    agent=analyst,
    context=[research_task]
)

writing_task = Task(
    description="""
    Create a professional final report about {topic}.

    Use the research and analysis.

    Structure:
    1. Executive Summary
    2. Introduction
    3. Research Findings
    4. Detailed Analysis
    5. Benefits and Challenges
    6. Recommendations
    7. Conclusion

    Format the report using Markdown.
    """,
    expected_output="A complete professional Markdown report.",
    agent=writer,
    context=[research_task, analysis_task],
    output_file="final_report.md"
)

# -----------------------------
# CREW
# -----------------------------

crew = Crew(
    agents=[researcher, analyst, writer],
    tasks=[research_task, analysis_task, writing_task],
    process=Process.sequential,
    verbose=True
)

# -----------------------------
# RUN
# -----------------------------

import time

# -----------------------------
# RUN
# -----------------------------

if __name__ == "__main__":
    topic = input("Enter your research topic: ")

    success = False
    max_attempts = 3
    result = None

    for attempt in range(max_attempts):
        try:
            print(f"\nAttempt {attempt + 1} of {max_attempts}: Starting crew execution...")
            result = crew.kickoff(
                inputs={"topic": topic}
            )
            success = True
            break
        except Exception as e:
            print(f"\n⚠️ Encountered an error on attempt {attempt + 1}: {e}")
            if attempt < max_attempts - 1:
                print("Waiting 5 seconds before retrying the crew execution...")
                time.sleep(5)
            else:
                print("\n❌ Max attempts reached. The crew could not complete the execution due to API errors.")
              
    if success and result:
      print("\n=============================================")
      print("🎉 Crew execution completed successfully!")
      print("📄 Report successfully saved to final_report.md")
      print("=============================================\n")
  

