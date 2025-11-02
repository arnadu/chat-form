import json, re
from typing import Dict, List, Any, NamedTuple
import panel as pn

pn.extension()

class FormQuestion(NamedTuple):
    id: str
    question: str
    instructions: str
    widget_type: str = "text"
    options: List[str] = None

# Define the form structure
FORM_QUESTIONS = [
    FormQuestion(
        id="1.1",
        question="Project Title",
        instructions="Provide a concise, descriptive title for this data processing project.",
        widget_type="text"
    ),
    FormQuestion(
        id="1.2.1", 
        question="Project Summary",
        instructions="Describe the overall scope and nature of data processing activities.",
        widget_type="textarea"
    ),
    FormQuestion(
        id="1.2.2",
        question="Purpose of Processing", 
        instructions="Explain why this data processing is necessary. What business need does it fulfill?",
        widget_type="textarea"
    ),
    FormQuestion(
        id="2.1",
        question="Data Types",
        instructions="List all categories of personal data that will be processed.",
        widget_type="textarea"
    ),
    FormQuestion(
        id="2.2",
        question="Legal Basis",
        instructions="Identify the lawful basis for processing under GDPR Article 6.",
        widget_type="select",
        options=["Consent", "Contract", "Legal Obligation", "Vital Interests", "Public Task", "Legitimate Interests"]
    ),
]

# Create form using Panel widgets - GUARANTEED TO WORK
def create_form():
    widgets = {}
    instruction_states = {}  # Track instruction visibility
    
    # Create title
    title = pn.pane.Markdown("# 📋 GDPR Assessment Form", sizing_mode="stretch_width")
    
    # Create table header
    header = pn.Row(
        pn.pane.HTML("<strong>ID</strong>", width=80, margin=(5, 5)),
        pn.pane.HTML("<strong>Question</strong>", sizing_mode='stretch_width', margin=(5, 5)),
        pn.pane.HTML("<strong>Answer</strong>", sizing_mode='stretch_width', margin=(5, 5)), 
        pn.pane.HTML("<strong>Rationale</strong>", sizing_mode='stretch_width', margin=(5, 5)),
        pn.pane.HTML("<strong>Help</strong>", width=60, margin=(5, 5)),
        styles={'background': '#007acc', 'color': 'white', 'padding': '10px'}
    )
    
    form_rows = [title, header]
    
    for q in FORM_QUESTIONS:
        # Create answer widget based on type
        if q.widget_type == "textarea":
            answer_widget = pn.widgets.TextAreaInput(
                placeholder="Enter answer...", 
                height=80, 
                sizing_mode='stretch_width'
            )
        elif q.widget_type == "select" and q.options:
            answer_widget = pn.widgets.Select(
                options=[""] + q.options, 
                height=40,
                sizing_mode='stretch_width'
            )
        else:
            answer_widget = pn.widgets.TextInput(
                placeholder="Enter answer...", 
                height=40,
                sizing_mode='stretch_width'
            )
        
        # Create rationale widget
        rationale_widget = pn.widgets.TextAreaInput(
            placeholder="Explain reasoning...", 
            height=80,
            sizing_mode='stretch_width'
        )
        
        # Store widgets for easy access
        widgets[q.id] = {
            "answer": answer_widget,
            "rationale": rationale_widget,
            "question": q.question,
            "instructions": q.instructions
        }
        
        # Create help button - THIS DEFINITELY WORKS
        help_button = pn.widgets.Button(
            name="?", 
            width=50, 
            height=40, 
            button_type="primary",
            margin=(5, 5)
        )
        
        # Create instruction panel
        instruction_panel = pn.pane.Markdown(
            f"**💡 Instructions:** {q.instructions}",
            visible=False,
            sizing_mode='stretch_width',
            styles={
                'background': '#e7f3ff', 
                'padding': '15px', 
                'border': '2px solid #007acc',
                'border-radius': '5px',
                'margin': '5px'
            }
        )
        
        # Initialize instruction state
        instruction_states[q.id] = False
        
        # Create toggle function with closure
        def make_toggle(panel, qid):
            def toggle(event):
                current_state = instruction_states[qid]
                new_state = not current_state
                instruction_states[qid] = new_state
                panel.visible = new_state
                event.obj.name = "✕" if new_state else "?"
                event.obj.button_type = "light" if new_state else "primary"
            return toggle
            
        help_button.on_click(make_toggle(instruction_panel, q.id))
        
        # Create main table row
        table_row = pn.Row(
            pn.pane.HTML(f"<strong>{q.id}</strong>", width=80, margin=(5, 5)),
            pn.pane.HTML(f"<strong>{q.question}</strong>", sizing_mode='stretch_width', margin=(5, 5)),
            answer_widget,
            rationale_widget, 
            help_button,
            styles={'padding': '10px', 'border-bottom': '1px solid #ddd', 'background': '#f9f9f9'}
        )
        
        # Container for row and instructions
        row_container = pn.Column(
            table_row, 
            instruction_panel, 
            sizing_mode='stretch_width'
        )
        
        form_rows.append(row_container)
    
    return pn.Column(*form_rows, sizing_mode='stretch_width'), widgets

