require('dotenv').config();
const OpenAI = require('openai');

const owner = 'rasbt';
const repo = 'LLMs-from-scratch';
const tools_ =  [
    {
        "type": "function",
        "function": {
            "name": "fetch_structure",
            "description": "Get the current time in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "The repo owner"
                    },
                    "repo": {
                        "type": "string",
                        "description": "The repo name"
                    }
                },
                "required": [ "owner" ,"repo" ]
            }
        }
    }
]

const openai = new OpenAI({
  baseURL: "https://openrouter.ai/api/v1",
  apiKey: process.env.Open_route_key,
});

async function fetchStructure(owner, repo) {
  const url = `https://api.github.com/repos/${owner}/${repo}/git/trees/main?recursive=1`;
  const res = await fetch(url, {
    headers: { 'Accept': 'application/vnd.github.v3+json' }
  });
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return res.json();
}

async function main() {
  try {
    const structure = await fetchStructure(owner, repo);

    const completion = await openai.chat.completions.create({
      model: "openai/gpt-oss-20b:free",
      messages: [
        {
          role: "system",
          content: `You are an intelligent AI code assistant that deeply understands GitHub repositories. When given a GitHub repo owner name and repo name, you:
         
         Fetch the full structure and content of the repository using the GitHub API without cloning.
         
         Extract and parse file contents, prioritizing source code files (e.g., .py, .js, .java, .md, .json, etc.).
         
         Summarize the purpose and functionality of each file and major component.
         
         Generate high-quality documentation, including README summaries, architecture overviews, and code-level explanations.
         `
        },
        {
          role: "user",
          content: `Here is the owner name ${owner} and the repo name ${repo}. Please fetch the repository structure and provide a detailed summary of its contents, including file types, purposes, and any relevant documentation.`
        },
        
      ],
      tools: tools_,
      tool_choices : ["auto"],
    });

    console.log(completion.choices[0].message.content);

  } catch (err) {
    console.error("Error:", err);
  }
}

main();
