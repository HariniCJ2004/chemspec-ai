from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)


class Planner:
    """Planner wrapper used by the graph.

    Provides a `route_query(query: str) -> str` method that returns
    either 'TDS' or 'SDS'.
    """

    def route_query(self, query: str) -> str:
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
            temperature=0,
        )

        # Normalize the model output
        classification = response.choices[0].message.content.strip()
        classification = classification.upper()
        if "TDS" in classification:
            return "TDS"
        if "SDS" in classification:
            return "SDS"
        # Fallback: default to SDS if unsure
        return "SDS"