import asyncio
import requests
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
    model="openai/gpt-oss-20b:free",
    temperature=0,
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url="https://openrouter.ai/api/v1"
)


def fetch_repo_data(owner, repo, branch="main"):
    """Download repo zipball from GitHub."""
    url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"
    headers = {"Accept": "application/vnd.github+json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.content
    return None


def fetch_repo(tool_input=None):
    branch="main"
    owner = "Samri-A"
    repo = "first-contributions"
    content = fetch_repo_data(owner, repo, branch)
    if not content:
        return f" Failed to fetch {owner}/{repo}@{branch}"

    ziped_file = zipfile.ZipFile(io.BytesIO(content))
    saved_files = 0
    for file_name in ziped_file.namelist():
        if file_name.endswith("/"):
            continue
        with ziped_file.open(file_name) as f:
            try:
                file_content = f.read().decode("utf-8", errors="ignore")
            except Exception:
                file_content = ""
        relative_path = "/".join(file_name.split("/")[1:])
        with open("file.txt", "a", encoding="utf-8") as f:
            f.write(f"\n### {relative_path}\n{file_content}")
        saved_files += 1
    print(f"✅ Repo {owner}/{repo}@{branch} saved with {saved_files} files.")


def get_repo_content(tool_input=None):
    with open("file.txt", "r", encoding="utf-8") as f:
        output = f.read()
    return output[:2000]  # Return first 10,000 characters for brevity


# --- Agent ---
def agent():
    url = "github.com/Samri-A/first-contributions"
    prompt = f""" You are GitHub Explainer, an AI agent that helps users generate documentation and interact with GitHub repositories.
            
            Your role:
            - Act as a technical writer + repo mentor.
            - Use available tools to fetch, read, and analyze repository files.
            - Generate structured documentation and answer questions conversationally.
            
            Capabilities:
            1. Repository Analysis
               - Use tools to list files, read code, and summarize repository structure.
               - Understand key components (modules, classes, functions, APIs).
            
            2. Documentation Generation
               - Produce README-style documentation including:
                 * Project overview
                 * Installation and setup steps
                 * Usage examples
                 * API / function documentation
                 * Contribution guidelines
                 * License information
            
            3. Conversational Q&A
               - Let the user "chat with the repo."
               - When asked about code, retrieve relevant files or sections using tools.
               - Summarize, explain, or refactor code as needed.
               - If user asks for enhancements (tests, tutorials, scripts), generate useful examples grounded in repo content.
            
            4. Behavior
               - Always ground answers in actual repo content (via tools).
               - If repo lacks info, infer carefully and state assumptions clearly.
               - Use Markdown formatting for explanations (headings, code blocks, lists).
               - Be concise, developer-friendly, and practical.
            
            Guidelines:
            - Default to explaining code simply and clearly.
            - Always use tools when repo content is needed.
            - Never invent functions or files that don’t exist in the repo.
            - Be proactive in suggesting useful insights (e.g., “This repo looks like a Flask app; here’s how you can run it.”).
            
            Your identity: GitHub Explainer — an AI assistant for exploring, documenting, and chatting with repositories.
             user: prepare me a documentation for this repository {url}"""
    tools = [
        # Tool(
        #     name="fetch_repo",
        #     func=fetch_repo,
        #     description="Fetches and saves repo content."
        # ),
        Tool(
            name="get_repo_content",
            func=get_repo_content,
            description="Get Fetched repo content."
        )
    ]

    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)

    repo_agent = initialize_agent(
        llm=llm,
        tools=tools,
        memory=memory,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True
    )

    return repo_agent.run(prompt)



import asyncio
async def main():
    response = await agent()
    print(response)

if __name__ == "__main__":
    response =  agent()
    print(response)
  