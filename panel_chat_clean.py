import json
import re
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

# Form data storage
form_data = {q.id: {"question": q.question, "answer": "", "rationale": ""} for q in FORM_QUESTIONS}

# Panel widgets storage
form_widgets = {}
instruction_widgets = {}
instruction_buttons = {}

def create_form_widgets():
    """Create Panel widgets for the entire form in table layout"""
    global form_widgets, instruction_widgets, instruction_buttons
    
    # Create table header
    header_row = pn.Row(
        pn.pane.HTML("<strong>ID</strong>", width=80, margin=(5, 10)),
        pn.pane.HTML("<strong>Question</strong>", width=250, margin=(5, 10)),  
        pn.pane.HTML("<strong>Answer</strong>", margin=(5, 10), sizing_mode="stretch_width"),
        pn.pane.HTML("<strong>Rationale</strong>", margin=(5, 10), sizing_mode="stretch_width"),
        sizing_mode="stretch_width",
        styles={"background": "#007acc", "color": "white", "padding": "10px", "border-radius": "4px 4px 0 0"}
    )
    
    table_rows = [header_row]
    
    for i, question in enumerate(FORM_QUESTIONS):
        # Create instruction pane (initially hidden)
        instruction_pane = pn.pane.Markdown(
            f"💡 **Instructions:** {question.instructions}",
            visible=False,
            margin=(5, 10),
            styles={"background": "#e7f3ff", "border-left": "3px solid #007acc", "padding": "10px", "border-radius": "4px"}
        )
        instruction_widgets[question.id] = instruction_pane
        
        # Create help button
        help_btn = pn.widgets.Button(
            name="?", 
            width=25, 
            height=25,
            button_type="light",
            margin=(0, 5),
            styles={"border-radius": "50%", "font-size": "12px"}
        )
        
        def make_toggle_callback(qid):
            def toggle_instructions(event):
                instruction_pane = instruction_widgets[qid]
                btn = instruction_buttons[qid]
                if instruction_pane.visible:
                    instruction_pane.visible = False
                    btn.name = "?"
                    btn.button_type = "light"
                else:
                    instruction_pane.visible = True
                    btn.name = "✕"
                    btn.button_type = "primary"
            return toggle_instructions
        
        help_btn.on_click(make_toggle_callback(question.id))
        instruction_buttons[question.id] = help_btn
        
        # Create answer widget based on type
        current_answer = form_data[question.id]["answer"]
        
        if question.widget_type == "textarea":
            answer_widget = pn.widgets.TextAreaInput(
                value=current_answer,
                placeholder="Enter answer...",
                height=80,
                sizing_mode="stretch_width"
            )
        elif question.widget_type == "select" and question.options:
            answer_widget = pn.widgets.Select(
                value=current_answer if current_answer in (question.options or []) else None,
                options=question.options,
                sizing_mode="stretch_width"
            )
        else:
            answer_widget = pn.widgets.TextInput(
                value=current_answer,
                placeholder="Enter answer...",
                sizing_mode="stretch_width"
            )
        
        # Create rationale widget
        current_rationale = form_data[question.id]["rationale"]
        rationale_widget = pn.widgets.TextAreaInput(
            value=current_rationale,
            placeholder="Explain rationale...",
            height=80,
            sizing_mode="stretch_width"
        )
        
        # Store widgets for later access
        form_widgets[question.id] = {
            "answer": answer_widget,
            "rationale": rationale_widget
        }
        
        # Add change callbacks to sync with form_data
        def make_sync_callback(qid, field_type):
            def sync_to_form_data(event):
                if field_type == "answer":
                    form_data[qid]["answer"] = str(event.new) if event.new is not None else ""
                elif field_type == "rationale":
                    form_data[qid]["rationale"] = str(event.new) if event.new is not None else ""
                print(f"✅ Synced {qid}.{field_type}: {event.new}")
            return sync_to_form_data
        
        answer_widget.param.watch(make_sync_callback(question.id, "answer"), "value")
        rationale_widget.param.watch(make_sync_callback(question.id, "rationale"), "value")
        
        # Create question column with help button
        question_column = pn.Column(
            pn.Row(
                pn.pane.Markdown(f"**{question.question}**", sizing_mode="stretch_width"),
                help_btn,
                sizing_mode="stretch_width"
            ),
            instruction_pane,
            sizing_mode="stretch_width"
        )
        
        # Create table row (alternating background colors)
        row_bg = "#f9f9f9" if i % 2 == 0 else "white"
        
        table_row = pn.Row(
            pn.pane.HTML(f"<strong>{question.id}</strong>", width=80, margin=(10, 10)),
            pn.Column(question_column, width=250, margin=(5, 10)),
            pn.Column(answer_widget, margin=(5, 10), sizing_mode="stretch_width"),
            pn.Column(rationale_widget, margin=(5, 10), sizing_mode="stretch_width"),
            sizing_mode="stretch_width",
            styles={"background": row_bg, "border-bottom": "1px solid #ddd", "padding": "5px"}
        )
        
        table_rows.append(table_row)
    
    # Create complete table
    table = pn.Column(
        *table_rows,
        sizing_mode="stretch_width",
        styles={"border": "1px solid #ddd", "border-radius": "4px", "overflow": "hidden"}
    )
    
    return pn.Column(
        pn.pane.HTML("<h1>🛡️ Data Processing Assessment</h1>"),
        table,
        sizing_mode="stretch_width",
        margin=20,
        styles={"background": "white", "border-radius": "8px", "padding": "20px"}
    )

