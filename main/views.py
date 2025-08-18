from django.shortcuts import render
import requests
from .models import files
import zipfile
import io
from langchain.tools import Tool
from langchain.agents import AgentType, initialize_agent
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv
load_dotenv()
llm = ChatOpenAI(
    model= "openai/gpt-oss-20b:free",
    temperature= 0, 
    api_key = os.getenv('OPENAI_API_KEY'),
    base_url = "https://openrouter.ai/api/v1"
)

async def  fetch_repo_data(owner , repo , branch):
    url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"
    headers = {"Accept": "application/vnd.github+json"}
    response = await requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        return None

async def fetch_repo(owner, repo, branch):
    ziped_file = zipfile.ZipFile(io.BytesIO(await fetch_repo_data(owner, repo, branch)))
    for file_name in ziped_file.namelist():
        if file_name.endswith("/"):
            continue
        with ziped_file.open(file_name) as f:
            try:
                content = f.read().decode("utf-8", errors="ignore") 
            except Exception:
                content = ""
    
        relative_path = "/".join(file_name.split("/")[1:])
        files.objects.create(
            repo=repo,
            branch=branch,
            path=relative_path,
            content=content
        )

def agent(input):
    tools = []
    information_tools = Tool(
        name="fetch_repo_data",
        func=fetch_repo_data,
        description="Fetches repository data from GitHub."
    )

    tools.append(information_tools)
    full_repo_tools = Tool(
        name="fetch_repo",
        func=fetch_repo,
        description="Fetches the full repository content from GitHub."
    )

    tools.append(full_repo_tools)

    

    prompt = f""" user: {input}"""
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    agent = initialize_agent(
        llm=llm,
        tools=tools,
        memory=memory, 
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION
    )

    agent_response = agent.run(prompt)

    return agent_response

def chat_view(request):
    return render(request, "chat.html")

def home_view(request):
    return render(request, "welcome_screen.html")