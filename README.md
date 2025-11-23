# The Sentinel AI Concierge: The Autonomous Multi-Cluster Orchestrator Agent 🤖

## Agents Intensive - Capstone Project | Track: Concierge Agents

### Overview 🌐

This project, developed for the Google AI Agents Intensive Capstone, is an intelligent AI Chatbot designed to solve the challenge of **Modern life management is critically fragmented. Users constantly switch between single-purpose applications (e.g., a travel app, a recipe planner, a banking portal) to handle multi-step, multi-domain tasks. This lack of centralized intelligence leads to constant context switching, wasted time, and cognitive overload. Traditional AI assistants often fail at complex queries because they lack the necessary specialized architectural depth.**.

The **Sentinel AI Concierge: The Autonomous Multi-Cluster Orchestrator** acts as a complex, multi-step agent, utilizing **Multi-agent system** (Tool Use) for real-time data retrieval and a proprietary **RAG System (Retrieval-Augmented Generation)** for deep contextual knowledge. This architecture allows it to accurately and efficiently answer multi-faceted user queries in a single, cohesive response.

### Core Agentic Features ✨

| Feature | Description | Technical Implementation |
| :--- | :--- | :--- |
| **Function Calling (Tool Use)** | The agent is equipped with external tools to fetch up-to-the-minute, real-time data that is not in the LLM's training set. | Uses the Gemini API's function calling capability to reason on user intent and dynamically call the `Multi-agent system` or `Agent deployment` functions. |
| **RAG System (Knowledge Base)** | Provides deep access to a private, non-public corpus of documents for domain-specific, contextual answers. | A Vector Database is used to retrieve the most relevant document snippets, which are then passed to the LLM as grounding context. |
| **Complex Reasoning & Synthesis** | The agent executes a multi-step plan (combining tool call + RAG lookup) and fuses the different data sources into a single, comprehensive, and grounded response. | This is the core agentic behavior, demonstrating an understanding of context, tool-dependency, and information synthesis. |

### Technical Architecture 🧠

The agent's decision flow, powered by the Gemini model, ensures that it uses the right resource at the right time:

1.  **User Query:** The prompt is received by the agent orchestrator.
2.  **LLM Planning:** The Gemini model analyzes the request to determine if it requires external data (Tool Call) or internal context (RAG).
3.  **Parallel Execution:** Both Function Calls and RAG queries are executed as necessary.
    * **Tool Call:** `Multi-agent system` is executed, and raw JSON data is returned.
    * **RAG:** A query is sent to the Vector DB, and context-rich text chunks are retrieved.
4.  **Final Generation:** The LLM receives the raw tool output, the RAG context, and the original user query, and synthesizes them to produce the final, definitive answer.

### Setup & Installation 🛠️

To run the project locally, please ensure you have Python 3.9+ and the required packages.

1.  **Clone the Repository:**
    ```bash
    git clone [YOUR_GITHUB_REPO_URL_HERE]
    cd [YOUR_REPO_FOLDER_NAME]
    ```

2.  **Set up the Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt 
    # (Ensure requirements.txt lists dependencies like google-genai, etc.)
    ```

4.  **Configure API Key:**
    * Set your Gemini API key as an environment variable:
        ```bash
        export GEMINI_API_KEY="YOUR_API_KEY_HERE"
        ```

5.  **Run the Application:**
    ```bash
    python app.py
    ```
    The application will typically be accessible at `http://127.0.0.1:8000`.

### Example Usage 💬

The true capability of the agent is demonstrated with a combined query that necessitates both tool use and RAG:

| Prompt | Agent Action | Expected Result |
| :--- | :--- | :--- |
| **"What is the current [Tool 1] status right now, and how does that relate to the 'Key Risks' section we outlined in the document about the [Project Topic]?"** | 1. Calls `[Function 1 Name]` tool. 2. Executes a RAG search. 3. Synthesizes both results. | A single, comprehensive answer that includes the real-time data point and a contextual summary from the proprietary document. |

### Project Structure 📂

* `app.py`: The main file containing the agent orchestration, function definitions, and core Gemini API logic.
* `index.html`: The simple frontend interface for user interaction.

### Features Work 🚀

* **Multi-agent system**: Implementing a self-correction mechanism to validate tool outputs before responding to the user.
* **Sessions & Memory**: Integrating a user-specific long-term memory module to maintain personalized context across sessions.

***