def read_form() -> Dict[str, Dict[str, str]]:
    """Read current form data from Panel widgets"""
    # Data is automatically synced via callbacks, just return current state
    return {qid: {"question": data["question"], "answer": data["answer"], "rationale": data["rationale"]} 
            for qid, data in form_data.items()}

def apply_edits(edits: List[Dict[str, Any]]) -> None:
    """Apply edits to form data and update Panel widgets"""
    for edit in edits:
        qid = edit.get("id")
        if qid in form_data and qid in form_widgets:
            # Update form_data
            if "answer" in edit:
                form_data[qid]["answer"] = edit["answer"]
                # Update widget (this will trigger callback but it's safe)
                form_widgets[qid]["answer"].value = edit["answer"]
            if "rationale" in edit:
                form_data[qid]["rationale"] = edit["rationale"]
                form_widgets[qid]["rationale"].value = edit["rationale"]

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
                {"id": "1.2.2", "answer": "Providing timely technical assistance to customers."},
                {"id": "2.1", "answer": "Name, email, phone number, technical issue descriptions."},
                {"id": "2.2", "answer": "Legitimate Interests"}
            ],
            "follow-up question": "Should I help you complete any other sections?"
        })
    
    if "show form" in user_msg.lower():
        form_summary = []
        for qid, data in current_form.items():
            status = "✅" if data["answer"] else "❌"
            form_summary.append(f"{status} **{qid}**: {data['question']}")
        form_status = "**Current Form Status:**\n\n" + "\n".join(form_summary)
        return json.dumps({
            "explanation of edits": form_status,
            "edits": [],
            "follow-up question": "Would you like me to help fill out any incomplete fields?"
        })
    
    if "clear form" in user_msg.lower():
        clear_edits = []
        for qid in current_form.keys():
            clear_edits.extend([
                {"id": qid, "answer": ""},
                {"id": qid, "rationale": ""}
            ])
        return json.dumps({
            "explanation of edits": "Cleared all form fields.",
            "edits": clear_edits,
            "follow-up question": "Ready to start fresh! What would you like to fill out first?"
        })
    
    # Handle specific field updates
    if "answer " in user_msg.lower() and ":" in user_msg:
        try:
            parts = user_msg.split(":", 1)
            field_part = parts[0].strip().lower()
            value = parts[1].strip()
            
            if field_part.startswith("answer "):
                field_id = field_part.replace("answer ", "")
                return json.dumps({
                    "explanation of edits": f"Updated answer for field {field_id}",
                    "edits": [{"id": field_id, "answer": value}],
                    "follow-up question": "Would you like to add a rationale for this answer?"
                })
            elif field_part.startswith("rationale "):
                field_id = field_part.replace("rationale ", "")
                return json.dumps({
                    "explanation of edits": f"Updated rationale for field {field_id}",
                    "edits": [{"id": field_id, "rationale": value}],
                    "follow-up question": "Anything else you'd like to update?"
                })
        except:
            pass
    
    return json.dumps({
        "explanation of edits": "",
        "edits": [],
        "follow-up question": "Try: 'title: My Project', 'autofill example', 'show form', 'clear form', or 'answer 1.1: your answer'."
    })

def on_message(contents, user, **kwargs):
    """Handle chat messages"""
    current_form = read_form()
    raw = fake_llm(str(contents), current_form)
    payload = parse_json(raw)
    
    if not payload:
        return "Could not parse valid JSON from model output."
    
    return handle_json_payload(payload)

# Create the form
form_panel = create_form_widgets()

# Create status display
status_pane = pn.pane.Markdown("**Status:** Form ready - all data automatically synced with Panel widgets!", margin=(10, 5))

# Create chat interface
chat = pn.chat.ChatInterface(
    callback=on_message,
    show_clear=False,
    placeholder_text="Try: 'title: My Project', 'autofill example', 'show form', or 'clear form'",
    sizing_mode="stretch_both",
)

# Send welcome message
chat.send("**🎯 CLEAN PANEL WIDGETS SOLUTION**\n\n✅ **Pure Panel widgets** - No iframe complexity\n💡 **? buttons work perfectly** - Toggle instructions with callbacks\n🔄 **Automatic sync** - Widget callbacks update form_data instantly\n📝 **LLM integration** - Updates widget values bidirectionally\n⚡ **Real-time** - Changes reflected immediately\n🧹 **Clean & Simple** - No JavaScript, no postMessage, no iframe isolation\n\n🎮 **Try these commands:**\n• `title: My Project Name`\n• `autofill example`\n• `show form`\n• `clear form`\n• `answer 1.1: Your custom answer`", user="System")

# Create layout
layout = pn.Row(
    pn.Column(
        "# 💬 Chat Assistant", 
        chat, 
        sizing_mode="stretch_both"
    ),
    pn.Column(
        "# 📋 Clean Panel Form",
        status_pane,
        form_panel,
        sizing_mode="stretch_both",
        scroll=True
    ),
    min_height=700,
    sizing_mode="stretch_both"
)

layout.servable()