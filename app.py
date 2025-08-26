from fastapi import FastAPI
import requests
import zipfile
import io
from langchain.tools import Tool 
from langchain.prompts import PromptTemplate
from langchain.agents import AgentType, initialize_agent 
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
import chromadb
import uvicorn
from pydantic import BaseModel

load_dotenv()
client = chromadb.Client()
try:
    collection = client.create_collection(name="git_repo_data")
except:
    collection = client.get_collection(name="git_repo_data")


llm = ChatOpenAI(
    model="openai/gpt-oss-20b:free",
    temperature=0,
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url="https://openrouter.ai/api/v1"
)


model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

app = FastAPI(debug=True)

class data(BaseModel):
    prompt:str

def preprocess_document(data , file_path): 
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=256,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False,
    )
    
    chunks = text_splitter.split_text(data)
    for i , item in enumerate(chunks):
        embedding = model.encode(item).tolist()
        collection.add(
            ids=[f"{file_path}_chunk_{i}"],
            metadatas=[{"path": file_path}],
            documents=[item],
            embeddings=[embedding]
        )
    
def fetch_repo_data(owner, repo, branch="main"):
    """Download repo zipball from GitHub."""
    url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"
    headers = {"Accept": "application/vnd.github+json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.content
    return None

def parse_github_url(url: str):
    if url.startswith("https://github.com/"):
        parts = url.replace("https://github.com/", "").split("/")
    else:
        parts = url.split("/")
    if len(parts) >= 2:
        return parts[0], parts[1]
    else:
        raise ValueError("Invalid GitHub URL or format. Use username/reponame")


def fetch_repo(owner, repo, branch="main"):
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
        preprocess_document(file_content , relative_path)
        saved_files += 1
    for_agent = f"Repo  saved with {saved_files} files."
    return  f"Repo saved with {saved_files} files."
    

def get_repo_content(query):
    
    result = collection.query(
        query_texts= query,
        n_results=15
    )
    return result

def fetch_repo_tool(url: str):
    owner, repo = parse_github_url(url)
    return fetch_repo(owner, repo)

tools = [
    Tool(
        name="fetch_repo",
        func=fetch_repo_tool,
        description=(
            "Fetches all files from a GitHub repository given a GitHub URL or username/repo. "
            "It downloads the repo as a zip, extracts each file, splits the content into chunks, "
            "creates embeddings for each chunk, and stores them in the vector database for later retrieval."
        )
    ),
    Tool(
        name="get_repo_content",
        func=get_repo_content,
        description=(
            "Retrieves the most relevant content from a previously fetched repository. "
            "Input should be a natural language query about the repo, such as asking about specific "
            "functions, classes, or documentation. Returns the chunks of code or text that best match the query."
        )
    )
]


memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
template = """You are GitHub Explainer, a versatile AI agent that generates developer-style documentation and interacts with any GitHub repository.

Your role:
- Act as a technical writer, repository mentor, and code analyst.
- Use available tools to fetch, read, and analyze repository files dynamically.
- Produce structured, detailed documentation and answer code-related questions.

Capabilities:
1. Repository Analysis
   - When a new GitHub URL is provided, first fetch the repository using the `fetch_repo` tool.
   - Then use the `get_repo_content` tool to retrieve README.md, Python files, notebooks, or other relevant files.
   - Understand key components including modules, classes, functions, and APIs.

2. Documentation Generation
   - Generate developer-style documentation, not just README summaries.
   - Include:
     * Overview (from README if available)
     * Project structure
     * Modules, classes, and methods
     * Functions / APIs with signature, arguments, return values, and description
     * Usage examples (from code or README)
     * Installation instructions
     * Testing instructions
     * Contribution guidelines
     * License information
   - Always ground documentation in actual repository content.

3. Conversational Q&A
   - Allow the user to "chat with the repo".
   - Retrieve relevant files or sections using `get_repo_content`.
   - Summarize, explain, or refactor code as needed.

Behavior:
- Use Markdown formatting with headings, code blocks, tables, or lists where helpful.
- If information is missing, infer carefully and clearly state assumptions.
- Always fetch the repo first, then query content using `get_repo_content` for any analysis or task.

Repo URL: {input}
Task: {task}
"""

prompt = PromptTemplate(input_variables=["input"], template=template)

repo_agent = initialize_agent(
    llm=llm,
    tools=tools,
    memory=memory,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    prompt = prompt,
    handle_parsing_errors=True
)


@app.post('/chat')
def ai_agent_chat(data: data):
    response = repo_agent.run(data.prompt)
    return {"Response" : response}

if __name__ == "__main__":
    uvicorn.run("app:app",  port=8000, reload=True)
    
    