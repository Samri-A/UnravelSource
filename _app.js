require('dotenv').config();
const repo = 'LLMs-from-scratch';
const owner = 'rasbt'; 
const OpenAI =  require('openai');
const openai = new OpenAI({
  baseURL: "https://openrouter.ai/api/v1",
  apiKey: process.env.Open_route_key,
  
});


const tools_ =  [
    {
        "type": "function",
        "function": {
            "name": "fetch_structure",
            "description": "Get the current time in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_url": {
                        "type": "string",
                        "description": "The repo url"
                    }
                },
                "required": ["repo_url"]
            }
        }
    }
]

async function fetch_structure(repo_url) {
    try {
      const response = await fetch(repo_url);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log(data);
      return data; 
    } catch (error) {
      console.error('Error fetching repository:', error);
      throw error;
    }
  }
// var options = {
//     method: 'GET',
//   headers: {
//     'Authorization': process.env.token,
//     'Accept': 'application/vnd.github.v3+json'
//   }
// };

// async function file_content_read(data , path){
//     try{
//     const file_res = await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/${data[path]["path"]}`)
//     const file_data = await file_res.json();
//     try{
//         const fileContentEncoding =  file_data.encoding;
//         let fileContent = file_data.content;  
//        if (fileContentEncoding === 'base64') {
//         const decodedContent = atob(fileContent);  
//         console.log(data[path]["path"])
//       // console.log(decodedContent);
//     }}
//     catch{
//         for(var i = 0; i < file_data.length; i++){
          
//      console.log(i);
//     //await file_content_read(data , path);
    
//     }
// }
//    }
//     catch(e){
//         console.log(e);

//     }
// }
async function main_(){
//     try{
//     const  fetch_repo = await fetch(`https://api.github.com/repos/${owner}/${repo}/contents`);
//     if (!fetch_repo.ok) {
//       throw new Error(`HTTP error! status: ${fetch_repo.status}`);
//     }
//      data = await fetch_repo.json();
//      //console.log(data);
//      for(var path = 0; path < data.length; path++){
          
//      //console.log(path);
//     await file_content_read(data , path);
    
    
//     }
//     }catch(error) {
//     console.error('Error fetching repository:', error);
//   }



fetch(`https://api.github.com/repos/${owner}/${repo}/git/trees/main?recursive=1`)

  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  })
  .then(data => {
    console.log(data);
     return data;
  })
  .catch(error => {
    console.error('Error fetching repository:', error);
    
  });
    

}
var github_data = fetch_structure(`https://api.github.com/repos/${owner}/${repo}/git/trees/main?recursive=1`)

async function main() {
  const completion = await openai.chat.completions.create({
    model: "openai/gpt-oss-20b:free",
    messages: [
      {
        "role": "system",
        "content": `You are an intelligent AI code assistant that deeply understands GitHub repositories. When given a GitHub repo URL, you:
         
         Fetch the full structure and content of the repository using the GitHub API without cloning.
         
         Extract and parse file contents, prioritizing source code files (e.g., .py, .js, .java, .md, .json, etc.).
         
         Summarize the purpose and functionality of each file and major component.
         
         Generate high-quality documentation, including README summaries, architecture overviews, and code-level explanations.
         
         Create semantic embeddings from file contents and store them in a production-ready graph or vector database to enable real-time retrieval.
         
         Allow interactive conversations where users can ask about the repo’s purpose, logic, dependencies, architecture, and more.
         
         Be concise, technical, and always explain based on actual code logic, function definitions, and project structure.
         
         You must:
         
         Be aware of file hierarchies and relationships between components.

         Use dependency inference and comment/code analysis to provide insightful explanations.
         
         Avoid hallucinations; only respond based on what’s in the codebase.
         
         Use memory-efficient and production-grade techniques for data fetching, embedding, and storage.
         
         Your goal is to help developers, product teams, and learners understand any GitHub repo in seconds.
         
         `
      },{
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": `https://api.github.com/repos/${owner}/${repo}/git/trees/main?recursive=1`
          }
        ]
      }
      

    ],
    tools : tools_
    
  });

  console.log(completion.choices[0].message);
}

main();