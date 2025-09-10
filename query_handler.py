import os
import json
import pickle
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def load_vector_store():
    """Loads the FAISS vector store from the local file."""
    try:
        with open("faiss_vector_store.pkl", "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None


def structure_query(query: str):
    """
    Uses an LLM to parse a natural language query into a structured JSON format.

    Args:
        query: The user's natural language query.

    Returns:
        A Python dictionary with the structured query details.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

    prompt = PromptTemplate(
        input_variables=["query"],
        template="""
        You are an expert at parsing and structuring user queries related to insurance claims, contracts, or policies.
        Extract the key details from the following query and return them as a clean JSON object.
        The keys should be in snake_case.

        Example:
        Query: "46-year-old male, knee surgery in Pune, 3-month-old insurance policy"
        Output: {{
            "age": 46,
            "gender": "male",
            "procedure": "knee surgery",
            "location": "Pune",
            "policy_duration_months": 3
        }}

        Now, parse the following query:
        Query: "{query}"
        Output:
        """
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(query=query)

    try:
        # Clean the response to ensure it's valid JSON
        json_response = response.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(json_response)
    except json.JSONDecodeError:
        return {"error": "Failed to parse query into JSON.", "raw_response": response}


def get_relevant_clauses(query: str, vector_store):
    """
    Searches the vector store for clauses relevant to the query.

    Args:
        query: The user's query.
        vector_store: The loaded FAISS vector store.

    Returns:
        A list of relevant text chunks (clauses).
    """
    if vector_store is None:
        return []

    # Perform similarity search
    docs = vector_store.similarity_search(query, k=5)
    return [doc.page_content for doc in docs]


def generate_final_decision(structured_query: dict, relevant_clauses: list):
    """
    Generates the final decision based on the query and relevant clauses.

    Args:
        structured_query: The parsed query as a dictionary.
        relevant_clauses: A list of relevant clauses from the documents.

    Returns:
        A dictionary containing the final decision, amount, and justification.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1, convert_system_message_to_human=True)

    clauses_text = "\n\n".join([f"Clause {i + 1}:\n{clause}" for i, clause in enumerate(relevant_clauses)])

    prompt_template = """
    You are an expert claims processing agent. Your task is to make a decision based on a user's situation and the provided policy clauses.
    Analyze the user's details and evaluate them against the relevant clauses.

    **User's Details:**
    ```json
    {query_details}
    ```

    **Relevant Policy Clauses:**
    ```
    {clauses}
    ```

    **Your Task:**
    1.  Carefully read each clause and determine if it applies to the user's situation.
    2.  Based on your analysis, decide whether the claim should be "Approved", "Rejected", or "Pending Review".
    3.  If a payout amount is mentioned or can be calculated from the clauses, state the amount. If not applicable, set the amount to "N/A".
    4.  Provide a clear justification for your decision, explicitly referencing the clause number(s) (e.g., "as per Clause 2 and Clause 4") that support your reasoning.

    **Output Format:**
    Return your response as a single, valid JSON object with the following keys:
    - "decision": (string) "Approved", "Rejected", or "Pending Review"
    - "amount": (string or number) The calculated payout amount or "N/A"
    - "justification": (string) A detailed explanation of the decision, referencing specific clauses.

    **Example Response:**
    {{
        "decision": "Approved",
        "amount": "N/A",
        "justification": "The policy covers knee surgery after a waiting period of 24 months as per Clause 3. Since the user's policy is 36 months old, the procedure is covered."
    }}

    Now, generate the response for the given details and clauses.
    """

    prompt = PromptTemplate(
        input_variables=["query_details", "clauses"],
        template=prompt_template
    )

    chain = LLMChain(llm=llm, prompt=prompt)

    response = chain.run({
        "query_details": json.dumps(structured_query, indent=2),
        "clauses": clauses_text
    })

    try:
        # Clean and load the JSON response
        json_response = response.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(json_response)
    except json.JSONDecodeError:
        return {"error": "Failed to generate a valid JSON decision.", "raw_response": response}


def process_query(query: str):
    """

    Main handler to process a user query from start to finish.
    """
    # 1. Load the vector store
    vector_store = load_vector_store()
    if vector_store is None:
        return {"error": "Vector store not found. Please process documents first."}

    # 2. Structure the user's query
    structured_query = structure_query(query)
    if "error" in structured_query:
        return structured_query

    # 3. Retrieve relevant clauses
    relevant_clauses = get_relevant_clauses(query, vector_store)
    if not relevant_clauses:
        return {"error": "Could not find any relevant clauses in the documents for this query."}

    # 4. Generate the final decision
    final_decision = generate_final_decision(structured_query, relevant_clauses)

    # 5. Add retrieved clauses to the final output for transparency
    final_decision['retrieved_clauses'] = relevant_clauses

    return final_decision