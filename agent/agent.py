import os
import json
from groq import Groq
from tools import FINAGENT_TOOLS, query_database, search_documents

# Initialize the Groq Client
client = Groq(api_key="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")


SYSTEM_PROMPT = """
You are FinAgent, an elite financial intelligence assistant.

CRITICAL OPERATIONAL RULES:
1. CITATIONS: Always provide transparent, audit-ready citations. Cite specific table names for DB queries, and exact filenames/page numbers for document searches.
2. COMPARISONS & CROSS-DOCUMENT QUERIES: If a question asks you to compare two different companies (e.g., Maybank vs CIMB) or different periods, you MUST execute separate, dedicated tool calls for each entity. Do not attempt to merge them into one search query.
3. DATA ABSENCE: If the requested information is not found in the database or the documents, you must not guess. You MUST explicitly include the exact phrase "I lack the data" in your final response.
4. BEHAVIOR: Do not output raw text tags like <function>. Use native tool choices.
"""

def run_financial_agent(user_query: str):
    print(f"\n🚀 User Query: {user_query}")
    print("-" * 50)
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]
    
    # Upgrade to a multi-turn agent loop (max 5 iterations to prevent infinite loops)
    for iteration in range(5):
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            tools=FINAGENT_TOOLS,
            tool_choice="auto",
            max_tokens=1500
        )
        
        response_message = response.choices[0].message
        
        # Did the model decide to use a tool?
        if response_message.tool_calls:
            # Append the assistant's tool request to the conversation history
            messages.append(response_message)
            
            # Execute each tool request
            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                if tool_name == "query_database":
                    result_str = query_database(sql_query=tool_args["sql_query"])
                elif tool_name == "search_documents":
                    result_str = search_documents(query=tool_args["query"], top_k=tool_args.get("top_k", 3))
                else:
                    result_str = f"Error: Tool {tool_name} not recognized."
                    
                # Append the result of the Python function back to the LLM
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_name,
                    "content": result_str,
                })
        else:
            # The model answered without needing tools (or finished its research)
            print("\n🤖 FinAgent Response:")
            print(response_message.content)
            return # Exit the loop and the function
            
    print("\n🤖 FinAgent Response:")
    print("Agent stopped: Reached maximum iterations without providing a final answer.")

if __name__ == "__main__":
    sample_prompt = (
        "Compare Maybank's 2024 revenue from our database with what their "
        "annual report document says about their credit risk strategy."
    )
    run_financial_agent(sample_prompt)