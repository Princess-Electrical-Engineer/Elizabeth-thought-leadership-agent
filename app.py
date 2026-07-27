"""Elizabeth Besenyei LinkedIn Thought Leadership Agent."""
import html
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "agent"))
from fetch_articles import MIN_QUEUE_SIZE, load_state, prune_stale, save_state, topup_queue
from generate_post import generate_posts, generate_summary

st.set_page_config(page_title="Elizabeth's LinkedIn Agent", page_icon="🛰️", layout="centered")


def check_password() -> None:
    expected = os.getenv("APP_PASSWORD") or st.secrets.get("APP_PASSWORD", "")
    if not expected:
        return
    if st.session_state.get("authenticated"):
        return
    entered = st.text_input("Password", type="password")
    if entered == expected:
        st.session_state.authenticated = True
        st.rerun()
    if entered:
        st.error("Incorrect password")
    st.stop()


check_password()


def refresh_state(force=False):
    state = load_state()
    state["queue"] = prune_stale(state.get("queue", []))
    if force or len(state["queue"]) < MIN_QUEUE_SIZE:
        state["queue"], state["history"] = topup_queue(
            state["queue"], state.get("history", [])
        )
        state["generated_at"] = datetime.now(timezone.utc).isoformat()
        save_state(state)
    st.session_state.state = state


def reset_draft():
    for key, value in {
        "summary": "", "summary_ready": False, "draft": "", "draft_ready": False,
        "opinion": ""
    }.items():
        st.session_state[key] = value


def remove_current():
    state = st.session_state.state
    if state.get("queue"):
        state["queue"] = state["queue"][1:]
    state["queue"], state["history"] = topup_queue(
        state.get("queue", []), state.get("history", [])
    )
    state["generated_at"] = datetime.now(timezone.utc).isoformat()
    save_state(state)
    st.session_state.state = state
    reset_draft()


for key, value in {
    "state": None, "summary": "", "summary_ready": False,
    "draft": "", "draft_ready": False, "opinion": ""
}.items():
    st.session_state.setdefault(key, value)

st.title("Elizabeth's LinkedIn Thought Leadership Agent")
st.caption("A focused review-and-draft workflow for aerospace, systems engineering, technology, and technical leadership.")

with st.sidebar:
    st.subheader("Content focus")
    st.write("Systems engineering · aerospace and defense · space systems · integration and test · communications · innovation · engineering leadership")
    st.caption("All posts require Elizabeth's review. The app does not publish automatically.")

if st.session_state.state is None:
    with st.spinner("Finding recent articles..."):
        refresh_state()

queue = st.session_state.state.get("queue", [])
if not queue:
    st.info("No qualifying recent articles were found. Refresh the feeds or adjust the source configuration.")
    if st.button("Refresh article feeds", type="primary"):
        with st.spinner("Checking sources..."):
            refresh_state(force=True)
        st.rerun()
    st.stop()

article = queue[0]
st.caption(f"{len(queue)} article(s) available")
st.markdown(
    f"""<div style='padding:1rem;border-left:4px solid #0a66c2;background:#f6f8fa;border-radius:4px'>
    <small>{html.escape(article.get('source', 'Unknown source'))}</small><br>
    <strong>{html.escape(article.get('title', ''))}</strong>
    </div>""",
    unsafe_allow_html=True,
)

left, right = st.columns(2)
with left:
    st.link_button("Read full article", article.get("url", "#"), use_container_width=True)
with right:
    if st.button("Skip article", use_container_width=True):
        remove_current()
        st.rerun()

st.subheader("1. Understand the article")
if not st.session_state.summary_ready:
    try:
        with st.spinner("Preparing an engineering-focused summary..."):
            st.session_state.summary = generate_summary(article)
    except Exception as exc:
        st.session_state.summary = article.get("summary", "")[:700]
        st.warning(f"AI summary unavailable: {exc}")
    st.session_state.summary_ready = True
st.info(st.session_state.summary or "No summary was provided by the feed.")

st.subheader("2. Add Elizabeth's perspective")
st.caption("Use bullet points. Include what matters, the engineering tradeoff, and what professionals should consider.")
st.session_state.opinion = st.text_area(
    "Your notes",
    value=st.session_state.opinion,
    placeholder="- The technical development that matters most is...\n- The systems-level risk or tradeoff is...\n- From an integration and test perspective...",
    height=150,
)

if st.button("Generate LinkedIn draft", type="primary", disabled=not st.session_state.opinion.strip()):
    try:
        with st.spinner("Writing in Elizabeth's professional voice..."):
            st.session_state.draft = generate_posts(article, st.session_state.opinion)["linkedin"]
            st.session_state.draft_ready = True
    except Exception as exc:
        st.error(f"Draft generation failed: {exc}")

if st.session_state.draft_ready:
    st.subheader("3. Review and post")
    st.session_state.draft = st.text_area("LinkedIn draft", value=st.session_state.draft, height=360)
    st.caption(f"{len(st.session_state.draft.split())} words · Review every factual claim before publishing.")
    col1, col2 = st.columns(2)
    with col1:
        st.link_button("Open LinkedIn", "https://www.linkedin.com/feed/", use_container_width=True)
    with col2:
        if st.button("Mark done and show next", type="primary", use_container_width=True):
            remove_current()
            st.rerun()
