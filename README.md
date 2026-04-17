# song_analyzer

# 🎵 Song Meaning Analyzer

An AI-powered CLI application that analyzes song lyrics and extracts structured insights such as emotions, themes, narrative perspective, and symbolic meaning.

This project demonstrates how to integrate LLMs into a structured data pipeline — transforming unstructured text (lyrics) into machine-readable JSON outputs.

---

## 🚀 Project Overview

The goal of this project is to:

- Take raw song lyrics as input
- Analyze them using an LLM (OpenAI API)
- Extract meaningful structured information
- Save results for further processing or analysis

This is not just a text generator — it is designed as a **mini AI system** with:

- Input pipeline
- Prompt engineering layer
- Structured output enforcement
- Storage layer (raw + parsed outputs)

---

## 🧠 What This Project Demonstrates

This project is built to showcase skills relevant to **AI Systems Architecture**:

- Prompt design for structured outputs (JSON schema enforcement)
- Handling unstructured → structured data transformation
- Building reproducible pipelines for LLM-based systems
- File-based data workflows (inputs → outputs)
- Separation of concerns (loader, config, main logic)

---

## 🏗️ System Flow

[Song Lyrics (.txt)]
↓
Loader Module
↓
Prompt Construction
↓
OpenAI API Call
↓
Raw LLM Output
↓
Saved to /outputs/raw
↓
(Optional parsing/validation)
↓
Saved to /outputs/parsed

Think of it like a mini ETL pipeline:

- **Extract** → Load lyrics
- **Transform** → LLM analysis
- **Load** → Save structured results

---

## 📁 Project Structure

song-meaning-analyzer/
│
├── data/
│ └── songs/
│ ├── song1.txt
│ └── song2.txt
│
├── output/
│ ├── raw/
│ ├── parsed/
│ └── evaluation/
│
├── src/
│ ├── main.py --> orchestration only
│ ├── config.py --> defaults and settings
│ ├── models.py --> structure of the data /schema
│ ├── prompts.py --> contains the prompt template
│ ├── file_manager.py --> files and paths : read lyrics, creates output filename, saves json, finds the laste 10 raw files, creates files if they dont exist
│ ├── analyzer.py --> llm interation
│ ├── aggregator.py --> raw jsons as inputs -> statistics/summaries as outputs
│ ├── evaluator.py --> quality checks of system
│ └── utils.py --> helpful things that do not go anywhere else
│
├── .env
├── requirements.txt
└── README.md

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/VasilikiPapadimou/song_analyzer.git
cd song_analyzer
2. Create virtual environment
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows
3. Install dependencies
pip install -r requirements.txt
4. Set your API key

Create a .env file or configure in config.py:

OPENAI_API_KEY=your_api_key_here
▶️ Usage
Add song lyrics as .txt files inside:
data/songs/
Run the application:
python src/main.py
Outputs will be generated in:
outputs/raw/ → raw LLM response
outputs/parsed/ → structured JSON
📄 Example Output
{{
  "song_title": "Example Song",
  "artist": "Unknown",
  "dominant_emotions": ["melancholy","nostalgia"],
  "emotional_arc": "Starts reflective, builds to emotional intensity, ends in acceptance",
  "main_themes": ["loss","memory","identity"],
  "narrator_perspective": "first_person",
  "key_symbols_or_images": ["rain","empty streets"],
  "interpretation_summary": "A reflection on past relationships and emotional growth",
  "evidence_lines": [
    "I walk alone through the rain",
    "Echoes of what we became"
  ],
  "ambiguities_or_uncertainties": "Unclear if the narrator seeks closure or remains stuck",
  "confidence_note": "Moderate confidence due to metaphor-heavy lyrics"
}}
```
