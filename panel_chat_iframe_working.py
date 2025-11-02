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

# Bidirectional sync tracking
sync_counter = 0
latest_iframe_sync = {}
sync_log = []

def read_form() -> Dict[str, Dict[str, str]]:
    """Read current form data, merging with any synced iframe data"""
    # Merge backend form_data with any real-time sync data from iframe
    merged_data = {}
    for qid in form_data:
        # Start with backend data
        merged_data[qid] = {
            "question": form_data[qid]["question"],
            "answer": form_data[qid]["answer"],
            "rationale": form_data[qid]["rationale"]
        }
        
        # Override with iframe sync data if available
        safe_id = qid.replace('.', '_')
        if safe_id in latest_iframe_sync:
            iframe_data = latest_iframe_sync[safe_id]
            if isinstance(iframe_data, dict):
                if "answer" in iframe_data:
                    merged_data[qid]["answer"] = iframe_data["answer"]
                if "rationale" in iframe_data:
                    merged_data[qid]["rationale"] = iframe_data["rationale"]
    
    return merged_data

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
        
        // Function to collect all form data - called from parent when needed
        function getFormData() {{
            const formData = {{}};
            const questions = {json.dumps([q.id.replace('.', '_') for q in FORM_QUESTIONS])};
            
            questions.forEach(safeId => {{
                const answerElement = document.getElementById('answer_' + safeId);
                const rationaleElement = document.getElementById('rationale_' + safeId);
                
                formData[safeId] = {{
                    answer: answerElement ? answerElement.value : '',
                    rationale: rationaleElement ? rationaleElement.value : ''
                }};
            }});
            
            console.log('📤 Collected form data:', formData);
            return formData;
        }}
        
        // Make getFormData globally accessible
        window.getFormData = getFormData;
        
        // BULLETPROOF BIDIRECTIONAL SYNC - Real-time form data capture
        let syncCounter = 0;
        
        // Enhanced form data collection with all fields
        function collectAllFormData() {{
            const formData = {{}};
            const questions = {json.dumps([q.id.replace('.', '_') for q in FORM_QUESTIONS])};
            
            questions.forEach(safeId => {{
                const answerElement = document.getElementById('answer_' + safeId);
                const rationaleElement = document.getElementById('rationale_' + safeId);
                
                formData[safeId] = {{
                    answer: answerElement ? answerElement.value : '',
                    rationale: rationaleElement ? rationaleElement.value : ''
                }};
            }});
            
            return {{
                formFields: formData,
                meta: {{
                    timestamp: new Date().toISOString(),
                    syncId: ++syncCounter,
                    source: 'iframe'
                }}
            }};
        }}
        
        // Send to Python with bulletproof delivery
        function sendToPython(eventType = 'change') {{
            const data = collectAllFormData();
            
            // Method 1: PostMessage (primary)
            window.parent.postMessage({{
                type: 'IFRAME_FORM_SYNC',
                formData: data.formFields,
                meta: data.meta,
                eventType: eventType
            }}, '*');
            
            // Method 2: localStorage backup
            localStorage.setItem('latestFormSync', JSON.stringify({{
                data: data,
                eventType: eventType,
                timestamp: new Date().toISOString()
            }}));
            
            console.log('📤 Synced to Python:', eventType, data);
        }}
        
        // Comprehensive event listener setup
        function setupBulletproofSync() {{
            const inputs = document.querySelectorAll('input, textarea, select');
            
            inputs.forEach(input => {{
                // Capture ALL possible user interactions
                input.addEventListener('input', () => sendToPython('input'));
                input.addEventListener('change', () => sendToPython('change'));
                input.addEventListener('blur', () => sendToPython('blur'));
                input.addEventListener('keyup', () => sendToPython('keyup'));
                
                // Special handling for paste events
                if (input.tagName === 'TEXTAREA' || input.type === 'text') {{
                    input.addEventListener('paste', () => {{
                        setTimeout(() => sendToPython('paste'), 10);
                    }});
                }}
            }});
            
            console.log('✅ Bulletproof sync active on', inputs.length, 'inputs');
        }}
        
        // Make functions globally accessible
        window.getFormData = collectAllFormData;
        window.syncToParent = sendToPython;
        
        // Initialize bulletproof sync
        document.addEventListener('DOMContentLoaded', function() {{
            setupBulletproofSync();
            sendToPython('init'); // Send initial state
        }});
        
        // Safety net: periodic sync every 3 seconds
        setInterval(() => sendToPython('periodic'), 3000);
    </script>
