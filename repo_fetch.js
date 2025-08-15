class GetCodeBase{
    constructor(repo_url){
       this.repo_url = repo_url;
    }

    async fetch_structure() {
    try {
      const response = await fetch(this.repo_url);

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
}