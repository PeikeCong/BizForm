# BizFormulate
BizFormulate is a Streamlit-based AI assistant that transforms unstructured business notes into structured strategic insights. It supports multiple frameworks like Business Model Canvas, SWOT, and Porter’s Five Forces. Users can upload text or documents, receive AI-generated analysis via LLaMA 3.1, and provide feedback for future improvement. Past sessions and insights are stored in a local SQLite database for review and download.

## 📺 Demo Video

[![Watch the demo](https://img.youtube.com/vi/nNZafFBTywY/hqdefault.jpg)](https://youtu.be/nNZafFBTywY)


## Features

- Upload text, PDF, or Word files for processing
- Choose from strategic frameworks: Business Model Canvas, SWOT, Porter’s Five Forces
- LLaMA 3.1 generates:
  - Summary
  - Category-specific insights
  - Strategic suggestions
- Visual Business Model Canvas in scrollable card format
- Spider web chart showing strategic profile dimensions (e.g., Risk, Scalability)
- User feedback system (thumbs up/down and comment)
- Saves session history in a SQLite database for review and download

## Tech Stack

- **Frontend**: Streamlit (with custom HTML/CSS for card layout)
- **AI Model**: LLaMA 3.1 via Hugging Face Inference API
- **Backend**: Python + SQLAlchemy ORM
- **Database**: SQLite
- **File Parsing**:
  - `PyPDF2` for PDFs
  - `python-docx` for Word documents
  - Built-in reader for text files

## Getting Started

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/bizformulate.git
   cd bizformulate

2. Set up virtual environment and install dependencies
   ```bash
   pip install -r requirements.txt

3. Add Hugging Face API token
   ```bash
   Create a token.txt file in the root directory and paste your Hugging Face API token into it.

4. Run the app
   ```bash
   streamlit run app.py

## Example Use Cases

- Analyze interview notes for startup idea validation
- Structure meeting discussions using Business Model Canvas
- Generate and share strategic summaries with stakeholders

## License

MIT License


