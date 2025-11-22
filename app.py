import os
import time
import sys
import json
from google import genai
from google.genai.errors import APIError 
from flask import Flask, render_template, request, jsonify, session

# IMPORTANT: Set a secret key for session management (history saver)
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "your_super_secret_key_for_history_saver")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = SECRET_KEY

# --- 0. Mock Classes and Custom Tools (for robust offline testing) ---

class MockClient:
    """A placeholder client used when the actual API key is not found."""
    def __init__(self):
        self.models = type('MockModels', (object,), {'generate_content': self._mock_generate_content})

    def _mock_generate_content(self, model, contents, config=None):
        """Mocks a structured response for independent agents."""
        if "generate a prioritized list" in contents:
            text = "Mock Research: 1. Budget flights; 2. Budget lodging; 3. Ideal destinations (Paris)."
        elif "Evaluate the previous state" in contents:
            text = "Next Task in Sequence"
        elif "7-day meal plan" in contents:
            text = "Mock Meal Plan: Day 1: Chicken/Broccoli. Day 2: Veggie Soup. Day 3-7: Low-carb meals."
        elif "navigate a database of resources" in contents:
            text = "Resource Found: Local Hotline (1-800-555-HELP). Nearest Clinic: 5km. Online Support Group: Link."
        elif "double-check the accuracy and safety" in contents:
            text = "Verification: PASSED. Output is safe and directly addresses the query."
        elif "Use the built-in Google Search tool" in contents:
            text = "Search Result: The sky is blue because the Earth's atmosphere scatters blue light more than red light."
        else:
            text = "General Agent: I am currently running in Mock Client mode, but I understand your request!"
            
        return type('MockResponse', (object,), {'text': text})

# Custom Tool 1: Inventory Database (for Culinary Agent)
class InventoryDBTool:
    """Mock database tool to retrieve ingredients."""
    def run(self):
        print(f"  -> [CulinaryAgent] Used Custom Tool: InventoryDBTool. Data: chicken, broccoli, rice, one onion.")
        return "Ingredients: chicken, broccoli, rice, one onion, butter, milk."

# Long Term Memory
class LongTermMemoryDB:
    """Mock database for user preferences."""
    def get_user_preferences(self):
        print(f"  -> [CulinaryAgent] Retrieved Long-Term Memory: Vegetarian, prefers low-carb, no nuts.")
        return "Vegetarian, prefers low-carb, no nuts."

# Simulated Built-in Tool: Google Search (for General Agent)
class SearchAgent:
    """Simulates a call to a built-in tool (e.g., Google Search) for general questions."""
    def process(self, query, client):
        print(f"  -> [SearchAgent] Using built-in tool for query: '{query}'")
        prompt = f"Use the built-in Google Search tool to find the answer to the following question: {query}"
        try:
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            return response.text
        except Exception as e:
            return f"Search Agent failed: {e}"


class MetricLogger:
    """Simple class for Observability: Logging, Tracing, Metrics"""
    @staticmethod
    def log(key, value=1):
        if "latency" in key:
            print(f"METRIC LOGGED: {key}={value:.3f}s")
        else:
            print(f"METRIC LOGGED: {value}")


# --- 1. Independent Core Agent Definitions (LLM-Powered) ---

# --- Life Admin Executor Agents (Loop Pattern) ---
class TaskManagerAgent:
    def process(self, previous_state, client):
        print(f"  -> [TaskManagerAgent] Evaluating previous state: '{previous_state}' autonomously...")
        prompt = f"Evaluate the previous state: '{previous_state}'. If the state mentions 'Approval Complete', respond ONLY with 'Task Complete'. If the state mentions 'Awaiting external service', respond ONLY with 'Proceed to Approval'. Otherwise, respond ONLY with 'Next Task in Sequence'."
        try:
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            decision = response.text.strip()
            return decision
        except Exception:
            return "Next Task in Sequence" 

class PassportApprovalAgent:
    def run(self):
        print("[Passport_Approval_Wait] Agent PAUSED (Long-Running Operation simulated)...")
        time.sleep(0.001) 
        print("[Passport_Approval_Wait] Agent RESUMED. Task complete.")
        return "Passport Approval Complete."

# --- Dynamic Meal Planner Agent (Memory/Tooling Pattern) ---
class CulinaryAgent:
    def process(self, memory_data, inventory_data, client):
        print(f"  -> [CulinaryAgent] Generating 7-day meal plan autonomously...")
        prompt = (
            f"Generate a creative 7-day meal plan. Memory/Preferences: {memory_data}. Inventory: {inventory_data}. "
            "Prioritize using inventory first, then adhering to preferences. Respond with a concise 7-day plan."
        )
        try:
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            return response.text
        except Exception as e:
            return f"Culinary Agent failed: {e}"

