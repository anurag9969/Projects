import gradio as gr
from agents.listener import analyze
from agents.recommender import recommend
from utils.youtube import search_youtube

def run(text, urgency, reversibility):

    result = analyze(text, urgency, reversibility)

    pressure = result["pressure"]
    verdict = result["verdict"]
    advice = result["advice"]

    rec = recommend(text, hobby="")   # ✅ prevent crash
    videos = search_youtube(rec["youtube"])

    yt = ""
    for v in videos:
        yt += f"▶️ {v['title']} ({v['match']}%)\n{v['url']}\n\n"

    return f"""
🧠 Pressure Score: {pressure}/100
⚖️ Verdict: {verdict}
💡 Advice: {advice}

💬 Support:
{rec['support']}

🎬 Recommendations:
Movie: {rec['movie']}
Song: {rec['song']}
Activity: {rec['activity']}

📺 YouTube Videos:
{yt}
"""

with gr.Blocks(title="Cognitive Guardian") as demo:
    gr.Markdown("# 🧠 Cognitive Guardian")

    text = gr.Textbox(label="Describe your situation", lines=4)
    urgency = gr.Slider(1,5,value=3,label="Urgency")
    reversibility = gr.Slider(1,5,value=3,label="Reversibility")

    btn = gr.Button("Analyze")
    output = gr.Textbox(lines=18)

    btn.click(run, [text, urgency, reversibility], output)

demo.launch(share=True)
