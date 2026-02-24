from openai import AzureOpenAI
import os
from dotenv import load_dotenv
 
load_dotenv()
 
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
 
def Planner(query):
    prompt = f"""
    Classify this query into:
    - TDS (technical data)
    - SDS (safety related)
 
    Query: {query}
 
    Answer only TDS or SDS.
    """
 
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
 
    return response.choices[0].message.content.strip()