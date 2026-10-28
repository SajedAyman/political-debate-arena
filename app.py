import os
import gradio as gr
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Use two distinct model IDs available to your free Groq account.
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GOVERNMENT_MODEL = os.getenv("GOVERNMENT_MODEL", "openai/gpt-oss-20b").strip()
OPPOSITION_MODEL = os.getenv("OPPOSITION_MODEL", "llama-3.3-70b-versatile").strip()
MAX_ROUNDS = 10

GOVERNMENT_PROMPT = """You are the GOVERNMENT side in a structured, educational political debate.
Your role is to defend the current government's policies in the specified country, while remaining honest.
Rules:
- Give a clear, relevant argument and respond to the other side's latest argument.
- Use verifiable data and statistics where possible. Name the metric, year, and source.
- Prefer reputable sources such as the World Bank (data.worldbank.org), IMF (imf.org),
  national statistical agencies, UN agencies, OECD (oecd.org), and official budget reports.
- Never invent a statistic, quote, source, or URL. If you cannot verify a figure from your knowledge,
  say so and make a qualitative argument instead.
- Distinguish established facts from interpretation, and acknowledge meaningful weaknesses or uncertainty.
- Do not claim to represent or speak for a real government. This is a simulated debate role.
- Keep the response between 100 and 180 words. Be civil; no insults or inflammatory rhetoric.
- End with a short “Sources to check:” list of relevant source names/URLs when you can provide them."""

OPPOSITION_PROMPT = """You are the OPPOSITION side in a structured, educational political debate.
Your role is to challenge the current government's policies in the specified country, while remaining honest.
Rules:
- Give a clear, relevant argument and respond to the government's latest argument.
- Use verifiable data and statistics where possible. Name the metric, year, and source.
- Prefer reputable sources such as the World Bank (data.worldbank.org), IMF (imf.org),
  national statistical agencies, UN agencies, OECD (oecd.org), and official audit/budget reports.
- Never invent a statistic, quote, source, or URL. If you cannot verify a figure from your knowledge,
  say so and make a qualitative argument instead.
- Distinguish established facts from interpretation, and acknowledge meaningful weaknesses or uncertainty.
- Do not claim to represent or speak for a real opposition party. This is a simulated debate role.
- Keep the response between 100 and 180 words. Be civil; no insults or inflammatory rhetoric.
- End with a short “Sources to check:” list of relevant source names/URLs when you can provide them."""

def ask_model(client, model, system_prompt, country, topic, round_number, previous):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": (
            f"Country: {country}\n"
            f"Debate topic: {topic}\n"
            f"Round: {round_number} of {MAX_ROUNDS}\n\n"
            f"Conversation so far:\n{previous or 'This is the opening statement. Set out your position on the topic.'}\n\n"
            "Make your next contribution. Do not repeat the entire conversation."
        )}
    ]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.5,
        max_tokens=450,
    )
    return response.choices[0].message.content.strip()

def start_debate(country, topic, rounds):
    country = (country or "").strip()
    topic = (topic or "").strip()
    if not country:
        raise gr.Error("Please enter a country.")
    if not topic:
        raise gr.Error("Please enter a debate topic.")
    if not GROQ_API_KEY:
        raise gr.Error(
            "Missing GROQ_API_KEY. Create a free Groq API key, then add it to a local .env file. "
            "Never commit .env or share your key."
        )

    try:
        client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )
        transcript = []
        max_rounds = max(1, min(int(rounds), MAX_ROUNDS))

        for round_number in range(1, max_rounds + 1):
            prior = "\n\n".join(
                f"{item['speaker']} (Round {item['round']}): {item['text']}"
                for item in transcript
            )
            government_text = ask_model(
                client, GOVERNMENT_MODEL, GOVERNMENT_PROMPT,
                country, topic, round_number, prior
            )
            transcript.append({
                "round": round_number,
                "speaker": "🏛️ Government",
                "text": government_text,
            })

            prior = "\n\n".join(
                f"{item['speaker']} (Round {item['round']}): {item['text']}"
                for item in transcript
            )
            opposition_text = ask_model(
                client, OPPOSITION_MODEL, OPPOSITION_PROMPT,
                country, topic, round_number, prior
            )
            transcript.append({
                "round": round_number,
                "speaker": "🗣️ Opposition",
                "text": opposition_text,
            })

        rendered = []
        for item in transcript:
            rendered.append(
                f"## Round {item['round']} — {item['speaker']}\n\n{item['text']}"
            )
        rendered.append(
            "\n---\n**Important:** This is a simulated AI debate, not a verified news report. "
            "Language models can make mistakes; check the listed sources before relying on statistics."
        )
        return "\n\n".join(rendered)
    except gr.Error:
        raise
    except Exception as exc:
        raise gr.Error(
            f"The model request failed: {exc}\n\n"
            "Check that your API key is valid, both model IDs are available to your account, "
            "and your free-tier rate limits have not been exceeded."
        )

with gr.Blocks(title="Political Debate Arena", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        "# 🏛️ Political Debate Arena\n"
        "### Two LLMs • Government vs Opposition • Evidence-led discussion\n\n"
        "Choose a country and topic. Two different language models will debate in alternating turns. "
        "A round contains one government statement and one opposition response."
    )
    with gr.Row():
        country = gr.Textbox(
            label="Country",
            placeholder="e.g., Egypt, United States, France",
            value="Egypt",
        )
        topic = gr.Textbox(
            label="Debate topic",
            placeholder="e.g., economic policy, education, healthcare",
            value="Economic policy and cost of living",
        )
    rounds = gr.Slider(
        minimum=1, maximum=MAX_ROUNDS, step=1, value=3,
        label="Number of rounds (maximum 10)",
        info="Each round contains two LLM responses.",
    )
    run_button = gr.Button("Start debate", variant="primary")
    output = gr.Markdown(label="Debate transcript")
    run_button.click(
        fn=start_debate,
        inputs=[country, topic, rounds],
        outputs=output,
    )
    gr.Markdown(
        "---\n"
        "**Research note:** Prompts instruct both models not to invent statistics and to name credible sources. "
        "The app does not independently verify every claim. Always cross-check important figures."
    )

if __name__ == "__main__":
    demo.launch()
