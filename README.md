# Political Debate Arena

A Gradio application where two different LLMs simulate a political debate about a country selected by the user:

- **Government LLM** — defends government policies.
- **Opposition LLM** — challenges government policies.
- **Evidence-led prompts** — ask for statistics, years, and credible sources, and instruct models not to invent facts.
- **Round limit** — the interface allows 1–10 rounds maximum. Each round contains one statement from each side.
- **API-key safety** — keys are read from a local `.env` file and are not stored in source code.

> This is an educational simulation. Model-generated claims and citations may be wrong and should be checked independently.

## Technology

- Python
- Gradio UI
- Groq API with two distinct model IDs (free developer access is subject to provider availability and rate limits)
- OpenAI-compatible Python client

## 1. Get an API key

1. Create an account at [Groq Console](https://console.groq.com/).
2. Create an API key in the console.
3. Do not share the key, add it to screenshots, or commit it to GitHub.

Provider free-tier access, model availability, and limits can change.

## 2. Install and configure

Python 3.10 or newer is recommended.

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
```

Edit `.env` and replace the placeholder with your own key:

```dotenv
GROQ_API_KEY=your_real_key_here
GOVERNMENT_MODEL=openai/gpt-oss-20b
OPPOSITION_MODEL=llama-3.3-70b-versatile
```

If a model ID is not available to your account, replace it with an active model ID shown in the [Groq supported models list](https://console.groq.com/docs/models). Use two distinct model IDs.

## 3. Run the application

```bash
python app.py
```

Open the local Gradio URL printed in the terminal (usually `http://127.0.0.1:7860`).

## 4. Test it

Try:
- Country: `Egypt`
- Topic: `Economic policy and cost of living`
- Rounds: `2`

Confirm that the transcript alternates between Government and Opposition and that each side provides arguments and source suggestions.

## 5. Upload to GitHub safely

1. Create a **public** repository on GitHub, for example `political-debate-arena`.
2. Ensure `.env` contains your real key locally, and `.env.example` contains only a placeholder.
3. In the project folder, run:

```bash
git init
git add app.py requirements.txt README.md .env.example .gitignore
git status
```

4. Before committing, confirm `.env` is **not** listed in the staged files. If it is, run `git rm --cached .env` and check `.gitignore`.
5. Commit and push:

```bash
git commit -m "Build two-LLM political debate app with Gradio"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/political-debate-arena.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. Submit the resulting repository URL to your instructor.

## Design overview

The application passes the country, topic, round number, and prior transcript to each LLM. The government model responds first; the opposition model receives the conversation, including the latest government statement, and replies. The process repeats up to the selected number of rounds.

## Limitations

- The model is prompted to use reliable sources, but this app does not perform independent fact-checking or live web retrieval.
- Free API usage has rate limits and model availability can change.
- Political roles are simulated and do not represent actual parties or officials.
