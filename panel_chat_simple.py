import json, re
from typing import Dict, List, Any
import panel as pn
import param

pn.extension()

# Simple form using native Panel widgets instead of ReactiveHTML
class SimpleForm(param.Parameterized):
    field_1_1 = param.String(default="", label="1.1 Project Title")
    field_1_2_1 = param.String(default="", label="1.2.1 Summary")
    field_1_2_2 = param.String(default="", label="1.2.2 Purpose")
    field_2_1 = param.String(default="", label="2.1 Data Types")
    field_2_2 = param.String(default="", label="2.2 Legal Basis")

# Create form instance
form_obj = SimpleForm()

# Create Panel widgets
form_widgets = pn.Param(
    form_obj,
    parameters=['field_1_1', 'field_1_2_1', 'field_1_2_2', 'field_2_1', 'field_2_2'],
    widgets={
        'field_1_1': pn.widgets.TextInput,
        'field_1_2_1': pn.widgets.TextAreaInput,
        'field_1_2_2': pn.widgets.TextAreaInput,
        'field_2_1': pn.widgets.TextAreaInput,
        'field_2_2': pn.widgets.TextInput,
    },
    sizing_mode='stretch_width'
)

# ID mapping for the chat interface
ID_MAP = {
    "1.1": "field_1_1",
    "1.2.1": "field_1_2_1", 
    "1.2.2": "field_1_2_2",
    "2.1": "field_2_1",
    "2.2": "field_2_2"
}

def read_form() -> Dict[str, str]:
    return {original_id: getattr(form_obj, param_name) for original_id, param_name in ID_MAP.items()}

def apply_edits(edits: List[Dict[str, str]]) -> None:
    for e in edits:
        fid, val = e.get("id"), e.get("value", "")
        if fid in ID_MAP:
            setattr(form_obj, ID_MAP[fid], val)

def parse_json(text: str) -> Dict[str, Any]:
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                return {}
    return {}

def handle_json_payload(payload: Dict[str, Any]) -> str:
    explanation = str(payload.get("explanation of edits", "")).strip()
    edits = payload.get("edits", [])
    follow_up = str(payload.get("follow-up question", "")).strip()
    if isinstance(edits, list):
        apply_edits(edits)
    reply = ""
    if explanation:
        reply += f"**Update:** {explanation}\n\n"
    if follow_up:
        reply += f"**Next:** {follow_up}"
    return reply or "Done."

def fake_llm(user_msg: str, current_form: Dict[str, str]) -> str:
    if user_msg.lower().startswith("title:"):
        val = user_msg.split(":", 1)[1].strip()
        return json.dumps({
            "explanation of edits": f"Set the project title to '{val}'.",
            "edits": [{"id": "1.1", "value": val}],
            "follow-up question": "Would you like to fill in 1.2.1 (Summary) next?"
        })
    if "autofill example" in user_msg.lower():
        return json.dumps({
            "explanation of edits": "Added example content to summary and purpose.",
            "edits": [
                {"id": "1.2.1", "value": "Example summary of the data processing activity."},
                {"id": "1.2.2", "value": "We process contact info to provide user support."}
            ],
            "follow-up question": "Do you want to describe the data types under 2.1?"
        })
    return json.dumps({
        "explanation of edits": "",
        "edits": [],
        "follow-up question": "Which field (by ID like 1.2.1) should we update next?"
    })

def on_message(contents, user, **kwargs):
    raw = fake_llm(str(contents), read_form())
    payload = parse_json(raw)
    if not payload:
        return "Could not parse valid JSON from model output."
    return handle_json_payload(payload)

# Create chat interface
chat = pn.chat.ChatInterface(
    callback=on_message,
    show_clear=False,
    placeholder_text="Ask the model... Try: 'title: DPIA Example' or 'autofill example'",
    sizing_mode="stretch_both",
)

# Add initial message
chat.send(
    "**Simple Form Test**\n\nTry:\n- 'title: My Project'\n- 'autofill example'",
    user="System"
)

# Create layout
layout = pn.Row(
    pn.Column("# 💬 Chat", chat, sizing_mode="stretch_both"),
    pn.Column("# 🧾 Simple Form", form_widgets, sizing_mode="stretch_both"),
    min_height=600,
    sizing_mode="stretch_both"
)

layout.servable()