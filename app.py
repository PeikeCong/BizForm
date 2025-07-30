import os
import random
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
from huggingface_hub import InferenceClient
from streamlit.components.v1 import html
from models import SessionLocal, Framework, AnalysisSession, Feedback, init_db
from PyPDF2 import PdfReader
import docx

def extract_text_from_uploaded_file(uploaded_file, file_type):
    if file_type == "txt":
        return uploaded_file.read().decode("utf-8")
    elif file_type == "pdf":
        reader = PdfReader(uploaded_file)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
        return full_text.strip()
    elif file_type == "docx":
        doc = docx.Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    else:
        return ""

# === Load Hugging Face Token ===
try:
    with open("token.txt", "r") as f:
        HF_TOKEN = f.read().strip()
except FileNotFoundError:
    raise RuntimeError("❌ 'token.txt' not found. Please place your Hugging Face token there.")

# === LLaMA Inference Client ===
llama_client = InferenceClient(
    model="meta-llama/Llama-3.1-8B-Instruct",
    api_key=HF_TOKEN,
    provider="auto",
)

# === Initialize DB ===
init_db()
db = SessionLocal()

# === Streamlit App Config ===
st.set_page_config(page_title="BizFormulate", layout="wide")
st.title("📊 Transform Business Notes into Strategic Insights")
st.caption("Powered by Meta LLaMA-3.1 for summarization, frameworks, and strategic suggestions.")

# === Upload ===
uploaded_file = st.file_uploader("📄 Upload Business File (.txt, .pdf, .docx)", type=["txt", "pdf", "docx"])

# === Framework Selection ===
frameworks = db.query(Framework).all()
framework_names = [f.name for f in frameworks] + ["Business Model Canvas"]
framework_dict = {f.name: f for f in frameworks}

selected_framework = st.selectbox("🎯 Choose Business Framework", framework_names)
categories = [
    "Key Partners", "Key Activities", "Value Propositions", "Customer Relationships",
    "Customer Segments", "Key Resources", "Channels", "Cost Structure", "Revenue Streams"
] if selected_framework == "Business Model Canvas" else [c.name for c in framework_dict[selected_framework].categories]

# === Analysis Inputs ===
analysis_depth = st.radio(
    "🧠 Select Analysis Depth:",
    ["Quick", "Standard", "Detailed"],
    index=1,
    horizontal=True
)

perspective = st.slider(
    "🔍 Choose Business Perspective:",
    min_value=0,
    max_value=100,
    value=50,
    help="0 = Operational details, 100 = Big-picture strategy"
)

# === Helper: Call LLaMA ===
def call_llama(prompt):
    completion = llama_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content.strip()