# --- Hyper-Personalized Travel Planner Agents (Sequential Pattern) ---
class ResearcherAgent:
    def process(self, query, client):
        print(f"  -> [ResearcherAgent] Setting research goals autonomously...")
        prompt = f"Analyze the user request: '{query}'. Generate a prioritized list of 3 key research goals needed to create the full itinerary. Return the list as a bulleted list."
        try:
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            return response.text
        except Exception as e:
            return f"Research failed: {e}"

class LogisticsAgent:
    def process(self, research_data, client):
        print(f"  -> [LogisticsAgent] Processing research data into logistics autonomously...")
        prompt = f"Based on the following research data:\n---\n{research_data}\n---\n Formulate a conceptual logistics plan. Specify the main destination city and a budget range for accommodations. Respond concisely."
        try:
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            return response.text
        except Exception as e:
            return f"Logistics failed: {e}"

class ItineraryAgent:
    def process(self, logistics_data, client):
        print(f"  -> [ItineraryAgent] Generating final itinerary autonomously...")
        prompt = f"Based on the following logistics plan:\n---\n{logistics_data}\n---\nCreate a detailed 3-day itinerary for the specified city, including one main sight for each day. Respond concisely."
        try:
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            return response.text
        except Exception as e:
            return f"Itinerary failed: {e}"

# --- Mental Health Resource Navigator Agent (Agents for Good Track) ---
class MentalHealthAgent:
    def process(self, user_query, client):
        print("  -> [MentalHealthAgent] Analyzing distress cues and navigating resource database autonomously...")
        prompt = (
            f"The user has expressed distress with the query: '{user_query}'. Act as a resource navigator. "
            "Provide general knowledge for *immediate help* and *local services*. "
            "Output the resource type, a generic phone number (like 988 or 1-800-273-TALK), and generic online support link. "
            "Crucially: Include a strong safety disclaimer that you are an AI and not a substitute for professional help. "
        )
        try:
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            return response.text
        except Exception as e:
            return f"Mental Health Resource Navigation failed: {e}"

# --- 2. Meta Agent Definition ---
class VerificationAgent:
    def process(self, original_query, core_agent_output, client):
        print("  -> [VerificationAgent] Double-checking core agent output for safety and accuracy...")
        prompt = (
            f"You are a safety and quality assurance layer. Double-check the accuracy and safety of the 'Agent Output' "
            f"against the 'Original Query'.\n\nOriginal Query: '{original_query}'\nAgent Output: '{core_agent_output}'\n\n"
            "Respond ONLY with 'Verification: PASSED. [Brief Reason]' or 'Verification: FAILED. [Brief Reason]'. "
            "Be especially careful with outputs from the Mental Health Agent."
        )
        try:
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            return response.text.strip()
        except Exception as e:
            return f"Verification: FAILED. Internal check error: {e}"


# --- 3. Cluster Definitions ---
class AdminCluster:
    def execute(self, user_query, client):
        current_state = "Initial Request Received"
        for i in range(5): 
            if "Task loop completed" in current_state: break
            decision = TaskManagerAgent().process(current_state, client)
            if "Task Complete" in decision: current_state = "Task loop completed."
            elif "Proceed to Approval" in decision: current_state = PassportApprovalAgent().run()
            elif "Next Task in Sequence" in decision: current_state = "Passport renewal broken down. Awaiting external service."
            else: current_state = f"Decision unclear. Loop stopped at iteration {i}."
        return f"Goal '{user_query}' processed. Final State: {current_state}"

class CulinaryCluster:
    def execute(self, user_query, client):
        memory_data = LongTermMemoryDB().get_user_preferences()
        inventory_data = InventoryDBTool().run()
        return CulinaryAgent().process(memory_data, inventory_data, client)

class TravelCluster:
    def execute(self, user_query, client):
        research_output = ResearcherAgent().process(user_query, client)
        logistics_output = LogisticsAgent().process(research_output, client) 
        return ItineraryAgent().process(logistics_output, client)

class MentalHealthCluster:
    def execute(self, user_query, client):
        return MentalHealthAgent().process(user_query, client)


# --- 4. Orchestrator Definition ---

