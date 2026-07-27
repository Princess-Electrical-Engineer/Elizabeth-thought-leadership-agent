"""Generate concise article summaries and LinkedIn drafts in Elizabeth's voice."""
import json
import os
from pathlib import Path

import anthropic

ROOT = Path(__file__).parent.parent
VOICE_PROFILE_PATH = ROOT / "voice_profile.md"
SUMMARY_MODEL = os.getenv("ANTHROPIC_SUMMARY_MODEL", "claude-3-5-haiku-latest")
POST_MODEL = os.getenv("ANTHROPIC_POST_MODEL", "claude-sonnet-4-0")


def load_voice_profile() -> str:
    return VOICE_PROFILE_PATH.read_text(encoding="utf-8")


def _client() -> anthropic.Anthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured.")
    return anthropic.Anthropic(api_key=api_key)


def generate_summary(article: dict) -> str:
    message = _client().messages.create(
        model=SUMMARY_MODEL,
        max_tokens=250,
        messages=[{"role": "user", "content": f"""Summarize the article in 3 concise sentences for an experienced aerospace and systems engineer. State the development, its engineering or mission significance, and the main uncertainty or tradeoff. Do not add facts beyond the supplied content.\n\nTitle: {article.get('title', '')}\nSource: {article.get('source', '')}\nContent: {article.get('summary', '')}"""}],
    )
    return message.content[0].text.strip()


def generate_posts(article: dict, opinion: str) -> dict:
    system_prompt = f"""You are Elizabeth Besenyei's LinkedIn ghostwriter. Follow this profile exactly:\n\n{load_voice_profile()}\n\nRules:\n- Preserve Elizabeth's actual opinion and do not invent experience or facts.\n- Treat the article as context, not as the post's main content.\n- Make the draft professional, serious, technically credible, and readable.\n- Never imply classified, proprietary, export-controlled, or nonpublic knowledge.\n- Return only valid JSON with one key named linkedin."""
    user_prompt = f"""Article title: {article.get('title', '')}\nSource: {article.get('source', '')}\nURL: {article.get('url', '')}\nArticle summary: {article.get('summary', '')}\n\nElizabeth's notes or opinion:\n{opinion}\n\nReturn: {{\"linkedin\": \"full post text\"}}"""
    message = _client().messages.create(
        model=POST_MODEL,
        max_tokens=900,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1].removeprefix("json").strip()
    return json.loads(raw)
