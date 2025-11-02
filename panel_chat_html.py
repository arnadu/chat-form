import json, re
from typing import Dict, List, Any, NamedTuple
import panel as pn
import param

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

def generate_form_html():
    """Generate a complete HTML form - much more performant!"""
    
    # Generate select options for dropdown questions
    def make_options(question):
        if question.widget_type == "select" and question.options:
            options = '<option value="">Select...</option>'
            for opt in question.options:
                options += f'<option value="{opt}">{opt}</option>'
            return options
        return ""
    
    # Generate input field based on type
    def make_input(question):
        safe_id = question.id.replace('.', '_')
        if question.widget_type == "textarea":
            return f'''<textarea id="answer_{safe_id}" name="answer_{safe_id}" 
                      placeholder="Enter answer..." rows="3" 
                      style="width:100%; resize:vertical; padding:8px; border:1px solid #ddd; border-radius:4px;"></textarea>'''
        elif question.widget_type == "select":
            return f'''<select id="answer_{safe_id}" name="answer_{safe_id}" 
                      style="width:100%; padding:8px; border:1px solid #ddd; border-radius:4px; height:50px;">
                      {make_options(question)}</select>'''
        else:
            return f'''<input type="text" id="answer_{safe_id}" name="answer_{safe_id}" 
                      placeholder="Enter answer..." 
                      style="width:100%; padding:8px; border:1px solid #ddd; border-radius:4px; height:34px;" />'''
    
    # Generate rationale field (always textarea)
    def make_rationale(question):
        safe_id = question.id.replace('.', '_')
        return f'''<textarea id="rationale_{safe_id}" name="rationale_{safe_id}" 
                  placeholder="Explain reasoning..." rows="3"
                  style="width:100%; resize:vertical; padding:8px; border:1px solid #ddd; border-radius:4px;"></textarea>'''
    
    # Generate the complete HTML form
    html = '''
    <style>
        .form-table {
            width: 100%;
            border-collapse: collapse;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
        }
        .form-table th {
            background: #f5f5f5;
            padding: 12px 8px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #ddd;
        }
        .form-table td {
            padding: 8px;
            border-bottom: 1px solid #eee;
            vertical-align: top;
        }
        .question-cell {
            width: 25%;
            max-width: 200px;
        }
        .answer-cell, .rationale-cell {
            width: 35%;
        }
        .help-cell {
            width: 5%;
            text-align: center;
        }
        .help-btn {
            background: #007acc;
            color: white;
            border: none;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
        }
        .help-btn:hover {
            background: #005a99;
        }
        .instructions {
            display: none;
            background: #f0f8ff;
            padding: 10px;
            margin: 5px 0;
            border-left: 4px solid #007acc;
            font-size: 0.9em;
            line-height: 1.4;
        }
        .instructions.show {
            display: block;
        }
        .question-id {
            font-weight: bold;
            color: #333;
        }
    </style>
    
    <table class="form-table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Question</th>
                <th>Answer</th>
                <th>Rationale</th>
                <th>?</th>
            </tr>
        </thead>
        <tbody>
    '''
    
    for q in FORM_QUESTIONS:
        safe_id = q.id.replace('.', '_')
        html += f'''
            <tr>
                <td class="question-cell">
                    <div class="question-id">{q.id}</div>
                    <div style="font-size: 0.9em; margin-top: 4px;">{q.question}</div>
                    <div id="instructions_{safe_id}" class="instructions">
                        <strong>Instructions:</strong> {q.instructions}
                    </div>
                </td>
                <td class="answer-cell">
                    {make_input(q)}
                </td>
                <td class="rationale-cell">
                    {make_rationale(q)}
                </td>
                <td class="help-cell">
                    <button class="help-btn" type="button" onclick="toggleInstructions('{safe_id}')">?</button>
                </td>
            </tr>
        '''
    
    html += '''
        </tbody>
    </table>
    
    <script>
        function toggleInstructions(id) {
            const instructions = document.getElementById('instructions_' + id);
            instructions.classList.toggle('show');
        }
        
        // Function to get all form data - called by Panel
        function getFormData() {
            const data = {};
            const inputs = document.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                if (input.name) {
                    data[input.name] = input.value;
                }
            });
            return data;
        }
        
        // Function to set form data - called by Panel
        function setFormData(updates) {
            for (const [fieldName, value] of Object.entries(updates)) {
                const element = document.querySelector(`[name="${fieldName}"]`);
                if (element) {
                    element.value = value;
                }
            }
        }
    </script>
    '''
    
    return html

