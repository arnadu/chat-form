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
        
        # Generate row with working ? button (use safe_id for JavaScript)
        table_rows += f'''
            <tr>
                <td class="id-cell"><strong>{question.id}</strong></td>
                <td class="question-cell">
                    <div>
                        {html.escape(question.question)}
                        <button class="help-btn" onclick="toggleInstructions('{safe_id}')" title="Show/hide instructions">?</button>
                    </div>
                    <div id="instructions_{safe_id}" class="instructions">
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
            background: #e8e8e8;
            color: #666;
            border: 1px solid #ddd;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            cursor: pointer;
            font-size: 10px;
            margin-left: 6px;
            opacity: 0.7;
            transition: all 0.2s ease;
        }}
        
        .help-btn:hover {{
            background: #007acc;
            color: white;
            opacity: 1;
            transform: scale(1.1);
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
        <h1>🛡️ Data Processing Assessment</h1>
        
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
        console.log('🚀 Iframe JavaScript loaded successfully');
        
        // Toggle instructions visibility with localStorage persistence
        // This works perfectly in iframe context because event.target is available
        function toggleInstructions(questionId) {{
            console.log('Toggling instructions for:', questionId);
            
            const instructions = document.getElementById('instructions_' + questionId);
            const button = event.target; // ✅ Works in iframe!
            
            if (!instructions) {{
                console.error('Instructions element not found for:', questionId);
                return;
            }}
            
            if (instructions.classList.contains('show')) {{
                instructions.classList.remove('show');
                button.textContent = '?';
                button.style.background = '#e8e8e8';
                button.style.color = '#666';
                button.style.opacity = '0.7';
                localStorage.setItem('instructions_' + questionId, 'false');
                console.log('✅ Hiding instructions for:', questionId);
            }} else {{
                instructions.classList.add('show');
                button.textContent = '✕';
                button.style.background = '#888';
                button.style.color = 'white';
                button.style.opacity = '1';
                localStorage.setItem('instructions_' + questionId, 'true');
                console.log('✅ Showing instructions for:', questionId);
            }}
        }}
        
        // Restore instruction states from localStorage
        function restoreInstructionStates() {{
            const questions = {json.dumps([q.id.replace('.', '_') for q in FORM_QUESTIONS])};
            questions.forEach(safeId => {{
                const stored = localStorage.getItem('instructions_' + safeId);
                if (stored === 'true') {{
                    const instructions = document.getElementById('instructions_' + safeId);
                    const button = document.querySelector('button[onclick="toggleInstructions(\\'' + safeId + '\\')"]');
                    if (instructions && button) {{
                        instructions.classList.add('show');
                        button.textContent = '✕';
                        button.style.background = '#888';
                        button.style.color = 'white';
                        button.style.opacity = '1';
                    }}
                }}
            }});
            console.log('✅ Restored instruction states from localStorage');
        }}
        
        // Initialize on DOM load
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('✅ DOM loaded, restoring instruction states');
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

chat.send("**🚀 WORKING IFRAME SOLUTION**\n\n✅ Panel's recommended iframe+srcdoc approach\n💡 ? buttons toggle instructions perfectly\n🔥 JavaScript works reliably in iframe context\n📝 LLM integration updates form values", user="System")

# Create layout
layout = pn.Row(
    pn.Column("# 💬 Chat Assistant", chat, sizing_mode="stretch_both"),
    pn.Column("# 📋 Form with Working ? Buttons", html_pane, sizing_mode="stretch_both"),
    min_height=600,
    sizing_mode="stretch_both"
)

layout.servable()