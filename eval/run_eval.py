import json
import sys
import os
import io
import time
from contextlib import redirect_stdout

# Dynamically find the absolute paths for the root and agent directories
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
agent_dir = os.path.join(root_dir, "agent")

# Inject both paths to the front of Python's search list
if agent_dir not in sys.path:
    sys.path.insert(0, agent_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Now Python can find 'tools' inside agent.py, and find 'agent' here!
from agent import run_financial_agent

def evaluate_agent():
    print("Starting Automated RAG Evaluation...\n")
    
    with open('eval/eval_questions.json', 'r') as f:
        test_cases = json.load(f)
        
    passed = 0
    total = len(test_cases)
    
    for case in test_cases:
        print(f"--- Testing Question {case['id']}: {case['type']} ---")
        question = case["question"]
        expected = case["expected_concept"]
        
        f_out = io.StringIO()
        with redirect_stdout(f_out):
            run_financial_agent(question)
        output = f_out.getvalue()
        
        if expected.lower() in output.lower():
            print("✅ PASS\n")
            passed += 1
        else:
            print("❌ FAIL")
            print(f"Expected to find: {expected}")
            print(f"Output received: {output[:300]}...\n")
            
        # Pause to avoid hitting Groq's 8,000 TPM rate limit
        print("Waiting 15 seconds for rate limits to reset...\n")
        time.sleep(15)
            
    print("===============================")
    print(f"FINAL SCORE: {passed}/{total} ({(passed/total)*100:.1f}%)")
    print("===============================")

if __name__ == "__main__":
    evaluate_agent()