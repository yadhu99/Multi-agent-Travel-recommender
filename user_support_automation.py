import os
from crewai import Agent, Task, Crew,tools
from scrapper import CustomScrapeWebsiteTool
from langchain_openai import ChatOpenAI
from IPython.display import Markdown

# Set the API Base URL to OpenRouter
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
# Use your OpenRouter API key
os.environ["OPENAI_API_KEY"] = "Add your api key"

# Create a chat model
llm = ChatOpenAI(
    model="define your model",  # OpenRouter model name format
    temperature=0.7
)

head=Agent(
    role="Senior Support Representative",
    goal="Be the most friendly and helpful"
          "Senior Represnetative in your team",
    backstory=(
                "You work at StackOverflow(https://stackoverflow.com/questions/tagged/python) and "
                "now working on providing "
                "support to {customer}, a super important customer to the company"
                "you need to make sure that you provide best support !"
                "Ensuring that you provide all the information that a customer asks for,"
                "Make sure to provide full complete answers,"
                "and make no assumptions"

    ),
    allow_delegation=False,
    verbose=True
)

support_quality_agent=Agent(
    role="Support Quality Assurance Specialist",
    goal="Get recognition for providing the best support quality assurance with your team",
    backstory=(
                "You work at StackOverflow(https://stackoverflow.com/questions/tagged/python) and "
                "now working on providing "
                "on request from {customer} ensuring that "
                "the support reprsentative is"
                "providing the best support possible. \n"
                "You need to amke sure that the support representative is providing full"
                "complete answers, and make no assumptions"


    ),
    
    verbose=True
)

docs_scrape_tool = CustomScrapeWebsiteTool(
    website_url="https://stackoverflow.com/questions/tagged/python"
)


# Use the tool
scraped_content = docs_scrape_tool.run()
print(scraped_content)

@tools.tool

def scrape_website(url=None):


    """Scrape content from a website."""
    tool = CustomScrapeWebsiteTool(website_url=url)
    return tool.run()

enquiry_resolution=Task(
    description=(
        "{customer} just reached out with a super important question:\n"
	    "{inquiry}\n\n"
        "{person} from {customer} is the one that reached out. "
		"Make sure to use everything you know "
        "to provide the best support possible."
		"You must strive to provide a complete "
        "and accurate response to the customer's inquiry."
    ),
    expected_output=(
	    "A detailed, informative response to the "
        "customer's inquiry that addresses "
        "all aspects of their question.\n"
        "The response should include references "
        "to everything you used to find the answer, "
        "including external data or solutions. "
        "Ensure the answer is complete, "
		"leaving no questions unanswered, and maintain a helpful and friendly "
		"tone throughout."
        
        
    ),
    tools=[scrape_website],
    agent=head
)

quality_assurance_review = Task(
    description=(
        "Review the response drafted by the Senior Support Representative for {customer}'s inquiry. "
        "Ensure that the answer is comprehensive, accurate, and adheres to the "
		"high-quality standards expected for customer support.\n"
        "Verify that all parts of the customer's inquiry "
        "have been addressed "
		"thoroughly, with a helpful and friendly tone.\n"
        "Check for references and sources used to "
        " find the information, "
		"ensuring the response is well-supported and "
        "leaves no questions unanswered."
    ),
    expected_output=(
        "A final, detailed, and informative response "
        "ready to be sent to the customer.\n"
        "This response should fully address the "
        "customer's inquiry, incorporating all "
		"relevant feedback and improvements.\n"
		"Don't be too formal, we are a chill and cool company "
	    "but maintain a professional and friendly tone throughout."
    ),
    agent=support_quality_agent,
)

crew = Crew(
  agents=[head,support_quality_agent],
  tasks=[enquiry_resolution, quality_assurance_review],
  verbose=1,
  memory=True
)

inputs = {
    
    "customer": "TechLearners",
    "person": "Manisha",
    "inquiry": "explain me python errors that may likely occur"

}
result = crew.kickoff(inputs=inputs)
print(result.raw)



