# from django.shortcuts import render
# import requests
# from .models import files
# import zipfile
# import io
# from langchain.tools import Tool
# from langchain.agents import AgentType, initialize_agent
# from langchain_openai import ChatOpenAI
# from langchain.memory import ConversationBufferMemory
# import os
# from dotenv import load_dotenv
# load_dotenv()
# llm = ChatOpenAI(
#     model= "openai/gpt-oss-20b:free",
#     temperature= 0, 
#     api_key = os.getenv('OPENAI_API_KEY'),
#     base_url = "https://openrouter.ai/api/v1"
# )

# def  fetch_repo_data(owner , repo , branch):
#     url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"
#     headers = {"Accept": "application/vnd.github+json"}
#     response = requests.get(url, headers=headers)
#     if response.status_code == 200:
#         return response.content
#     else:
#         return None
# def get_repo_content(repo, branch):
#     return files.filter(repo=repo, branch=branch)


# def fetch_repo(owner, repo, branch):
#     ziped_file = zipfile.ZipFile(io.BytesIO(fetch_repo_data(owner, repo, branch)))
#     for file_name in ziped_file.namelist():
#         if file_name.endswith("/"):
#             continue
#         with ziped_file.open(file_name) as f:
#             try:
#                 content = f.read().decode("utf-8", errors="ignore") 
#             except Exception:
#                 content = ""
    
#         relative_path = "/".join(file_name.split("/")[1:])
#         files.objects.create(
#             repo=repo,
#             branch=branch,
#             path=relative_path,
#             content=content
#         )

# def agent(input):
#     tools = []
#     information_tools = Tool(
#         name="fetch_repo_data",
#         func=fetch_repo_data,
#         description="Fetches repository data from GitHub."
#     )

#     tools.append(information_tools)
#     full_repo_tools = Tool(
#         name="fetch_repo",
#         func=fetch_repo,
#         description="Fetches the full repository content from GitHub to save to database."
#     )

#     tools.append(full_repo_tools)
#     get_repo_content_tools = Tool(
#         name="get_repo_content",
#         func=get_repo_content,
#         description="Fetches the repository content from the database."
#     )

#     tools.append(get_repo_content_tools)

#     prompt = f""" You are GitHub Explainer, an AI agent that helps users generate documentation and interact with GitHub repositories.
            
#             Your role:
#             - Act as a technical writer + repo mentor.
#             - Use available tools to fetch, read, and analyze repository files.
#             - Generate structured documentation and answer questions conversationally.
            
#             Capabilities:
#             1. Repository Analysis
#                - Use tools to list files, read code, and summarize repository structure.
#                - Understand key components (modules, classes, functions, APIs).
            
#             2. Documentation Generation
#                - Produce README-style documentation including:
#                  * Project overview
#                  * Installation and setup steps
#                  * Usage examples
#                  * API / function documentation
#                  * Contribution guidelines
#                  * License information
            
#             3. Conversational Q&A
#                - Let the user "chat with the repo."
#                - When asked about code, retrieve relevant files or sections using tools.
#                - Summarize, explain, or refactor code as needed.
#                - If user asks for enhancements (tests, tutorials, scripts), generate useful examples grounded in repo content.
            
#             4. Behavior
#                - Always ground answers in actual repo content (via tools).
#                - If repo lacks info, infer carefully and state assumptions clearly.
#                - Use Markdown formatting for explanations (headings, code blocks, lists).
#                - Be concise, developer-friendly, and practical.
            
#             Guidelines:
#             - Default to explaining code simply and clearly.
#             - Always use tools when repo content is needed.
#             - Never invent functions or files that don’t exist in the repo.
#             - Be proactive in suggesting useful insights (e.g., “This repo looks like a Flask app; here’s how you can run it.”).
            
#             Your identity: GitHub Explainer — an AI assistant for exploring, documenting, and chatting with repositories.
#              user: {input}"""
#     memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
#     agent = initialize_agent(
#         llm=llm,
#         tools=tools,
#         memory=memory, 
#         agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION
#     )

#     agent_response = agent.run(prompt)

#     return agent_response


# def home_view(request):
#     return render(request, "welcome_screen.html")


# def explain_repo_view(request):
#     if request.method == "POST":
#         repo_link = request.POST.get("repoLink")
#         response = agent(repo_link)
#         return render(request, "chat.html", {"response": response})
#     return render(request, "welcome_screen.html")

from django.shortcuts import render
import requests
from .models import files  # ✅ Model class should be singular & capitalized
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

# --- Repo Tools ---
def fetch_repo_data(owner, repo, branch="main"):
    """Download repo zipball from GitHub."""
    url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"
    headers = {"Accept": "application/vnd.github+json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.content
    return None


def fetch_repo(owner, repo, branch="main"):
    """Extract repo files and save to DB."""
    content = fetch_repo_data(owner, repo, branch)
    if not content:
        return f"❌ Failed to fetch {owner}/{repo}@{branch}"

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
        files.objects.create(
            repo=repo,
            branch=branch,
            path=relative_path,
            content=file_content
        )
        saved_files += 1
    return f"✅ Repo {owner}/{repo}@{branch} saved with {saved_files} files."


def get_repo_content(repo, branch="main"):
    """Return concatenated repo content from DB."""
    qs = files.objects.filter(repo=repo, branch=branch)
    if not qs.exists():
        return f"❌ No repo content found for {repo}@{branch}"
    output = []
    for f in qs:
        output.append(f"\n### {f.path}\n{f.content[:1000]}")  # limit to avoid huge context
    return "\n".join(output)


# --- Agent ---
def agent(user_input: str):
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
             user: {user_input}"""
    tools = [
        Tool(
            name="fetch_repo_data",
            func=lambda x: "Downloaded bytes" if fetch_repo_data(**eval(x)) else "Failed",
            description="Fetches repository data from GitHub. Input must be a dict string: {'owner': 'user', 'repo': 'repo', 'branch': 'main'}"
        ),
        Tool(
            name="fetch_repo",
            func=lambda x: fetch_repo(**eval(x)),
            description="Fetches and saves repo content. Input: {'owner': 'user', 'repo': 'repo', 'branch': 'main'}"
        ),
        Tool(
            name="get_repo_content",
            func=lambda x: get_repo_content(**eval(x)),
            description="Get repo content from DB. Input: {'repo': 'repo', 'branch': 'main'}"
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


# --- Django Views ---
def home_view(request):
    return render(request, "welcome_screen.html")


def explain_repo_view(request):
    if request.method == "POST":
        repo_link = request.POST.get("repoLink")
        response = agent({"input": "prepare me a documentation", "repo": repo_link})
        return render(request, "chat.html", {"response": response})
    return render(request, "welcome_screen.html")
