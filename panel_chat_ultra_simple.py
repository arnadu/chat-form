import json, re
import html
from typing import Dict, List, Any, NamedTuple
import panel as pn

pn.extension()

class FormQuestion(NamedTuple):
    id: str
    question: str
    instructions: str
    widget_type: str = "text"
    options: List[str] = None

# Define the form structure - clean and simple
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

# Initialize form data store from questions
form_data = {q.id: {"question": q.question, "answer": "", "rationale": ""} for q in FORM_QUESTIONS}

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

def generate_complete_html_document() -> str:
    """Generate a complete HTML document with JavaScript that works in iframe"""
    
    # Generate table rows
    table_rows = ""
    for question in FORM_QUESTIONS:
        safe_id = question.id.replace('.', '_')
        
        # Get current values
        current_answer = form_data.get(question.id, {}).get("answer", "")
        current_rationale = form_data.get(question.id, {}).get("rationale", "")
        
        # Escape HTML values
        current_answer = html.escape(current_answer)
        current_rationale = html.escape(current_rationale)
        
        # Generate input field based on type with current value
        if question.widget_type == "textarea":
            input_html = f'''<textarea id="answer_{safe_id}" name="answer_{safe_id}" placeholder="Enter answer...">{current_answer}</textarea>'''
        elif question.widget_type == "select" and question.options:
            options_html = '<option value="">Select...</option>'
            for opt in question.options:
                selected = 'selected' if opt == current_answer else ''
                options_html += f'<option value="{html.escape(opt)}" {selected}>{html.escape(opt)}</option>'
            input_html = f'''<select id="answer_{safe_id}" name="answer_{safe_id}">{options_html}</select>'''
        else:
            input_html = f'''<input type="text" id="answer_{safe_id}" name="answer_{safe_id}" placeholder="Enter answer..." value="{current_answer}">'''
        
        # Generate rationale textarea with current value
        rationale_html = f'''<textarea id="rationale_{safe_id}" name="rationale_{safe_id}" placeholder="Explain rationale...">{current_rationale}</textarea>'''
        
        # Generate row with working ? button
        table_rows += f'''
            <tr>
                <td class="id-cell"><strong>{question.id}</strong></td>
                <td class="question-cell">
                    <div>
                        {html.escape(question.question)}
                        <button class="help-btn" onclick="toggleInstructions('{question.id}')" title="Show/hide instructions">?</button>
                    </div>
                    <div id="instructions_{question.id}" class="instructions">
                        {html.escape(question.instructions)}
                    </div>
                </td>
                <td>{input_html}</td>
                <td>{rationale_html}</td>
            </tr>
        '''
    
    # Complete HTML document with working JavaScript (Panel's recommended iframe approach)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GDPR Assessment Form</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        
        .form-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #333;
            border-bottom: 2px solid #007acc;
            padding-bottom: 10px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th, td {{
            padding: 12px;
            border: 1px solid #ddd;
            text-align: left;
            vertical-align: top;
        }}
        
        th {{
            background-color: #007acc;
            color: white;
            font-weight: bold;
        }}
        
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
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
        
        .help-btn {{
            background: #007acc;
            color: white;
            border: none;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            cursor: pointer;
            font-size: 12px;
            margin-left: 8px;
        }}
        
        .help-btn:hover {{
            background: #005299;
        }}
        
        .instructions {{
            display: none;
            background: #e7f3ff;
            padding: 8px;
            margin-top: 4px;
            border-radius: 4px;
            border-left: 3px solid #007acc;
            font-size: 14px;
        }}
        
        .instructions.show {{
            display: block;
        }}
        
        .question-cell {{
            min-width: 200px;
        }}
        
        .id-cell {{
            width: 80px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="form-container">
        <h1>🛡️ GDPR Data Processing Assessment</h1>
        
        <table id="assessmentTable">
            <thead>
                <tr>
                    <th class="id-cell">ID</th>
                    <th class="question-cell">Question</th>
                    <th>Answer</th>
                    <th>Rationale</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>

    <script>
        console.log('Form JavaScript loaded successfully in iframe');
        
        // Toggle instructions visibility with localStorage persistence
        function toggleInstructions(questionId) {{
            console.log('Toggling instructions for:', questionId);
            
            const instructions = document.getElementById('instructions_' + questionId);
            const button = event.target;
            
            if (!instructions) {{
                console.error('Instructions element not found for:', questionId);
                return;
            }}
            
            if (instructions.classList.contains('show')) {{
                instructions.classList.remove('show');
                button.textContent = '?';
                localStorage.setItem('instructions_' + questionId, 'false');
                console.log('Hiding instructions for:', questionId);
            }} else {{
                instructions.classList.add('show');
                button.textContent = '✕';
                localStorage.setItem('instructions_' + questionId, 'true');
                console.log('Showing instructions for:', questionId);
            }}
        }}
        
        // Restore instruction states from localStorage
        function restoreInstructionStates() {{
            const questions = {json.dumps([q.id for q in FORM_QUESTIONS])};
            questions.forEach(questionId => {{
                const stored = localStorage.getItem('instructions_' + questionId);
                if (stored === 'true') {{
                    const instructions = document.getElementById('instructions_' + questionId);
                    const button = document.querySelector(`button[onclick="toggleInstructions('${{questionId}}')"`)`;
                    if (instructions && button) {{
                        instructions.classList.add('show');
                        button.textContent = '✕';
                    }}
                }}
            }});
        }}
        
        // Initialize on DOM load
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('DOM loaded, restoring instruction states');
            restoreInstructionStates();
        }});
        
        // Also restore immediately in case DOMContentLoaded already fired
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', restoreInstructionStates);
        }} else {{
            restoreInstructionStates();
        }}
    </script>
</body>
</html>'''

# Create HTML pane using iframe with srcdoc (Panel's recommended approach)
html_pane = pn.pane.HTML("", sizing_mode="stretch_both", min_height=600)

def update_form_display():
    """Update the HTML form display using iframe with srcdoc"""
    # Generate complete HTML document
    html_content = generate_complete_html_document()
    
    # Escape the HTML for srcdoc attribute (Panel's recommended approach)
    escaped_html = html.escape(html_content)
    
    # Create iframe with escaped HTML in srcdoc
    iframe_html = f'<iframe srcdoc="{escaped_html}" style="height:100%; width:100%; min-height:600px;" frameborder="0"></iframe>'
    
    # Update the HTML pane
    html_pane.object = iframe_html

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

chat.send("**Iframe + srcdoc Approach**\n\n✨ Panel's recommended HTML iframe method\n⚡ Working JavaScript in isolated iframe\n🚀 ? buttons should work perfectly!", user="System")

# Create layout
layout = pn.Row(
    pn.Column("# 💬 Chat", chat, sizing_mode="stretch_both"),
    pn.Column("# 📋 Form with Working ? Buttons (iframe)", html_pane, sizing_mode="stretch_both"),
    min_height=600,
    sizing_mode="stretch_both"
)

layout.servable()
def create_simple_form():
    # Store widgets in a simple dictionary
    widgets = {}
    
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
        # Create widgets directly - no parameter binding needed
        if q.widget_type == "textarea":
            answer_widget = pn.widgets.TextAreaInput(
                placeholder="Enter answer...", height=60, name=""
            )
        elif q.widget_type == "select" and q.options:
            answer_widget = pn.widgets.Select(
                options=[""] + q.options, height=60, name=""
            )
        else:
            answer_widget = pn.widgets.TextInput(
                placeholder="Enter answer...", height=60, name=""
            )
        
        rationale_widget = pn.widgets.TextAreaInput(
            placeholder="Explain reasoning...", height=60, name=""
        )
        
        # Store widgets for easy access later
        widgets[q.id] = {
            "answer": answer_widget,
            "rationale": rationale_widget,
            "question": q.question,
            "instructions": q.instructions
        }
        
        # Create help button
        help_button = pn.widgets.Button(name="?", width=40, height=40, button_type="primary")
        
        # Create instruction panel
        instruction_panel = pn.pane.Markdown(
            f"**Instructions:** {q.instructions}",
            visible=False,
            sizing_mode='stretch_width',
            styles={'background': '#f0f8ff', 'padding': '10px', 'border': '1px solid #007acc'}
        )
        
        # Simple toggle function
        def make_toggle(panel):
            def toggle(event):
                panel.visible = not panel.visible
            return toggle
            
        help_button.on_click(make_toggle(instruction_panel))
        
        # Create table row
        table_row = pn.Row(
            pn.pane.HTML(f"<strong>{q.id}</strong>", width=80, height=60, sizing_mode='fixed'),
            pn.pane.HTML(q.question, sizing_mode='stretch_width'),
            answer_widget,
            rationale_widget, 
            help_button,
            styles={'padding': '5px', 'border-bottom': '1px solid #eee'}
        )
        
        row_container = pn.Column(table_row, instruction_panel, sizing_mode='stretch_width')
        form_rows.append(row_container)
    
    return pn.Column(*form_rows, sizing_mode='stretch_width'), widgets

# Create form and widgets
form_widgets, widget_dict = create_simple_form()

# Simple helper functions - no complex parameter mapping
def read_form() -> Dict[str, Dict[str, str]]:
    """Read form data - much simpler!"""
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
    """Apply edits - much cleaner!"""
    for edit in edits:
        qid = edit.get("id")
        if qid in widget_dict:
            if "answer" in edit:
                widget_dict[qid]["answer"].value = edit["answer"]
            if "rationale" in edit:
                widget_dict[qid]["rationale"].value = edit["rationale"]

# Rest of the code remains the same...
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
    if user_msg.lower().startswith("title:"):
        val = user_msg.split(":", 1)[1].strip()
        return json.dumps({
            "explanation of edits": f"Set the project title to '{val}'.",
            "edits": [{"id": "1.1", "answer": val}],
            "follow-up question": "Would you like me to help with the project summary (1.2.1)?"
        })
    
    if "autofill example" in user_msg.lower():
        return json.dumps({
            "explanation of edits": "Added example GDPR assessment data.",
            "edits": [
                {"id": "1.1", "answer": "Customer Support Data Processing"},
                {"id": "1.2.1", "answer": "Processing customer contact information for technical support."},
                {"id": "2.2", "answer": "Legitimate Interests"}
            ],
            "follow-up question": "Should I help you complete the data types section (2.1)?"
        })
    
    return json.dumps({
        "explanation of edits": "",
        "edits": [],
        "follow-up question": "I can help you fill out the form. Try 'autofill example' or 'title: My Project'."
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

chat.send("**Simple Form Assistant**\n\nTry: 'title: My Project' or 'autofill example'", user="System")

# Create layout
layout = pn.Row(
    pn.Column("# 💬 Chat", chat, sizing_mode="stretch_both"),
    pn.Column("# 📋 Form", form_widgets, sizing_mode="stretch_both"),
    min_height=600,
    sizing_mode="stretch_both"
)

layout.servable()