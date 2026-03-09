# 🧠 Cognitive Guardian

Cognitive Guardian is a project I built to explore how AI can help people think more clearly about difficult decisions.

Many AI tools answer questions, but they rarely help users **reflect on decisions, emotions, and possible outcomes**.  
This project attempts to combine **AI reasoning, psychological context, and decision simulation** to provide more thoughtful guidance.

The system analyzes a user’s situation, estimates emotional pressure and risk, simulates alternative decision paths, and suggests helpful learning resources.

---

# 💡 What the Project Does

When a user describes a situation, the system:

1. Understands the emotional and cognitive context of the problem  
2. Estimates pressure and potential risk levels  
3. Simulates how different decisions might play out  
4. Provides personalized guidance in different tones (coach, mentor, etc.)  
5. Recommends relevant learning videos using semantic search  

The goal is not to replace human judgment but to **help people slow down and think through complex choices more clearly.**

---

# 🚀 Key Features

### 🧠 Cognitive Analysis
The system uses LLM reasoning to analyze the user’s situation and estimate:

- Emotional pressure
- Decision risk
- Overall confidence
- Emotional summary

Instead of using rule-based logic, the analysis is generated dynamically through LLM reasoning.

---

### 🔮 Decision Simulation

One of the core ideas of the project is **counterfactual thinking**.

Users can simulate different decision scenarios such as:

- If I continue my current path
- If I wait 3 months
- If I had done this 3 months ago

This helps explore how choices could affect emotional state, confidence, and future outcomes.

---

### 🎭 Persona-Based Guidance

Users can choose how the system communicates with them.

Available tones:

- 🧑‍🏫 Coach
- 🧠 Therapist
- 🎯 Strict Mentor
- 🤝 Friend

The reasoning stays the same, but the **communication style adapts**.

---

### 📺 Semantic Video Recommendations

To help users learn more about their situation, the system recommends YouTube videos.

Instead of simple keyword search, the project uses:

- semantic embeddings
- similarity matching
- reranking logic
- LLM verification

Each result includes a thumbnail, title, and relevance score.

---

### 🔍 Smart Query Rewriting

User input is often emotional and long.

The system converts that into a clean search query before retrieving videos.

Example:

User input:

```
I feel anxious before interviews and haven't given one in years
```

Converted query:

```
overcome interview fear after long gap
```

This improves recommendation accuracy significantly.

---

# 🏗 How the System Works

```
User Input
     ↓
LLM Cognitive Analysis
     ↓
Decision Simulation
     ↓
Persona-based Guidance
     ↓
Query Rewriting
     ↓
Semantic Video Search
     ↓
Reranking + LLM Verification
     ↓
Personalized Suggestions
```

---

# 🛠 Tech Stack

**Language**
- Python

**Framework**
- Streamlit

**AI / ML**
- OpenRouter LLM API
- Sentence Transformers
- Semantic similarity search

**Libraries**
- sentence-transformers
- requests
- streamlit
- regex utilities

---

# 📦 Running the Project

Clone the repository:

```bash
git clone https://github.com/yourusername/cognitive-guardian.git
cd cognitive-guardian
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run streamlit_app.py
```

Open the app at:

```
http://localhost:8501
```

---

# 🧪 What I Learned Building This

While building this project I explored:

- LLM prompt design for reasoning tasks
- counterfactual decision simulation
- semantic search and reranking
- designing AI systems that are **human-centered instead of purely technical**
- building interactive AI interfaces with Streamlit

It was an interesting experiment in combining **AI reasoning with real human decision contexts.**

---