class SentinelOrchestrator:
    def __init__(self, client):
        self.admin_cluster = AdminCluster()
        self.culinary_cluster = CulinaryCluster()
        self.travel_cluster = TravelCluster()
        self.health_cluster = MentalHealthCluster()
        self.verification_agent = VerificationAgent()
        self.client = client

    def route_request(self, user_query):
        start_time = time.time()
        print("\n[TRACE START] SentinelOrchestrator.route_request")
        
        domain = None
        lower_query = user_query.lower()

        # 1. Specialized Intent Classification (Routing)
        if "renew" in lower_query or "passport" in lower_query or "admin" in lower_query:
            domain = "Admin"
        elif "meal plan" in lower_query or "fridge" in lower_query or "cook" in lower_query or "recipe" in lower_query:
            domain = "Culinary"
        elif "travel" in lower_query or "trip" in lower_query or "vacation" in lower_query or "plan" in lower_query or "itinerary" in lower_query:
            domain = "Travel"
        elif "distress" in lower_query or "anxiety" in lower_query or "help" in lower_query or "hotline" in lower_query or "emergency" in lower_query or "overwhelmed" in lower_query:
            domain = "Health"
        
        core_output = None
        
        # 2. Execute Core Agent/Cluster
        if domain is not None:
            cluster_start_time = time.time()
            try:
                if domain == "Admin":
                    core_output = self.admin_cluster.execute(user_query, self.client)
                elif domain == "Culinary":
                    core_output = self.culinary_cluster.execute(user_query, self.client)
                elif domain == "Travel":
                    core_output = self.travel_cluster.execute(user_query, self.client)
                elif domain == "Health":
                    core_output = self.health_cluster.execute(user_query, self.client)
            except Exception as e:
                core_output = f"CLUSTER FAILED: {domain} agent execution error: {e}"
            MetricLogger.log(f"latency.{domain}Cluster.execute", time.time() - cluster_start_time)

        # 3. General Agent (Fallback)
        else:
            MAX_RETRIES = 2 
            for attempt in range(MAX_RETRIES):
                try:
                    # General Agent uses SearchAgent (Built-in Tool) for factual queries
                    core_output = SearchAgent().process(user_query, self.client)
                    break
                except Exception as e:
                    core_output = f"GENERAL AGENT FAILED: Unexpected error: {e}"
                    break
        
        # 4. Verification Step (Running the Meta-Agent)
        verification_result = self.verification_agent.process(user_query, core_output, self.client)
        
        # 5. Final Result Assembly
        final_title = f"Verified Response from {domain if domain else 'General'} Agent"
        final_output = f"**{final_title}**\n\n{core_output}\n\n---\n*Verification Agent Feedback*\n{verification_result}"

        MetricLogger.log("latency.SentinelOrchestrator.route_request", time.time() - start_time)
        print("[TRACE END] SentinelOrchestrator.route_request")
        
        return final_output

# --- 5. Flask Routes and Setup ---

# Global variable to hold the initialized orchestrator and client
GLOBAL_ORCHESTRATOR = None
GLOBAL_CLIENT = None

def initialize_global_resources():
    """
    Initializes the Gemini client and the orchestrator once.
    This replaces the deprecated @app.before_first_request.
    """
    global GLOBAL_CLIENT, GLOBAL_ORCHESTRATOR
    
    # Crucial check to ensure single initialization
    if GLOBAL_ORCHESTRATOR is not None:
        return

    API_KEY = os.environ.get("GEMINI_API_KEY")

    if not API_KEY:
        print("FATAL: GEMINI_API_KEY not found. Using Mock Client.")
        GLOBAL_CLIENT = MockClient()
    else:
        try:
            GLOBAL_CLIENT = genai.Client(api_key=API_KEY) 
            print("✅ Gemini Client initialized.")
        except Exception as e:
            print(f"Error initializing Gemini client: {e}. Falling back to Mock Client.")
            GLOBAL_CLIENT = MockClient()

    GLOBAL_ORCHESTRATOR = SentinelOrchestrator(GLOBAL_CLIENT)
    print("🚀 Sentinel Orchestrator initialized.")

# Call the initialization function immediately before running the app
# The Flask run command will now execute this before starting the server loop.
initialize_global_resources()


@app.route("/")
def index():
    """Renders the HTML chat interface."""
    # Initializes history if it doesn't exist (History Saver)
    if 'history' not in session:
        session['history'] = []
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Handles the user query, processes it through the agent system, and saves history."""
    try:
        data = request.get_json()
        user_query = data.get("message", "").strip()

        if not user_query:
            return jsonify({"error": "No message provided."}), 400

        # Run the multi-agent system
        agent_response_text = GLOBAL_ORCHESTRATOR.route_request(user_query)

        # Update History Saver (Flask Session)
        history = session.get('history', [])
        history.append({"user": user_query, "agent": agent_response_text})
        session['history'] = history
        
        # Return the response to the front-end
        return jsonify({"response": agent_response_text})

    except Exception as e:
        print(f"Flask Chat Error: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

@app.route("/history", methods=["GET"])
def get_history():
    """Retrieves the conversation history for the front-end to display."""
    # The history is saved and loaded automatically via the session
    return jsonify({"history": session.get('history', [])})

if __name__ == "__main__":
    print("\nStarting Sentinel AI Concierge Web Server...")
    print("Access the interface at http://127.0.0.1:5000/")
    app.run(debug=True) # Use debug=False for production