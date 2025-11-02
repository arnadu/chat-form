import json, re
from typing import Dict, List, Any, NamedTuple
import panel as pn
import param

pn.extension()

class FormQuestion(NamedTuple):
    id: str
    question: str
    instructions: str  # Tooltip for user, formatted for LLM
    widget_type: str = "text"  # "text", "textarea", "select"
    options: List[str] = None  # For select widgets

# Define the form structure - much cleaner!
FORM_QUESTIONS = [
    FormQuestion(
        id="1.1",
        question="Project Title",
        instructions="Provide a concise, descriptive title for this data processing project. This should clearly identify the main purpose or activity.",
        widget_type="text"
    ),
    FormQuestion(
        id="1.2.1", 
        question="Project Summary",
        instructions="Describe the overall scope and nature of data processing activities. Include key objectives, stakeholders, and expected outcomes.",
        widget_type="textarea"
    ),
    FormQuestion(
        id="1.2.2",
        question="Purpose of Processing", 
        instructions="Explain why this data processing is necessary. What business need does it fulfill? How does it benefit the organization and data subjects?",
        widget_type="textarea"
    ),
    FormQuestion(
        id="2.1",
        question="Data Types",
        instructions="List all categories of personal data that will be processed. Include special categories (sensitive data) if applicable. Be specific about data fields and sources.",
        widget_type="textarea"
    ),
    FormQuestion(
        id="2.2",
        question="Legal Basis",
        instructions="Identify the lawful basis for processing under GDPR Article 6. If processing special categories, also specify Article 9 basis. Explain why this basis applies.",
        widget_type="select",
        options=["Consent", "Contract", "Legal Obligation", "Vital Interests", "Public Task", "Legitimate Interests"]
    ),
]

# Dynamically create the form class
def create_form_class():
    class_dict = {"__doc__": "Dynamic form based on FORM_QUESTIONS"}
    
    for q in FORM_QUESTIONS:
        # Create safe parameter name
        param_name = f"field_{q.id.replace('.', '_')}"
        
        # Add answer field
        class_dict[f"{param_name}_answer"] = param.String(
            default="", 
            label=f"{q.id} {q.question}"
        )
        
        # Add rationale field
        class_dict[f"{param_name}_rationale"] = param.String(
            default="", 
            label=f"{q.id} Rationale"
        )
    
    return type("DynamicForm", (param.Parameterized,), class_dict)

# Create form instance
FormClass = create_form_class()
form_obj = FormClass()

# Create table-based form
def create_form_widgets():
    # Create table header
    header = pn.Row(
        pn.pane.HTML("<strong>ID</strong>", width=80, height=40, sizing_mode='fixed'),
        pn.pane.HTML("<strong>Question</strong>", sizing_mode='stretch_width'),
        pn.pane.HTML("<strong>Answer</strong>", sizing_mode='stretch_width'), 
        pn.pane.HTML("<strong>Rationale</strong>", sizing_mode='stretch_width'),
        pn.pane.HTML("<strong>?</strong>", width=40, height=40, sizing_mode='fixed'),
        styles={'background': '#f5f5f5', 'padding': '10px', 'border-bottom': '2px solid #ddd'}
    )
    
    form_rows = [header]
    
    for q in FORM_QUESTIONS:
        param_name = f"field_{q.id.replace('.', '_')}"
        answer_param = f"{param_name}_answer"
        rationale_param = f"{param_name}_rationale"
        
        # Create widgets based on type (no labels)
        if q.widget_type == "textarea":
            answer_widget = pn.widgets.TextAreaInput.from_param(
                getattr(form_obj.param, answer_param),
                placeholder="Enter answer...", height=60, name=""
            )
        elif q.widget_type == "select" and q.options:
            answer_widget = pn.widgets.Select.from_param(
                getattr(form_obj.param, answer_param),
                options=[""] + q.options, height=60, name=""
            )
        else:
            answer_widget = pn.widgets.TextInput.from_param(
                getattr(form_obj.param, answer_param),
                placeholder="Enter answer...", height=60, name=""
            )
        
        rationale_widget = pn.widgets.TextAreaInput.from_param(
            getattr(form_obj.param, rationale_param),
            placeholder="Explain reasoning...", height=60, name=""
        )
        
        # Create help button
        help_button = pn.widgets.Button(name="?", width=40, height=40, button_type="primary")
        
        # Create instruction panel (initially hidden)
        instruction_panel = pn.pane.Markdown(
            f"**Instructions:** {q.instructions}",
            visible=False,
            sizing_mode='stretch_width',
            styles={
                'background': '#f0f8ff', 
                'padding': '10px', 
                'border': '1px solid #007acc',
                'margin': '5px 0',
                'font-size': '0.9em'
            }
        )
        
        # Toggle function for instructions
        def toggle_instructions(event, panel=instruction_panel):
            panel.visible = not panel.visible
            
        help_button.on_click(toggle_instructions)
        
        # Create table row
        table_row = pn.Row(
            pn.pane.HTML(f"<strong>{q.id}</strong>", width=80, height=60, sizing_mode='fixed'),
            pn.pane.HTML(q.question, sizing_mode='stretch_width'),
            answer_widget,
            rationale_widget, 
            help_button,
            styles={'padding': '5px', 'border-bottom': '1px solid #eee'}
        )
        
        # Create row container with instructions
        row_container = pn.Column(
            table_row,
            instruction_panel,
            sizing_mode='stretch_width'
        )
        
        form_rows.append(row_container)
    
    return pn.Column(*form_rows, sizing_mode='stretch_width')

