# Panel chat + Markdown document demo
# Requirements: pip install "panel>=1.4"
# In Jupyter, just run this cell. If the UI doesn't render, run pn.extension() once and re-run.

import re
from typing import Tuple
import panel as pn

pn.extension()   # loads the Panel assets

# -------------------------------
# Shared state: the editable doc
# -------------------------------
DOCUMENT = {
    "content": "# Project Notes\n\nWelcome! This document will update as we chat.\n"
}

doc_pane = pn.pane.Markdown(
    DOCUMENT["content"],
    sizing_mode="stretch_both",
    styles={"padding": "1rem", "background": "#fafafa", "border": "1px solid #eee", "borderRadius": "12px"}
)

# ----------------------------------------------------------
# Edit protocol (LLM-friendly) supported in assistant reply:
#   [DOC:APPEND]
#   ...markdown to append...
#   [/DOC]
#
#   [DOC:REPLACE]
#   pattern: <<<old text>>>
#   with:    <<<new text>>>
#   [/DOC]
#
# The tags are stripped from what the user sees, but applied to the doc.
# ----------------------------------------------------------

APPEND_TAG_RE = re.compile(r"\[DOC:APPEND\](.*?)\[/DOC\]", re.DOTALL | re.IGNORECASE)
REPLACE_TAG_RE = re.compile(r"\[DOC:REPLACE\](.*?)\[/DOC\]", re.DOTALL | re.IGNORECASE)

def apply_doc_edits(assistant_reply: str, current_doc: str) -> Tuple[str, str]:
    """
    Applies [DOC:APPEND] and [DOC:REPLACE] blocks to the doc.
    Returns (clean_reply_without_tags, new_doc_content).
    """
    new_doc = current_doc
    clean_reply = assistant_reply

    # APPEND
    for block in APPEND_TAG_RE.findall(assistant_reply):
        addition = block.strip()
        if addition:
            if not new_doc.endswith("\n"):
                new_doc += "\n"
            new_doc += f"\n{addition}\n"
        clean_reply = clean_reply.replace(f"[DOC:APPEND]{block}[/DOC]", "").strip()

    # REPLACE (first occurrence)
    for block in REPLACE_TAG_RE.findall(assistant_reply):
        pat_match = re.search(r"pattern:\s*<<<(.*?)>>>", block, re.DOTALL | re.IGNORECASE)
        with_match = re.search(r"with:\s*<<<(.*?)>>>", block, re.DOTALL | re.IGNORECASE)
        if pat_match and with_match:
            old = pat_match.group(1)
            new = with_match.group(1)
            new_doc = new_doc.replace(old, new, 1)
        clean_reply = clean_reply.replace(f"[DOC:REPLACE]{block}[/DOC]", "").strip()

    return clean_reply.strip(), new_doc

# ----------------------------------------------------------
# Drop-in LLM function
# Replace `fake_llm` with your real LLM call.
# ----------------------------------------------------------
def fake_llm(user_message: str, current_doc: str) -> str:
    """
    Demo LLM:
    - If user includes edit tags, we acknowledge (edits applied by the parser).
    - If user writes 'title: ...', we replace the H1.
    - Otherwise, we append a small Note section.
    """
    if "[DOC:" in user_message:
        return "Applied your document changes. ✅"

    m = re.search(r"title\s*:\s*(.+)", user_message, re.IGNORECASE)
    if m:
        new_title = m.group(1).strip()
        return f"""Updating the document title.
[DOC:REPLACE]
pattern: <<<# Project Notes>>>
with:    <<<# {new_title}>>>
[/DOC]"""

    # Default: append the user's text under Notes
    return f"""Noted. I suggest adding a quick note.
[DOC:APPEND]
### Notes
- {user_message.strip()}
[/DOC]"""

# --- Example (commented) wiring with a real model ---
# from openai import OpenAI
# client = OpenAI()
# def real_llm(user_message: str, current_doc: str) -> str:
#     # Return a *string* that may include [DOC:APPEND] / [DOC:REPLACE] blocks.
#     completion = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role":"system","content":"You can update a markdown doc by emitting [DOC:APPEND]...[/DOC] or [DOC:REPLACE]...[/DOC] blocks. Otherwise, reply normally."},
#             {"role":"user","content": user_message},
#             {"role":"system","content": f"Current document:\n{current_doc}"}
#         ],
#         temperature=0.2,
#     )
#     return completion.choices[0].message.content

# ----------------------------------------------------------
# Chat callback: runs each turn and updates the Markdown pane
# ----------------------------------------------------------
def on_message(contents, user, **kwargs):
    # 1) Get a reply from the model (swap to real_llm if desired)
    assistant_reply = fake_llm(str(contents), DOCUMENT["content"])

    # 2) Apply any document edits found in the reply
    clean_reply, new_doc = apply_doc_edits(assistant_reply, DOCUMENT["content"])

    # 3) Persist & refresh the live Markdown
    DOCUMENT["content"] = new_doc
    doc_pane.object = DOCUMENT["content"]

    # 4) Return the visible assistant message for the chat UI
    return clean_reply or "(No visible text; edits applied.)"

# ----------------------------------------------------------
# Build the UI
# ----------------------------------------------------------
chat = pn.chat.ChatInterface(
    callback=on_message,
    show_clear=False,
    message_params={"show_avatar": False},
    placeholder_text="Ask the model… or include [DOC:APPEND]/[DOC:REPLACE] blocks to edit the document.",
    sizing_mode="stretch_both",
)

# Seed a brief usage tip
chat.send(
    "Hi! Send normal questions, or include edit tags to change the document.\n"
    "Example append:\n"
    "[DOC:APPEND]\n## To-Dos\n- Ship v1\n- Write docs\n[/DOC]\n\n"
    "Example replace:\n"
    "[DOC:REPLACE]\npattern: <<<# Project Notes>>>\nwith:    <<<# Sprint Plan>>>\n[/DOC]",
    user="System",
)

layout = pn.Row(
    pn.Column("# 🔎 Chat", chat, sizing_mode="stretch_both"),
    pn.Column("# 📝 Markdown Document", doc_pane, sizing_mode="stretch_both"),
    sizing_mode="stretch_both",
    height=650
)

# Make the layout servable for Panel server
layout.servable()
