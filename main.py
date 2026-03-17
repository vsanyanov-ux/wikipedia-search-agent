from agent import app
from langchain_core.messages import HumanMessage
import sys
import io

# Ensure UTF-8 output for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def run_query(query: str):
    print(f"\n--- Processing Query: {query} ---")
    inputs = {"messages": [HumanMessage(content=query)]}
    
    # We use stream to see the steps
    for output in app.stream(inputs):
        for key, value in output.items():
            print(f"\nNode: {key}")
            # Identify what to print based on node type
            if "messages" in value:
                last_msg = value["messages"][-1]
                if hasattr(last_msg, "content"):
                    print(f"Content: {last_msg.content}")
                if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                    print(f"Tool Calls: {last_msg.tool_calls}")

if __name__ == "__main__":
    # Тест 1: Простой вопрос
    run_query("What is the capital of France?")
    
    # Тест 2: Запрос, который должен вызвать инструмент
    run_query("Who is the CEO of Nvidia in 2024?")
    
    # Тест 3: Неоднозначный запрос для проверки логики восстановления
    run_query("Tell me about the planet Mercury.")