form_widgets = create_form_widgets()

# Create mapping for chat interface
ID_MAP = {}
for q in FORM_QUESTIONS:
    param_name = f"field_{q.id.replace('.', '_')}"
    ID_MAP[q.id] = {
        "answer": f"{param_name}_answer",
        "rationale": f"{param_name}_rationale",
        "question": q.question,
        "instructions": q.instructions
    }

def read_form() -> Dict[str, Dict[str, str]]:
    """Read form data including answers and rationales"""
    result = {}
    for qid, mapping in ID_MAP.items():
        result[qid] = {
            "answer": getattr(form_obj, mapping["answer"]),
            "rationale": getattr(form_obj, mapping["rationale"]),
            "question": mapping["question"],
            "instructions": mapping["instructions"]
        }
    return result

def apply_edits(edits: List[Dict[str, Any]]) -> None:
    """Apply edits to form fields"""
    for edit in edits:
        qid = edit.get("id")
        if qid in ID_MAP:
            mapping = ID_MAP[qid]
            
            # Update answer if provided
            if "answer" in edit:
                setattr(form_obj, mapping["answer"], edit["answer"])
            
            # Update rationale if provided  
            if "rationale" in edit:
                setattr(form_obj, mapping["rationale"], edit["rationale"])

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

def fake_llm(user_msg: str, current_form: Dict[str, Dict[str, str]]) -> str:
    """Enhanced LLM that understands the new form structure"""
    
    if user_msg.lower().startswith("title:"):
        val = user_msg.split(":", 1)[1].strip()
        return json.dumps({
            "explanation of edits": f"Set the project title to '{val}'.",
            "edits": [{"id": "1.1", "answer": val}],
            "follow-up question": "Would you like me to help with the project summary (1.2.1)?"
        })
    
    if "help" in user_msg.lower() and any(qid in user_msg for qid in ID_MAP.keys()):
        # Extract question ID from message
        for qid in ID_MAP.keys():
            if qid in user_msg:
                q_info = ID_MAP[qid]
                return f"**Question {qid}: {q_info['question']}**\n\n{q_info['instructions']}\n\nPlease provide your answer and explain your rationale."
    
    if "autofill example" in user_msg.lower():
        return json.dumps({
            "explanation of edits": "Added example GDPR assessment data with rationales.",
            "edits": [
                {
                    "id": "1.1", 
                    "answer": "Customer Support Data Processing",
                    "rationale": "Clear, descriptive title that indicates the main business function"
                },
                {
                    "id": "1.2.1", 
                    "answer": "Processing customer contact information and support tickets to provide technical assistance and resolve issues.",
                    "rationale": "Comprehensive summary covering scope, purpose, and key activities"
                },
                {
                    "id": "2.2", 
                    "answer": "Legitimate Interests",
                    "rationale": "Customer support is a legitimate business need that benefits both the company and customers"
                }
            ],
            "follow-up question": "Should I help you complete the data types section (2.1)?"
        })
    
    if "show form" in user_msg.lower():
        form_summary = []
        for qid, data in current_form.items():
            status = "✅" if data["answer"] else "❌"
            form_summary.append(f"{status} **{qid}**: {data['question']}")
        
        return "**Current Form Status:**\n\n" + "\n".join(form_summary) + "\n\nWhich question would you like to work on?"
    
    return json.dumps({
        "explanation of edits": "",
        "edits": [],
        "follow-up question": "I can help you fill out the form. Try 'show form' to see current status, 'help 1.1' for guidance, or 'autofill example' to see sample data."
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
    "**Enhanced GDPR Form Assistant**\n\n" +
    "I can help you complete this data processing assessment. Try:\n\n" +
    "• `show form` - See current completion status\n" +
    "• `help 1.1` - Get detailed guidance for any question\n" +
    "• `title: My Project` - Set a project title\n" +
    "• `autofill example` - Load sample GDPR assessment\n\n" +
    "Each question includes both an **answer** and **rationale** field to document your reasoning.",
    user="System"
)

# Create layout
layout = pn.Row(
    pn.Column("# 💬 Chat", chat, sizing_mode="stretch_both"),
    pn.Column("# 📋 Form", form_widgets, sizing_mode="stretch_both"),
    min_height=600,
    sizing_mode="stretch_both"
)

layout.servable()