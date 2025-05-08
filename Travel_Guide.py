# Import necessary libraries
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai.tools import tool
from langchain.tools import Tool
from scrapper import CustomScrapeWebsiteTool
import os


# Set OpenRouter API credentials - these are working based on your test results
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
os.environ["OPENAI_API_KEY"] = "Replace your api key"

# Disable CrewAI telemetry which might be causing timeout issues
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"

# Create a chat model - use the same configuration that worked in your test
llm = ChatOpenAI(
    model="define your model",
    temperature=0.7
)




# Define a tool to scrape website content

# @tool("ScrapeWebsite")
# def scrape_website(url: str) -> str:
#     """Scrape content from the given website URL."""
#     import requests
#     from bs4 import BeautifulSoup

#     if not url:
#         return "Please provide a valid URL to scrape."

#     try:
#         response = requests.get(url)
#         soup = BeautifulSoup(response.text, "html.parser")
#         return soup.get_text()[:500]
#     except Exception as e:
#         return f"Error scraping website: {str(e)}"


import requests
from bs4 import BeautifulSoup

@tool("ScrapeWebsite")
def scrape_website(url: str) -> str:
    """Scrape content from the given website URL."""
    try:
        if not url:
            return "Error: 'url' argument is missing."

        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator='\n', strip=True)
        return text[:1000]  
    except Exception as e:
        return f"Scraping failed: {str(e)}"



# Define the Analyzer agent (Travel Analyzer)
Analyzer_agent = Agent(
    role="Travel Analyzer",
    goal="Analyze the user input to understand the user's exact requirements.",
    backstory="You are a detail-oriented travel assistant specializing in interpreting user preferences for travel planning.",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# Define the Place Recommender agent (Tourist Guide)
place_recommender_agent = Agent(
    role="Tourist Guide",
    goal="Recommend the best places to visit based on the type of place the user wants to visit.",
    backstory=(
        "You work as a travel guide in your local city, Bangalore. You recommend places based on the requirements analyzed by the Travel Analyzer. "
        "You specialize in recommending places based on categories like tourist attractions, temples, amusement parks, restaurants, art galleries, and more. "
        "You can use the available tools (such as scrape_website) to gain current information and suggest the best places for the user to visit. "
        "Do not make any assumptions; recommend only data-supported options."
    ),
    verbose=True,
    llm=llm,
    tools=[scrape_website]
)

# Validate_agent=Agent(
#     role="Validator",
#     goal="You validate the final recommendation ",
#     backstory="You are a validator agent "
#               "You check whether the recommendations satisfies the uers request"
#               "validate the output of the tool aswell",
#     verbose=True,
#     allow_delegation=True,
#     llm=llm
# )

# Define the Analyze task for the Analyzer agent
Analyze = Task(
    description=(
        "a tourist reached out with a requirement: '{user_input}'. "
        "You need to analyze the user input to understand the exact requirement. Extract key details such as "
        "preferred types of places (e.g., tourist attractions, museum, park), location if specified, and any constraints "
        "like family, solo, ratings, or distance. Be precise and structured in your analysis."
    ),
    expected_output=(
        "A structured summary of the user's travel preferences including place types, rating preference, "
        "location (if mentioned), and any other relevant parameters."
    ),
    agent=Analyzer_agent
)


# Define the Recommend task for the Place Recommender agent
recommend = Task(
    description=(
        "You are an expert in recommending travel destinations to tourist. "
        "Based on the user's input: '{user_input}' and the analysis provided by the analyzer_agent, "
        "your goal is to recommend the most suitable places. Consider factors like place types, ratings, "
        "distance, and preferences extracted by the analyzer. Make sure the recommendations are relevant, "
        "well-justified, and formatted clearly."
    ),
    expected_output=(
        "A list of 3-5 highly relevant places, each with a short description and the reason why it matches the user's preferences. "
        "Include key details like name, type, rating, and (IMPORTANT)=> location coordinates (latitude and longitude)."
    ),
    agent=place_recommender_agent
)

# validate=Task(
#     description=("You validate the recommendation outputs "
#                 "check the final answer ,"
#                 "whether it has all the expected_output"
#     ),
#     expected_output=(
#         "A list of 3-5 highly relevant places, each with a short description and the reason why it matches the user's preferences. "
#         "Include key details like name, type, rating, and (IMPORTANT)=> location coordinates (latitude and longitude)."
#     ),
#     agent=Validate_agent
# )

os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["OPENAI_REQUEST_TIMEOUT"] = "60"  # 60 seconds timeout


crew = Crew(
    agents=[Analyzer_agent, place_recommender_agent],
    tasks=[Analyze, recommend],
    verbose=True,  
    memory=False,
    process=Process.sequential  
)


user_input ="i want to go on a date with my girlfriend suggest me some good cafe "

try:
    result = crew.kickoff(inputs={"user_input": user_input})
    print("Success!")
    print(result)
except Exception as e:
    print(f"Error running crew: {str(e)}")