# Create a working HTML form with proper Panel integration
class WorkingHTMLForm(pn.reactive.ReactiveHTML):
    """HTML form with proper Panel integration"""
    
    # Parameters to track form state
    form_data = param.Dict(default={})
    
    _template = generate_form_html()
    
    _scripts = {
        'click': """
            // Handle help button clicks
            if (event.target.classList.contains('help-btn')) {
                const id = event.target.getAttribute('onclick').match(/toggleInstructions\\('([^']+)'\\)/)[1];
                const instructions = document.getElementById('instructions_' + id);
                instructions.classList.toggle('show');
            }
        """,
        'change': """
            // Handle form field changes - sync back to Panel
            if (event.target.name) {
                const formData = {};
                const inputs = document.querySelectorAll('input, textarea, select');
                inputs.forEach(input => {
                    if (input.name) {
                        formData[input.name] = input.value;
                    }
                });
                data.form_data = formData;
            }
        """,
        'update_fields': """
            // Execute JavaScript code to update form fields
            try {
                eval(event.detail);
            } catch (e) {
                console.error('Error updating fields:', e);
            }
        """
    }

# Create the form
html_form = WorkingHTMLForm()

# Initialize form data store
form_data = {q.id: {"answer": "", "rationale": "", "question": q.question, "instructions": q.instructions} 
             for q in FORM_QUESTIONS}

def read_form() -> Dict[str, Dict[str, str]]:
    """Read form data from HTML form and our data store"""
    # Get current form data from HTML (if available)
    current_html_data = html_form.form_data or {}
    
    # Update our data store with HTML form values
    for q in FORM_QUESTIONS:
        safe_id = q.id.replace('.', '_')
        answer_key = f"answer_{safe_id}"
        rationale_key = f"rationale_{safe_id}"
        
        if answer_key in current_html_data:
            form_data[q.id]["answer"] = current_html_data[answer_key]
        if rationale_key in current_html_data:
            form_data[q.id]["rationale"] = current_html_data[rationale_key]
    
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
    
    # Update the HTML form with new values
    if updates_made:
        update_html_form()

def update_html_form():
    """Update HTML form fields with current form_data values"""
    js_updates = []
    for q in FORM_QUESTIONS:
        safe_id = q.id.replace('.', '_')
        answer_value = form_data[q.id]["answer"]
        rationale_value = form_data[q.id]["rationale"]
        
        if answer_value:
            js_updates.append(f'document.getElementById("answer_{safe_id}").value = {json.dumps(answer_value)};')
        if rationale_value:
            js_updates.append(f'document.getElementById("rationale_{safe_id}").value = {json.dumps(rationale_value)};')
    
    if js_updates:
        # Execute JavaScript to update form fields
        js_code = '\n'.join(js_updates)
        # Trigger JavaScript execution to update form fields
        html_form.send_event("update_fields", js_code)

# Rest of the LLM and chat code (same as before)
def parse_json(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text) if isinstance(json.loads(text), dict) else {}
    except Exception:
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        return json.loads(match.group(1)) if match else {}

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

chat.send("**Ultra-High-Performance HTML Form**\n\n✨ Single HTML document\n⚡ JavaScript-powered\n🚀 Maximum performance", user="System")

# Create layout
layout = pn.Row(
    pn.Column("# 💬 Chat", chat, sizing_mode="stretch_both"),
    pn.Column("# 📋 HTML Form", html_form, sizing_mode="stretch_both"),
    min_height=600,
    sizing_mode="stretch_both"
)

layout.servable()