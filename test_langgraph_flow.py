from graph.rag_graph import graph
def test_query(query: str):
    print("\n" + "=" * 60)
    print("QUERY:", query)
    print("=" * 60 + "\n")
 
    result = graph.invoke({
        "query": query
    })
 
    print("ROUTED TO:", result.get("route"))
 
    print("\n--- Retrieved Context Preview ---\n")
    context = result.get("context", "")
    if context:
        print(context[:500])
    else:
        print("No context retrieved.")
 
    print("\n--- Final Answer ---\n")
    print(result.get("answer"))
 
    print("\n" + "=" * 60 + "\n")
 
 
if __name__ == "__main__":
    # SDS-type question
    test_query("What are the safety precautions?")
 
    # TDS-type question
    test_query("What is the stability and reactivity of HEC Liquid Polymer XPT?")