# === Main Logic ===
if uploaded_file:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    input_text = extract_text_from_uploaded_file(uploaded_file, file_extension)
    st.subheader("📄 Uploaded Business Text")
    st.write(input_text[:1000] + "..." if len(input_text) > 1000 else input_text)

    if st.button("🚀 Run Analysis"):
        with st.spinner("🔎 Generating insights..."):
            depth_note = f"This analysis should be {analysis_depth.lower()}."
            perspective_note = (
                f"Consider a {'big-picture strategic' if perspective > 50 else 'detailed operational'} viewpoint."
            )

            summary_prompt = (
                f"Summarize this business text in 3–4 clear sentences.\n{depth_note}\n{perspective_note}\n\n{input_text}"
            )
            summary = call_llama(summary_prompt)

            insights_by_category = {}
            if categories:
                for category in categories:
                    base = f"Analyze this text in relation to the '{category}' block of the Business Model Canvas."
                    if selected_framework == "Business Model Canvas":
                        base += " Please format your response as simple bullet points."
                    else:
                        base = f"As a business consultant, analyze this text focusing on '{category}' in the '{selected_framework}' framework."
                    prompt = f"{base}\n{depth_note}\n{perspective_note}\n\n{input_text}"
                    insight = call_llama(prompt)
                    insights_by_category[category] = insight
            else:
                insights_by_category = None

            suggestion_prompt = (
                f"Based on this text, suggest 3 strategic business actions or next steps.\n{depth_note}\n{perspective_note}\n\n{input_text}"
            )
            suggestions = call_llama(suggestion_prompt)

            session = AnalysisSession(
                input_text=input_text,
                framework=selected_framework,
                result=str(insights_by_category),
                summary=summary,
                suggestions=suggestions,
            )
            db.add(session)
            db.commit()

        st.success("✅ Analysis Complete")

        st.markdown("### 📝 Simple Summary")
        st.info(summary)

        if selected_framework == "Business Model Canvas":
            st.markdown("### 📇 Business Model Canvas Carousel View")
            carousel_html = '''<div style="display: flex; overflow-x: auto; scroll-snap-type: x mandatory; gap: 1rem; padding: 1rem; -webkit-overflow-scrolling: touch;">'''
            for key, value in insights_by_category.items():
                carousel_html += f"""
                <div style="flex: 0 0 350px; scroll-snap-align: start; background: #fdfdfd; padding: 1.2rem; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); height: 300px; overflow-y: auto;">
                    <h4 style="margin-top:0">{key}</h4>
                    <p style="white-space: pre-wrap;">{value}</p>
                </div>
                """
            carousel_html += "</div>"
            html(carousel_html, height=360)

        else:
            st.markdown("### 📊 Framework-Based Insights")
            if insights_by_category:
                for cat, text in insights_by_category.items():
                    with st.expander(f"🔹 {cat}"):
                        st.write(text)
            else:
                st.warning("No categories defined for this framework.")

        st.markdown("### 💡 Strategic Suggestions")
        st.write(suggestions)

        st.markdown("### 🕸️ Strategic Profile Overview")
        business_dimensions = ["Market Potential", "Feasibility", "Differentiation", "Scalability", "Risk"]
        scores = [round(random.uniform(60, 95), 1) for _ in business_dimensions]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=scores,
            theta=business_dimensions,
            fill='toself',
            name='Strategic Profile',
            hovertemplate="<b>%{theta}</b><br>Score: %{r}%<extra></extra>"
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            margin=dict(l=30, r=30, t=30, b=30)
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 🙋 User Feedback")
        feedback_col1, feedback_col2 = st.columns([1, 3])
        with feedback_col1:
            user_feedback = st.radio("Was this analysis helpful?", ["👍 Yes", "👎 No"], key="global_feedback")
        with feedback_col2:
            user_note = st.text_area("Leave a comment (optional)", placeholder="e.g., The summary is accurate, but the suggestions feel too generic.")

        if st.button("Submit Feedback"):
            st.success("✅ Thanks for your feedback!")
            db.add(Feedback(
                session_id=session.id,
                thumb=user_feedback,
                note=user_note,
                timestamp=datetime.utcnow()
            ))
            db.commit()

        download_content = f"""
Framework: {selected_framework}
Analysis Depth: {analysis_depth}
Perspective: {perspective}

--- INPUT TEXT ---
{input_text}

--- SUMMARY ---
{summary}

--- FRAMEWORK INSIGHTS ---
{insights_by_category}

--- STRATEGIC SUGGESTIONS ---
{suggestions}
"""
        st.download_button(
            label="💾 Download This Analysis",
            data=download_content.strip(),
            file_name="current_session.txt",
            mime="text/plain"
        )

# === Sidebar: Past Sessions ===
with st.sidebar:
    st.markdown("### 🕘 Previous Sessions")
    past_sessions = db.query(AnalysisSession).order_by(AnalysisSession.id.desc()).limit(5).all()
    for s in past_sessions:
        with st.expander(f"📂 {s.framework} Session #{s.id}", expanded=False):
            st.markdown("**📝 Summary:**")
            st.info(s.summary or "_No summary available._")
            st.markdown("**💡 Suggestions:**")
            st.write(s.suggestions or "_No suggestions available._")
            st.markdown("**📊 Framework-Based Insights:**")
            st.write(s.result or "_No insights available._")

            feedback = db.query(Feedback).filter_by(session_id=s.id).first()
            if feedback:
                st.markdown(f"**🙋 User Feedback:** {feedback.thumb}")
                if feedback.note:
                    st.caption(f"💬 {feedback.note}")
            st.download_button(
                label="⬇️ Download This Session",
                data=f"""
Framework: {s.framework}

--- INPUT TEXT ---
{s.input_text}

--- SUMMARY ---
{s.summary}

--- FRAMEWORK INSIGHTS ---
{s.result}

--- SUGGESTIONS ---
{s.suggestions}
""".strip(),
                file_name=f"session_{s.id}.txt",
                mime="text/plain"
            )
