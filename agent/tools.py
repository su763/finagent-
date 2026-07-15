import json
import sqlite3
import chromadb

def query_database(sql_query: str) -> str:
    """Executes a SQL query against the SQLite database."""
    print(f"\n[Executing SQL]: {sql_query}")
    try:
        conn = sqlite3.connect("data/financials.db")
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        conn.close()
        
        result = [dict(row) for row in rows]
        if not result:
            return "Query executed successfully, but returned no results."
        return json.dumps(result)
    except Exception as e:
        return f"Error executing SQL: {str(e)}"

def search_documents(query: str, top_k: int = 3) -> str:
    """Searches the local ChromaDB vector store for document chunks."""
    print(f"\n[Searching docs]: '{query}' (top_k={top_k})")
    try:
        client = chromadb.PersistentClient(path="data/chroma_db")
        collection = client.get_collection(name="financial_docs")
        
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        formatted_results = []
        if results and 'documents' in results and results['documents']:
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            
            for doc, meta in zip(documents, metadatas):
                formatted_results.append({
                    "source": meta.get("source", "Unknown Document"),
                    "page": meta.get("page", "Unknown Page"),
                    "content": doc
                })
                
        if not formatted_results:
            return "No matching document segments found."
            
        return json.dumps(formatted_results)
    except Exception as e:
        return f"Error searching documents: {str(e)}"

# Groq/OpenAI standard tool schemas
FINAGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": "Run a SQL query against the structured financial database. The database has one table named 'company_financials' with columns: id (INTEGER), company_name (TEXT), fiscal_year (INTEGER), quarter (TEXT), revenue_billion (REAL), net_income_billion (REAL), total_assets_billion (REAL).",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": "The exact SQLite query to execute."
                    }
                },
                "required": ["sql_query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": "Search unstructured financial documents (annual reports, 10-Ks) for qualitative context, risk evaluations, and corporate strategy.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The key concept or question to match against document chunks."
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of relevant text blocks to retrieve. Default is 3."
                    }
                },
                "required": ["query"]
            }
        }
    }
]