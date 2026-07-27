# Elizabeth's LinkedIn Thought Leadership Agent

A focused Streamlit app that finds recent articles relevant to aerospace, systems engineering, space, integration and test, communications, innovation, and engineering leadership. Elizabeth adds her own perspective, and Claude converts it into a serious, professional LinkedIn draft for manual review and posting.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key"
streamlit run app.py
```

The page opens at `http://localhost:8501`.

## Configuration

- `voice_profile.md`: Elizabeth's voice, topics, and safety boundaries
- `config/sources.json`: article feeds, keywords, weights, queue size, and freshness
- `state.json`: local article queue and URL history
- `.env.example`: environment-variable template
- `.streamlit/secrets.toml.example`: optional password template

## Current sources

SpaceNews, Breaking Defense, Defense News, Air & Space Forces Magazine, IEEE Spectrum, MIT Engineering, MIT Technology Review, and NASA.

## Workflow

1. The app fetches and ranks recent articles.
2. Elizabeth reads the article and reviews a short summary.
3. Elizabeth enters her own notes or opinion.
4. The app drafts a LinkedIn post in her professional voice.
5. Elizabeth reviews the post and manually publishes it.

The app intentionally does not auto-publish.