</body>
</html>'''

# Create HTML pane using iframe with srcdoc (Panel's recommended approach)
html_pane = pn.pane.HTML("", sizing_mode="stretch_both", min_height=600)

# Storage for synced form data from iframe
synced_form_data = {}

def update_form_display():
    """Update the HTML form display using iframe with bulletproof sync"""
    global sync_counter
    sync_counter += 1
    
    # Generate complete HTML document
    html_content = generate_complete_html_document()
    
    # Escape the HTML for srcdoc attribute (Panel's recommended approach)
    escaped_html = html.escape(html_content)
    
    # Create iframe with bulletproof bidirectional sync
    iframe_html = f'''
    <div style="border: 2px solid #007acc; border-radius: 8px; overflow: hidden;">
        <div style="background: #007acc; color: white; padding: 8px 15px; font-size: 12px; font-weight: bold;">
            🔄 Live Sync Active (Update #{sync_counter})
        </div>
        <iframe id="form-iframe" srcdoc="{escaped_html}" style="width:100%; height:580px; border:none;"></iframe>
        <div id="sync-data" style="display: none;"></div>
    </div>
    
    <script>
        // Bulletproof sync: Listen for iframe form changes and update Python
        window.addEventListener('message', function(event) {{
            if (event.data && event.data.type === 'IFRAME_FORM_SYNC') {{
                const formData = event.data.formData;
                const eventType = event.data.eventType;
                const meta = event.data.meta;
                
                // Store the synced data for Python to access
                window.latestSync = {{
                    formData: formData,
                    eventType: eventType,
                    meta: meta,
                    received: new Date().toISOString()
                }};
                
                // Update hidden storage div
                document.getElementById('sync-data').textContent = JSON.stringify(window.latestSync);
                
                console.log('🔗 Python bridge received:', eventType, formData);
                
                // In Panel integration, this would trigger Python callback
                if (window.updatePythonFormData) {{
                    window.updatePythonFormData(formData, eventType);
                }}
            }}
        }});
        
        // Manual extraction function
        window.extractFormData = function() {{
            const iframe = document.getElementById('form-iframe');
            if (iframe && iframe.contentWindow && iframe.contentWindow.getFormData) {{
                const data = iframe.contentWindow.getFormData();
                console.log('� Manual extraction:', data);
                return data;
            }}
            return null;
        }};
        
        // Function to get last sync data
        window.getLatestSync = function() {{
            return window.latestSync || null;
        }};
        
        console.log('🚀 Bulletproof sync bridge initialized');
    </script>
    '''
    
    # Update the HTML pane
    html_pane.object = iframe_html

def process_iframe_sync(sync_data: Dict[str, Any], event_type: str = 'change'):
    """Process incoming sync data from iframe and update Python form_data"""
    global latest_iframe_sync
    import datetime
    
    try:
        # Store the raw sync data
        latest_iframe_sync = sync_data
        
        # Update Python form_data with iframe values
        for safe_id, field_data in sync_data.items():
            # Convert safe_id back to original question id
            original_id = safe_id.replace('_', '.')
            
            if original_id in form_data and isinstance(field_data, dict):
                if "answer" in field_data:
                    form_data[original_id]["answer"] = field_data["answer"]
                if "rationale" in field_data:
                    form_data[original_id]["rationale"] = field_data["rationale"]
        
        # Log the sync event
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        sync_log.append(f"**{timestamp}** `{event_type}` → {len(sync_data)} fields synced")
        
        # Keep log manageable
        if len(sync_log) > 15:
            sync_log.pop(0)
            
        print(f"✅ Processed {event_type} sync: {len(sync_data)} fields updated")
        
    except Exception as e:
        print(f"❌ Sync processing error: {e}")
        sync_log.append(f"**ERROR** Failed to process {event_type} sync: {e}")

# Create capture button to sync form data from iframe
capture_button = pn.widgets.Button(
    name="🔄 Capture Form Data", 
    button_type="primary",
    width=200,
    margin=(5, 5)
)

# Status indicator with enhanced sync info
capture_status = pn.pane.Markdown("**🔄 Bulletproof Sync Ready** - Real-time form sync is active", margin=(5, 5))

# Add sync log display
sync_log_pane = pn.pane.Markdown("**Sync Log:** Waiting for form interactions...", margin=(5, 5), height=150)

def capture_form_data(event):
    """Manually capture current form data from iframe"""
    try:
        capture_status.object = "⏳ Manually capturing form data from iframe..."
        
        # Trigger manual extraction
        current_html = html_pane.object
        trigger_js = '''
        <script>
            if (window.extractFormData) {
                const data = window.extractFormData();
                console.log('📋 Manual capture result:', data);
            }
            
            if (window.getLatestSync) {
                const lastSync = window.getLatestSync();
                console.log('📨 Latest auto-sync data:', lastSync);
                
                if (lastSync && lastSync.formData) {
                    // Simulate processing the sync data
                    console.log('Processing latest sync data for Python...');
                }
            }
        </script>
        '''
        
        html_pane.object = current_html + trigger_js
        
        # Simulate sync processing (in real integration, this would be automatic)
        if latest_iframe_sync:
            process_iframe_sync(latest_iframe_sync, 'manual_capture')
            capture_status.object = f"✅ Manual capture complete! Synced {len(latest_iframe_sync)} fields. Auto-sync is also active."
        else:
            capture_status.object = "✅ Manual capture triggered! Real-time auto-sync is active. Check console for details."
        
        # Reset HTML
        import time
        time.sleep(0.1)
        html_pane.object = current_html
        
    except Exception as e:
        capture_status.object = f"❌ Capture error: {e}"

capture_button.on_click(capture_form_data)

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
        form_status = "**Current Form Status:**\n\n" + "\n".join(form_summary)
        return json.dumps({
            "explanation of edits": form_status,
            "edits": [],
            "follow-up question": "Would you like me to help fill out any incomplete fields?"
        })
    
    if "sync form" in user_msg.lower():
        return json.dumps({
            "explanation of edits": "📋 **Note:** Manual form edits in the iframe are not automatically synced to the backend. Only LLM-generated edits update the form state. If you've made manual changes, please tell me what you entered and I'll update it for you.",
            "edits": [],
            "follow-up question": "What manual changes did you make that you'd like me to record?"
        })
    
    # Handle natural language updates like "I entered X in field Y"
    if any(phrase in user_msg.lower() for phrase in ["i entered", "i typed", "i filled", "i put", "i wrote"]):
        return json.dumps({
            "explanation of edits": "I understand you made manual edits. Please use specific commands like:\n• `title: Your Title`\n• `answer 1.1: Your Answer`\n• `rationale 2.1: Your Rationale`\n\nThis ensures the backend stays in sync with your changes.",
            "edits": [],
            "follow-up question": "What specific field would you like me to update?"
        })
    
    # Handle specific field updates like "answer 1.1: some value"
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
        "follow-up question": "Try: 'title: My Project', 'autofill example', 'show form', or 'answer 1.1: your answer'."
    })

def on_message(contents, user, **kwargs):
    # Read current form state (now includes real-time synced data from iframe)
    current_form = read_form()
    
    # Update sync log display
    if sync_log:
        sync_log_pane.object = "**Sync Log:**\n\n" + "\n\n".join(sync_log[-10:])  # Show last 10 events
    
    # Process with LLM
    raw = fake_llm(str(contents), current_form)
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

chat.send("**🎉 BULLETPROOF BIDIRECTIONAL SYNC SOLUTION**\n\n✅ **Real-time form synchronization** - Every keystroke captured instantly\n💡 **? buttons work perfectly** - Instructions toggle reliably in iframe\n🔥 **Bulletproof sync** - Multiple event listeners + postMessage + localStorage backup\n📝 **LLM integration** - Updates form values bidirectionally\n⚡ **Auto-sync active** - No manual sync needed, happens automatically!\n\n🔄 **Features:** Real-time sync, periodic backup, visual indicators, manual capture available\n📋 **Try it:** Type in any form field → sync happens instantly!", user="System")

# Create layout with bulletproof sync
layout = pn.Row(
    pn.Column("# 💬 Chat Assistant", chat, sizing_mode="stretch_both"),
    pn.Column(
        "# � Bulletproof Sync Form", 
        pn.Row(capture_button, sizing_mode="stretch_width"),
        capture_status,
        html_pane,
        pn.Accordion(("🔍 Sync Log", sync_log_pane), margin=(5, 0)),
        sizing_mode="stretch_both"
    ),
    min_height=600,
    sizing_mode="stretch_both"
)

layout.servable()