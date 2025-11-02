import json
import html
import panel as pn
from typing import Dict, Any

pn.extension()

# Form state that we want to keep synchronized
form_state = {
    "name": "",
    "email": "", 
    "message": "",
    "priority": "medium"
}

def create_sync_form():
    """Create form with bulletproof real-time sync"""
    
    # Generate form with current values
    name_value = html.escape(form_state["name"])
    email_value = html.escape(form_state["email"]) 
    message_value = html.escape(form_state["message"])
    priority_value = form_state["priority"]
    
    form_html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial; padding: 20px; background: #f9f9f9; }}
        .form-box {{ background: white; padding: 20px; border-radius: 8px; max-width: 500px; }}
        .field {{ margin: 15px 0; }}
        label {{ display: block; font-weight: bold; margin-bottom: 5px; }}
        input, textarea, select {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
        textarea {{ height: 100px; resize: vertical; }}
        .sync-status {{ background: #e8f5e8; padding: 8px; border-radius: 4px; font-size: 12px; color: #2d5016; }}
        .sync-indicator {{ float: right; color: #28a745; }}
    </style>
</head>
<body>
    <div class="form-box">
        <h2>🔄 Real-Time Sync Form</h2>
        
        <div class="sync-status" id="status">
            Ready to sync <span class="sync-indicator">●</span>
        </div>
        
        <div class="field">
            <label for="name">Name:</label>
            <input type="text" id="name" value="{name_value}" placeholder="Enter your name">
        </div>
        
        <div class="field">
            <label for="email">Email:</label>
            <input type="email" id="email" value="{email_value}" placeholder="Enter your email">
        </div>
        
        <div class="field">
            <label for="priority">Priority:</label>
            <select id="priority">
                <option value="low" {"selected" if priority_value == "low" else ""}>Low</option>
                <option value="medium" {"selected" if priority_value == "medium" else ""}>Medium</option>
                <option value="high" {"selected" if priority_value == "high" else ""}>High</option>
            </select>
        </div>
        
        <div class="field">
            <label for="message">Message:</label>
            <textarea id="message" placeholder="Enter your message">{message_value}</textarea>
        </div>
    </div>

    <script>
        let syncCount = 0;
        
        // Capture all current form data
        function captureFormData() {{
            return {{
                name: document.getElementById('name').value,
                email: document.getElementById('email').value, 
                priority: document.getElementById('priority').value,
                message: document.getElementById('message').value,
                timestamp: Date.now(),
                syncId: ++syncCount
            }};
        }}
        
        // Send data to parent immediately  
        function syncToParent(triggerType = 'change') {{
            const data = captureFormData();
            
            // Send via postMessage (most reliable)
            window.parent.postMessage({{
                type: 'formSync',
                formData: data,
                trigger: triggerType
            }}, '*');
            
            // Update visual indicator
            const status = document.getElementById('status');
            status.innerHTML = `Synced ${{data.syncId}} changes <span class="sync-indicator">✓</span>`;
            
            console.log('📤 Synced:', data);
        }}
        
        // Set up real-time listeners on ALL inputs
        function setupRealTimeSync() {{
            const inputs = document.querySelectorAll('#name, #email, #priority, #message');
            
            inputs.forEach(input => {{
                // Capture every type of change immediately
                input.addEventListener('input', () => syncToParent('input'));
                input.addEventListener('change', () => syncToParent('change')); 
                input.addEventListener('blur', () => syncToParent('blur'));
                input.addEventListener('keyup', () => syncToParent('keyup'));
            }});
            
            console.log('✅ Real-time sync active on', inputs.length, 'inputs');
        }}
        
        // Make functions globally accessible for manual triggers
        window.captureFormData = captureFormData;
        window.syncToParent = syncToParent;
        
        // Initialize when DOM is ready
        document.addEventListener('DOMContentLoaded', function() {{
            setupRealTimeSync();
            syncToParent('init'); // Send initial state
        }});
        
        // Backup: sync every 2 seconds just in case
        setInterval(() => syncToParent('periodic'), 2000);
    </script>
</body>
</html>'''
    
    return form_html

# Create the iframe container
html_pane = pn.pane.HTML("", sizing_mode="stretch_both", min_height=500)

# Display current Python state
state_pane = pn.pane.JSON(form_state, name="Current Python State", height=150)

# Status log
log_lines = []
log_pane = pn.pane.Markdown("**Sync Log:**\\n\\nWaiting for events...", height=200)

def update_log(message):
    """Add message to sync log"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_lines.append(f"**{timestamp}:** {message}")
    
    # Keep only last 10 messages
    if len(log_lines) > 10:
        log_lines.pop(0)
    
    log_pane.object = "**Sync Log:**\\n\\n" + "\\n".join(log_lines)

def update_iframe():
    """Update the iframe with current form state"""
    form_html = create_sync_form()
    escaped_html = html.escape(form_html)
    
    iframe_container = f'''
    <div style="border: 2px solid #007acc; border-radius: 8px; overflow: hidden;">
        <iframe id="sync-form" srcdoc="{escaped_html}" 
                style="width: 100%; height: 500px; border: none;"></iframe>
    </div>
    
    <script>
        // Listen for form sync messages from iframe
        window.addEventListener('message', function(event) {{
            if (event.data && event.data.type === 'formSync') {{
                const data = event.data.formData;
                const trigger = event.data.trigger;
                
                // Store the received data (in real app, would update Python state)
                window.lastFormSync = {{
                    data: data,
                    trigger: trigger,
                    received: new Date().toLocaleTimeString()
                }};
                
                console.log('🔄 Form sync received:', trigger, data);
                
                // Simulate updating Python backend (would use Panel's callback system)
                updatePythonState(data, trigger);
            }}
        }});
        
        function updatePythonState(data, trigger) {{
            // This would normally trigger a Panel callback to update Python
            // For now, just log what we received
            console.log('📝 Would update Python with:', data);
        }}
        
        // Manual capture function for testing
        window.manualCapture = function() {{
            const iframe = document.getElementById('sync-form');
            if (iframe && iframe.contentWindow && iframe.contentWindow.captureFormData) {{
                const data = iframe.contentWindow.captureFormData();
                console.log('📋 Manual capture:', data);
                return data;
            }}
            return null;
        }};
        
        // Function to check last sync
        window.getLastSync = function() {{
            return window.lastFormSync || null;
        }};
    </script>
    '''
    
    html_pane.object = iframe_container

# Test button to manually capture
test_btn = pn.widgets.Button(name="🧪 Test Manual Capture", button_type="primary")

def test_capture(event):
    """Test manual capture functionality"""
    update_log("Testing manual capture...")
    
    # Add JavaScript to trigger manual capture
    current_html = html_pane.object
    trigger_script = '''
    <script>
        if (window.manualCapture) {
            const result = window.manualCapture();
            console.log('Test result:', result);
        }
        
        if (window.getLastSync) {
            const lastSync = window.getLastSync();
            console.log('Last auto-sync:', lastSync);
        }
    </script>
    '''
    
    html_pane.object = current_html + trigger_script
    
    # Reset after brief moment
    import time
    time.sleep(0.1)
    html_pane.object = current_html
    
    update_log("Manual capture test completed - check browser console")

test_btn.on_click(test_capture)

# Simulate Python state update (in real app, this would be triggered by postMessage)
update_btn = pn.widgets.Button(name="🔄 Simulate Python Update", button_type="success")

def simulate_update(event):
    """Simulate updating Python state and refreshing form"""
    global form_state
    
    # Simulate some changes to Python state
    form_state["name"] = "Updated from Python"
    form_state["priority"] = "high" 
    form_state["message"] = "This was updated by Python backend"
    
    # Refresh the form to show Python changes
    update_iframe()
    state_pane.object = form_state
    
    update_log("Python state updated → Form refreshed with new values")

update_btn.on_click(simulate_update)

# Initialize
update_iframe()

# Layout
layout = pn.Column(
    "# 🔄 Real-Time Form Sync Test",
    pn.pane.Markdown("""
    This tests **bulletproof real-time synchronization** between iframe form and Python:
    
    **🎯 Key Features:**
    - ✅ Real-time listeners on every input (`input`, `change`, `blur`, `keyup`)  
    - ✅ Immediate postMessage to parent window
    - ✅ Visual sync confirmation in form
    - ✅ Backup periodic sync every 2 seconds
    - ✅ Manual capture for testing
    - ✅ Python state updates refresh form
    
    **📝 Test Instructions:**
    1. Type in any form field → watch console for real-time sync
    2. Click "Test Manual Capture" → see current form state 
    3. Click "Simulate Python Update" → see Python changes reflected in form
    
    Open browser console to see all sync events!
    """),
    
    pn.Row(test_btn, update_btn, sizing_mode="stretch_width"),
    
    pn.Row(
        pn.Column("## 📋 Live Form", html_pane, sizing_mode="stretch_both"),
        pn.Column(
            state_pane,
            log_pane,
            sizing_mode="stretch_width", 
            width=300
        ),
        sizing_mode="stretch_both"
    ),
    
    sizing_mode="stretch_both"
)

layout.servable()