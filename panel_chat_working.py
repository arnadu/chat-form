import json, re
from typing import Dict, List, Any, NamedTuple
import panel as pn

pn.extension()

class FormQuestion(NamedTuple):
    id: str
    question: str
    instructions: str
    widget_type: str
    options: List[str] = []

# Single source of truth for form questions
FORM_QUESTIONS = [
    FormQuestion(
        id="1.1",
        question="What is the name of your data processing activity?",
        instructions="Provide a clear, descriptive name for this specific data processing activity (e.g., 'Customer Support Ticket System', 'Employee Payroll Processing').",
        widget_type="text"
    ),
    FormQuestion(
        id="1.2.1", 
        question="Describe the purpose of the data processing",
        instructions="Explain why you are processing personal data. Be specific about the business purpose and what you aim to achieve.",
        widget_type="textarea"
    ),
    FormQuestion(
        id="1.2.2",
        question="What categories of personal data are processed?", 
        instructions="List the types of personal data involved (e.g., names, email addresses, phone numbers, IP addresses, cookies, etc.).",
        widget_type="textarea"
    ),
    FormQuestion(
        id="2.1",
        question="Who are the data subjects?",
        instructions="Identify whose personal data you are processing (e.g., customers, employees, website visitors, suppliers).", 
        widget_type="textarea"
    ),
    FormQuestion(
        id="2.2",
        question="What is your legal basis for processing?",
        instructions="Select the GDPR legal basis that applies to this processing activity. Choose the most appropriate one.",
        widget_type="select",
        options=["Consent", "Contract", "Legal Obligation", "Vital Interests", "Public Task", "Legitimate Interests"]
    ),
]

# Initialize form data store from questions
form_data = {q.id: {"question": q.question, "answer": "", "rationale": ""} for q in FORM_QUESTIONS}

# Track instruction visibility
instruction_states = {q.id: False for q in FORM_QUESTIONS}

def read_form() -> Dict[str, Dict[str, str]]:
    """Read current form data"""
    return form_data

def apply_edits(edits: List[Dict[str, Any]]) -> None:
    """Apply edits to form data and update HTML form"""
    updates_made = False
    
    for edit in edits:
        qid = edit.get("id")
        if qid in form_data:
            if "answer" in edit:
                form_data[qid]["answer"] = edit["answer"]
                updates_made = True
            if "rationale" in edit:
                form_data[qid]["rationale"] = edit["rationale"]
                updates_made = True
    
    # Update the HTML form by regenerating it
    if updates_made:
        update_form_display()

def generate_form_html_with_data() -> str:
    """Generate HTML form with current form_data values pre-filled"""
    
    # Generate table rows
    table_rows = ""
    for question in FORM_QUESTIONS:
        safe_id = question.id.replace('.', '_')
        
        # Get current values
        current_answer = form_data.get(question.id, {}).get("answer", "")
        current_rationale = form_data.get(question.id, {}).get("rationale", "")
        
        # Generate input field based on type with current value
        if question.widget_type == "textarea":
            input_html = f'''<textarea id="answer_{safe_id}" name="answer_{safe_id}" placeholder="Enter answer...">{current_answer}</textarea>'''
        elif question.widget_type == "select":
            options_html = '<option value="">Select...</option>'
            for opt in question.options:
                selected = 'selected' if opt == current_answer else ''
                options_html += f'<option value="{opt}" {selected}>{opt}</option>'
            input_html = f'''<select id="answer_{safe_id}" name="answer_{safe_id}">{options_html}</select>'''
        else:
            input_html = f'''<input type="text" id="answer_{safe_id}" name="answer_{safe_id}" placeholder="Enter answer..." value="{current_answer}">'''
        
        # Generate rationale textarea with current value
        rationale_html = f'''<textarea id="rationale_{safe_id}" name="rationale_{safe_id}" placeholder="Explain rationale...">{current_rationale}</textarea>'''
        
        # Instructions display (controlled by instruction_states)
        instructions_style = "display: block;" if instruction_states.get(question.id, False) else "display: none;"
        instructions_html = f'''<div id="instructions_{question.id}" style="{instructions_style} background: #e7f3ff; padding: 8px; margin-top: 4px; border-radius: 4px; border-left: 3px solid #007acc; font-size: 14px;">{question.instructions}</div>'''
        
        # Generate row
        table_rows += f'''
            <tr>
                <td style="width: 80px; text-align: center; padding: 12px; border: 1px solid #ddd; vertical-align: top;"><strong>{question.id}</strong></td>
                <td style="min-width: 200px; padding: 12px; border: 1px solid #ddd; vertical-align: top;">
                    <div>{question.question}</div>
                    {instructions_html}
                </td>
                <td style="padding: 12px; border: 1px solid #ddd; vertical-align: top;">{input_html}</td>
                <td style="padding: 12px; border: 1px solid #ddd; vertical-align: top;">{rationale_html}</td>
            </tr>
        '''
    
    # Complete HTML document with inline styles
    return f'''
    <div style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h1 style="color: #333; border-bottom: 2px solid #007acc; padding-bottom: 10px; margin-top: 0;">🛡️ GDPR Data Processing Assessment</h1>
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                <thead>
                    <tr>
                        <th style="padding: 12px; border: 1px solid #ddd; background-color: #007acc; color: white; font-weight: bold;">ID</th>
                        <th style="padding: 12px; border: 1px solid #ddd; background-color: #007acc; color: white; font-weight: bold;">Question</th>
                        <th style="padding: 12px; border: 1px solid #ddd; background-color: #007acc; color: white; font-weight: bold;">Answer</th>
                        <th style="padding: 12px; border: 1px solid #ddd; background-color: #007acc; color: white; font-weight: bold;">Rationale</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
    </div>
    <style>
        input, textarea, select {{
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }}
        textarea {{
            resize: vertical;
            min-height: 60px;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
    </style>
    '''

# Create HTML pane
html_pane = pn.pane.HTML("", sizing_mode="stretch_both", min_height=600)

def update_form_display():
    """Update the HTML form display with current form_data"""
    html_content = generate_form_html_with_data()
    html_pane.object = html_content

def toggle_instructions(question_id):
    """Toggle instruction visibility for a question"""
    instruction_states[question_id] = not instruction_states[question_id]
    update_form_display()

# Create help buttons for each question
help_buttons = {}
for q in FORM_QUESTIONS:
    btn = pn.widgets.Button(
        name=f"? {q.id}", 
        button_type="primary", 
        width=60, 
        height=30,
        margin=(5, 5)
    )
    btn.on_click(lambda event, qid=q.id: toggle_instructions(qid))
    help_buttons[q.id] = btn

# Initialize the form display
update_form_display()

def parse_json(text: str) -> Dict[str, Any]:
    """Parse JSON from text, handling common formatting issues"""
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
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
    """Simulate LLM responses with JSON format"""
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

chat.send("**Working Form with Help Buttons**\n\n✅ Panel widgets for ? buttons\n⚡ Reliable instruction toggling\n🚀 LLM integration works", user="System")

# Create help button panel
help_panel = pn.Column(
    "**Help Buttons:**",
    "Click to show/hide instructions for each question:",
    pn.FlexBox(*help_buttons.values(), flex_direction="row", flex_wrap="wrap"),
    width=300,
    margin=(10, 10)
)

# Create layout
layout = pn.Row(
    pn.Column("# 💬 Chat", chat, sizing_mode="stretch_both"),
    pn.Column(help_panel, "# 📋 Form", html_pane, sizing_mode="stretch_both"),
    min_height=600,
    sizing_mode="stretch_both"
)

layout.servable()