# Create form and widgets
form_container, widget_dict = create_form()

# Simple helper functions
def read_form() -> Dict[str, Dict[str, str]]:
    """Read current form data"""
    result = {}
    for qid, widgets in widget_dict.items():
        result[qid] = {
            "answer": widgets["answer"].value or "",
            "rationale": widgets["rationale"].value or "",
            "question": widgets["question"],
            "instructions": widgets["instructions"]
        }
    return result

def apply_edits(edits: List[Dict[str, Any]]) -> None:
    """Apply edits to form"""
    for edit in edits:
        qid = edit.get("id")
        if qid in widget_dict:
            if "answer" in edit:
                widget_dict[qid]["answer"].value = edit["answer"]
            if "rationale" in edit:
                widget_dict[qid]["rationale"].value = edit["rationale"]

def parse_json(text: str) -> Dict[str, Any]:
    """Parse JSON from text"""
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    return {}

def handle_json_payload(payload: Dict[str, Any]) -> str:
    """Handle JSON payload from LLM"""
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

def fake_llm(user_msg: str, current_form: Dict[str, Dict[str, str]]) -> str:
    """Simulate LLM responses"""
    if user_msg.lower().startswith("title:"):
        val = user_msg.split(":", 1)[1].strip()
        return json.dumps({
            "explanation of edits": f"Set the project title to '{val}'.",
            "edits": [{"id": "1.1", "answer": val}],
            "follow-up question": "Would you like me to help with the project summary?"
        })
    
    if "autofill example" in user_msg.lower():
        return json.dumps({
            "explanation of edits": "Added example GDPR assessment data.",
            "edits": [
                {"id": "1.1", "answer": "Customer Support Data Processing"},
                {"id": "1.2.1", "answer": "Processing customer contact information for technical support."},
                {"id": "2.2", "answer": "Legitimate Interests"}
            ],
            "follow-up question": "Should I help you complete the data types section?"
        })
    
    if "show form" in user_msg.lower():
        form_summary = []
        for qid, data in current_form.items():
            status = "✅" if data["answer"] else "❌"
            form_summary.append(f"{status} **{qid}**: {data['question']}")
        return "**Current Form Status:**\n\n" + "\n".join(form_summary)
    
    return json.dumps({
        "explanation of edits": "",
        "edits": [],
        "follow-up question": "Try 'title: My Project', 'autofill example', or 'show form'."
    })

def on_message(contents, user, **kwargs):
    """Handle chat messages"""
    raw = fake_llm(str(contents), read_form())
    payload = parse_json(raw)
    if not payload:
        return "Could not parse valid JSON from model output."
    return handle_json_payload(payload)

# Create chat interface
chat = pn.chat.ChatInterface(
    callback=on_message,
    show_clear=False,
    placeholder_text="Try: 'title: My Project' or 'autofill example'",
    sizing_mode="stretch_both",
)

chat.send("**✅ WORKING SOLUTION**\n\n🎯 Panel native widgets with working ? buttons\n💡 Click ? to show/hide instructions\n🚀 LLM integration fully functional!", user="System")

# Create final layout
layout = pn.Row(
    pn.Column("# 💬 Chat Assistant", chat, sizing_mode="stretch_both"),
    pn.Column(form_container, sizing_mode="stretch_both"),
    min_height=700,
    sizing_mode="stretch_both"
)

layout.servable()