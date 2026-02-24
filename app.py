import os
from dotenv import load_dotenv
from graph.rag_graph import graph   
 
load_dotenv()

 
def run_app():
    print("\n==============================")
    print("   CHEMSPEC RAG ASSISTANT")
    print("==============================\n")
 
    print("Type 'exit' to quit.\n")
 
    while True:
        query = input("Ask your question: ")
 
        if query.lower() in ["exit", "quit"]:
            print("\nExiting...")
            break
 
        try:
            result = graph.invoke({
                "query": query
            })
 
            print("\n--------------------------------")
            print(" Routed To:", result.get("route"))
            print("--------------------------------\n")
 
            print("Answer:\n")
            print(result.get("answer"))
 
            print("\n================================\n")
 
        except Exception as e:
            print("\n Error occurred:")
            print(e)
 
 
if __name__ == "__main__":
    run_app()