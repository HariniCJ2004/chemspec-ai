from agents.retrieval_agent import retrieve
 
context = retrieve("What are the hazards?", "SDS")
 
print("Retrieved Context:\n")
print(context[:1000])