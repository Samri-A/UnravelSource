from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentType , initialize_agent  , create_react_agent
from langchain.tools import Tool
from langchain_community.utilities import SerpAPIWrapper
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv()
llm = ChatOpenAI(
    model= "openai/gpt-oss-20b:free",
    temperature= 0, 
    api_key = os.getenv('OPENAI_API_KEY'),
    base_url = "https://openrouter.ai/api/v1"
)
tools = [ ]
search = SerpAPIWrapper(
    serpapi_api_key= os.getenv('search_api'), 

)
search_tools = Tool(
     name = 'websearch',
     func= search.run,
     description="Useful for answering questions about current events or information that requires up-to-date data from the internet."
)
tools.append(search_tools)

input = "recommend me new movie like wednesday"
custom_prompt = """You are a helpful assistant named Jarvis.
             You have access to the following tools:
             {tools}
             Use the following format:
             Question: The user's question
             Thought: Think about how to solve this
             Action: The tool to use, exactly as one of: {tool_names}
             Action Input: Input for the tool
             Observation: The result from using the tool
             ... (this Thought/Action/Action Input/Observation can repeat)
             Thought: I can now provide a final answer
             Final Answer: The final answer to the user's question
             Begin!
             Question: recommend me new movie like wednesday
             
             """
# {agent_scratchpad}
memory = ConversationBufferMemory(memory_key= 'chat_history' , return_messages=True)
agent = initialize_agent(
    llm=llm,
    tools= tools,
    memory = memory ,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose = True
)

result = agent.run(custom_prompt)
print(result)