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
    
    # Update the HTML form by regenerating it (preserves instruction state)
    if updates_made:
        update_form_display()

def parse_json(text: str) -> Dict[str, Any]:
    """Parse JSON from text, handling common formatting issues"""
    # Try to find JSON in the text
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

chat.send("**Dynamic HTML Form**\n\n✨ Single source of truth in Python\n⚡ Dynamically generated HTML\n🚀 Questions defined once, used everywhere", user="System")

# Create HTML pane (will be updated by update_form_display)
iframe = pn.pane.HTML(
    "",  # Will be populated by update_form_display
    sizing_mode="stretch_both",
    min_height=600
)

def update_form_display():
    """Update the HTML form display with current form_data"""
    # Generate HTML with current form data pre-filled
    html_content = generate_form_html_with_data()
    iframe.object = html_content

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
            input_html = f'''<textarea id="answer_{safe_id}" name="answer_{safe_id}" placeholder="Enter answer..." onchange="notifyParent()">{current_answer}</textarea>'''
        elif question.widget_type == "select":
            options_html = '<option value="">Select...</option>'
            for opt in question.options:
                selected = 'selected' if opt == current_answer else ''
                options_html += f'<option value="{opt}" {selected}>{opt}</option>'
            input_html = f'''<select id="answer_{safe_id}" name="answer_{safe_id}" onchange="notifyParent()">{options_html}</select>'''
        else:
            input_html = f'''<input type="text" id="answer_{safe_id}" name="answer_{safe_id}" placeholder="Enter answer..." value="{current_answer}" onchange="notifyParent()">'''
        
        # Generate rationale textarea with current value
        rationale_html = f'''<textarea id="rationale_{safe_id}" name="rationale_{safe_id}" placeholder="Explain rationale..." onchange="notifyParent()">{current_rationale}</textarea>'''
        
        # Generate row
        table_rows += f'''
            <tr>
                <td class="id-cell"><strong>{question.id}</strong></td>
                <td class="question-cell">
                    <div>
                        {question.question}
                        <button class="help-btn" onclick="toggleInstructions('{question.id}')" title="Show/hide instructions">?</button>
                    </div>
                    <div id="instructions_{question.id}" class="instructions">
                        {question.instructions}
                    </div>
                </td>
                <td>{input_html}</td>
                <td>{rationale_html}</td>
            </tr>
        '''
    
    # Complete HTML document
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
        // Store instruction state in browser storage to survive form refreshes
        const instructionStateKey = 'gdpr_form_instructions_state';
        
        function getInstructionState() {{
            const stored = localStorage.getItem(instructionStateKey);
            return stored ? JSON.parse(stored) : {{}};
        }}
        
        function setInstructionState(questionId, isVisible) {{
            const state = getInstructionState();
            state[questionId] = isVisible;
            localStorage.setItem(instructionStateKey, JSON.stringify(state));
        }}
        
        // Restore instruction states on page load
        function restoreInstructionStates() {{
            const state = getInstructionState();
            Object.keys(state).forEach(questionId => {{
                if (state[questionId]) {{
                    const instructions = document.getElementById(`instructions_${{questionId}}`);
                    const button = document.querySelector(`button[onclick="toggleInstructions('${{questionId}}')"`)`;
                    if (instructions && button) {{
                        instructions.classList.add('show');
                        button.textContent = '✕';
                    }}
                }}
            }});
        }}
        
        // Toggle instructions visibility
        function toggleInstructions(questionId) {{
            const instructions = document.getElementById(`instructions_${{questionId}}`);
            const button = event.target;
            
            if (instructions.classList.contains('show')) {{
                instructions.classList.remove('show');
                button.textContent = '?';
                setInstructionState(questionId, false);
            }} else {{
                instructions.classList.add('show');
                button.textContent = '✕';
                setInstructionState(questionId, true);
            }}
        }}

        // Notify of form changes
        function notifyParent() {{
            const formData = {{}};
            const inputs = document.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {{
                if (input.value) {{
                    formData[input.name] = input.value;
                }}
            }});
            
            console.log('Form data updated:', formData);
        }}
        
        // Restore states when DOM is loaded
        document.addEventListener('DOMContentLoaded', restoreInstructionStates);
        
        // Also restore states immediately (in case DOMContentLoaded already fired)
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', restoreInstructionStates);
        }} else {{
            restoreInstructionStates();
        }}
    </script>
</body>
</html>'''

# Initialize the form display
update_form_display()

# Add JavaScript to handle form updates directly in the page
js_code = """
<script>
// Global function to receive form data
window.updateFormData = function(data) {
    console.log('Form data updated:', data);
};

// Function to update the form with new data
window.updateFormFromPanel = function(formData) {
    if (window.updateForm) {
        window.updateForm(formData);
    }
};
</script>
"""

# Create layout
layout = pn.Column(
    pn.pane.HTML(js_code),  # Add our JavaScript
    pn.Row(
        pn.Column("# 💬 Chat", chat, sizing_mode="stretch_both"),
        pn.Column("# 📋 Form", iframe, sizing_mode="stretch_both"),
        min_height=600,
        sizing_mode="stretch_both"
    ),
    sizing_mode="stretch_both"
)

layout.servable()