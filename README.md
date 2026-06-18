# 🧠 ResearchMind

### Multi-Agent AI Research System powered by LangChain, LangGraph & Mistral AI


> An autonomous **Multi-Agent Research System** where specialized AI agents collaborate to search the web, extract knowledge, generate publication-quality reports, and critique their own output.

---

# ✨ Features

* 🔍 AI Search Agent using Tavily
* 📖 Reader Agent for deep webpage extraction
* ✍️ Writer Agent for structured research reports
* 🧐 Critic Agent for quality evaluation and scoring
* 🌐 Real-time web research
* 📊 Professional Markdown reports
* 🎯 Modular agent architecture
* 🎨 Interactive Streamlit interface
* 📥 Download generated reports

---

# 🏗️ System Architecture

```text
User Query
      │
      ▼
🔍 Search Agent
      │
      ▼
📖 Reader Agent
      │
      ▼
✍️ Writer Agent
      │
      ▼
🧐 Critic Agent
      │
      ▼
Final Research Report
```

---

# 🛠 Tech Stack

* Python
* LangChain
* LangGraph
* Mistral AI
* Tavily Search API
* BeautifulSoup
* Requests
* Streamlit
* Rich
* Python-dotenv

---

# 📑 Generated Report Includes

* Executive Summary
* Introduction
* Background
* Detailed Analysis
* Comparative Analysis
* Timeline
* Challenges & Risks
* Future Outlook
* Key Insights
* Conclusion
* References

---

# 🚀 Installation

```bash
git clone https://github.com/Shwetanshmishra/Multi-agent-Research-System.git

cd Multi-agent-Research-System

python -m venv multiagent

multiagent\Scripts\activate

pip install -r requirements.txt

streamlit run app.py
```

---

# 🔑 Environment Variables

Create a `.env` file:

```env
MISTRAL_API_KEY=your_key
TAVILY_API_KEY=your_key
```

---

# 📂 Project Structure

```text
app.py
pipeline.py
agents.py
tools.py
requirements.txt
.env.example
.gitignore
README.md
```

---

# 🎯 Future Improvements

* Multi-source parallel scraping
* PDF generation
* Citation management
* Vector database memory
* Research Synthesizer Agent
* Fact Verification Agent
* Export to DOCX/PDF
* Multi-language reports

---

# 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

Fork the repository and submit a pull request.

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Shwetansh Mishra**

* GitHub: https://github.com/Shwetanshmishra


---

⭐ If you found this project useful, consider giving it a star!
