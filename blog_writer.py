import os
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

# Set the API Base URL to OpenRouter
os.environ["OPENAI_API_BASE"] = ""
# Use your OpenRouter API key
os.environ["OPENAI_API_KEY"] = "add your api key"

# Create a chat model
llm = ChatOpenAI(
    model="define your models",  # OpenRouter model name format
    temperature=0.7
)

# Create the Content Planner Agent
planner = Agent(
    role="Content Planner", 
    goal="Plan engaging and factually accurate content in {topic}",
    backstory="You're working on planning a blog article "
               "about the topic: {topic}. "
               "You collect the information that helps the "
               "audience learn something "
               "and make informed decisions. "
               "Your work is the basis for "
               "the content Writer to write an article about this topic",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

writer=Agent(
    role="Writer agent",
    goal="Write insightful and factually accurate "
          "opinion piece about the topic: {topic}",
    backstory="You're working on a writing "
               "a new opinion piece about the work of"
               "the Conent Planner , who provides the outline"
               "and relevent context about the topic"
               "You follow the main objectives and "
               "direction of the outline"
               "as provide by the Content Planner."
               "You also provide objective and impartial insights"
               "and back them up with the information"
               "provided by the Content Planner"
               "you acknowledge in your opinion piece"
               "when your statements in your opinions"
               "as opposed to bojective statements",
      allow_delegation=False,
      verbose=True
)

editor=Agent(
    role="Editor",
    goal="Edit a given blog post to allign with"
          "the writing style of the organizations,",
    backstory="Your an editor who recieves a blog post "
              "from the Content Writer."
              "to ensure it follows journalistic best practices,"
              "provides balanced viewpoints"
              "when providing opinions or assertions,"
              "and also avoids major controversial topics"
              "or opinions wehn possible.",
    allow_delegation=False,
    verbose=True          


)

plan=Task(
    description=(
        "1. Prioritize the latest trends , key players,"
            "and noteworthy news on {topic}.\n"
         "2.Identify the target audience, considering"
          "their intrests and pain points, \n"
          "3. Develop a detailed content outline including"
          "an intoduction ,key points, and a call to action. \n"
          "4. Include SEO keywords and relevant data or sources."
    ),
    expected_output="A comprehensive contnt plan document "
                    "with a outline , audience analysis,"
                    "SEO keywords and resources",
    agent=planner,         
)

write=Task(
    description=(
        "1. Use the content plan to craft a compelling"
            "blog post on {topic}, \n"
        "2. Incorporate SEO keywords naturally. \n"
        "3. Sections/Subtitles are properly named "
            "in a engaging manner. \n"
        "4. Ensure the post is structured with an,"
            "engaging introduction , insightful body,"
            "and a summarizing conclusion, \n"
        "5. proofread for gramatical errors and"
            "allignment with the brand's voice. \n"

            
    ),
    expected_output="A well-written blog post"
                    "in markdown format, ready for publication,"
                    "each section should have 2 or 3 paragraph.",
    agent=writer,
)

edit=Task(
    description=("Proofread the given blog post for grammatical errors and"
                 "alignment with the brand's voice"),
    expected_output="A well-written blog post in markdown format ,"
            "ready for publication,"
            "each section should have 2 or 3 paragraphs",
    agent=editor,             
     
)

# Create the crew with just our planner
crew = Crew(
    agents=[planner, writer, editor],  # Define your agents before this
    tasks=[plan, write, edit],   
    verbose=1
)

# Run the crew for a specific topic
if __name__ == "__main__":
    try:
        topic = input("Enter the topic for your content plan: ")
        result = crew.kickoff(inputs={"topic": topic})
        print("\n\n==== FINAL RESULT ====\n\n")
        print(result)
    except Exception as e:
        print(f"An error occurred: {e}")
