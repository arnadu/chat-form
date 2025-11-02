import json
import html
import panel as pn

pn.extension()

# Simple test data
test_questions = [
    {"id": "q1", "text": "Name", "value": ""},
    {"id": "q2", "text": "Email", "value": ""},
    {"id": "q3", "text": "Comments", "value": ""}
]

# Track current form state
current_state = {q["id"]: q["value"] for q in test_questions}

def generate_simple_form():
    """Generate a simple form with event listeners on every input"""
    
    form_html = '''<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial; padding: 20px; }
        input, textarea { width: 100%; margin: 5px 0; padding: 8px; }
        .field { margin: 10px 0; }
    </style>
</head>
<body>
    <h2>Simple Form Sync Test</h2>
    
    <div class="field">
        <label>Name:</label>
        <input type="text" id="q1" value="" placeholder="Enter your name">
    </div>
    
    <div class="field">
        <label>Email:</label>
        <input type="email" id="q2" value="" placeholder="Enter your email">
    </div>
    
    <div class="field">
        <label>Comments:</label>
        <textarea id="q3" placeholder="Enter comments"></textarea>
    </div>
    
    <script>
        console.log('🚀 Form loaded');
        
        // Method 1: Real-time listeners on each input
        function setupRealTimeSync() {
            const inputs = document.querySelectorAll('input, textarea');
            inputs.forEach(input => {
                // Listen to both change and input events
                input.addEventListener('input', function() {
                    const formData = getCurrentFormData();
                    syncToParent(formData, 'realtime');
                });
                
                input.addEventListener('change', function() {
                    const formData = getCurrentFormData();
                    syncToParent(formData, 'change');
                });
            });
            console.log('✅ Real-time sync setup on', inputs.length, 'inputs');
        }
        
        // Method 2: Capture all current form data
        function getCurrentFormData() {
            return {
                q1: document.getElementById('q1').value,
                q2: document.getElementById('q2').value,
                q3: document.getElementById('q3').value,
                timestamp: new Date().toISOString()
            };
        }
        
        // Method 3: Send data to parent window
        function syncToParent(data, trigger) {
            // Store in localStorage (parent can read this)
            localStorage.setItem('formSync', JSON.stringify({
                data: data,
                trigger: trigger,
                timestamp: new Date().toISOString()
            }));
            
            // Send via postMessage
            window.parent.postMessage({
                type: 'formSync',
                data: data,
                trigger: trigger
            }, '*');
            
            console.log('📤 Synced via', trigger, ':', data);
        }
        
        // Method 4: Global function for manual capture
        window.captureFormData = function() {
            const data = getCurrentFormData();
            syncToParent(data, 'manual');
            return data;
        };
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            setupRealTimeSync();
            // Send initial empty state
            syncToParent(getCurrentFormData(), 'init');
        });
    </script>
</body>
</html>'''
    
    return form_html

# Create HTML pane with iframe
html_pane = pn.pane.HTML("", sizing_mode="stretch_both", min_height=400)

# Status display
status_pane = pn.pane.Markdown("**Status:** Initializing...", margin=(10, 0))
data_pane = pn.pane.JSON({}, margin=(10, 0), height=200)

def update_form():
    """Update the iframe with form"""
    form_html = generate_simple_form()
    escaped_html = html.escape(form_html)
    
    iframe_html = f'''
    <div>
        <iframe id="form-iframe" srcdoc="{escaped_html}" 
                style="width:100%; height:400px; border:1px solid #ccc;"></iframe>
        
        <script>
        let lastSyncData = null;
        
        // Method A: Listen for postMessage from iframe
        window.addEventListener('message', function(event) {{
            if (event.data && event.data.type === 'formSync') {{
                lastSyncData = event.data;
                console.log('📨 Received sync:', event.data);
                updateStatus('Received ' + event.data.trigger + ' sync at ' + new Date().toLocaleTimeString());
            }}
        }});
        
        // Method B: Function to manually capture from iframe
        window.captureFromIframe = function() {{
            try {{
                const iframe = document.getElementById('form-iframe');
                if (iframe && iframe.contentWindow && iframe.contentWindow.captureFormData) {{
                    const data = iframe.contentWindow.captureFormData();
                    console.log('📋 Manual capture:', data);
                    updateStatus('Manual capture at ' + new Date().toLocaleTimeString());
                    return data;
                }} else {{
                    console.error('Cannot access iframe captureFormData');
                    return null;
                }}
            }} catch (error) {{
                console.error('Capture error:', error);
                return null;
            }}
        }};
        
        // Method C: Check localStorage periodically
        function checkLocalStorage() {{
            try {{
                const stored = localStorage.getItem('formSync');
                if (stored) {{
                    const syncData = JSON.parse(stored);
                    if (!lastSyncData || syncData.timestamp !== lastSyncData.timestamp) {{
                        lastSyncData = syncData;
                        console.log('💾 LocalStorage sync:', syncData);
                        updateStatus('LocalStorage sync: ' + syncData.trigger + ' at ' + new Date().toLocaleTimeString());
                    }}
                }}
            }} catch (error) {{
                console.error('LocalStorage check error:', error);
            }}
        }}
        
        function updateStatus(message) {{
            // This would need to be connected to Panel somehow
            console.log('Status:', message);
        }}
        
        // Check localStorage every second
        setInterval(checkLocalStorage, 1000);
        </script>
    </div>
    '''
    
    html_pane.object = iframe_html

# Create manual capture button
capture_btn = pn.widgets.Button(
    name="📋 Manual Capture", 
    button_type="primary",
    margin=(5, 0)
)

def manual_capture(event):
    """Manually trigger form data capture"""
    status_pane.object = "**Status:** Triggering manual capture..."
    
    # Add JavaScript to trigger capture
    current_html = html_pane.object
    trigger_script = '''
    <script>
        if (window.captureFromIframe) {
            const data = window.captureFromIframe();
            console.log('Manual trigger result:', data);
        }
    </script>
    '''
    
    html_pane.object = current_html + trigger_script
    
    # Reset after brief moment
    import time
    time.sleep(0.1)
    html_pane.object = current_html
    
    status_pane.object = "**Status:** Manual capture triggered - check console"

capture_btn.on_click(manual_capture)

# Create periodic check button  
check_btn = pn.widgets.Button(
    name="🔍 Check Storage", 
    button_type="light",
    margin=(5, 0)
)

def check_storage(event):
    """Check what's in localStorage"""
    status_pane.object = "**Status:** Checking localStorage..."
    
    # This is a simulation - in reality we'd need a way to read localStorage from Python
    # For now, just trigger a JavaScript check
    current_html = html_pane.object
    check_script = '''
    <script>
        try {
            const stored = localStorage.getItem('formSync');
            if (stored) {
                const data = JSON.parse(stored);
                console.log('📦 Current localStorage formSync:', data);
            } else {
                console.log('📦 No formSync data in localStorage');
            }
        } catch (error) {
            console.error('Storage check error:', error);
        }
    </script>
    '''
    
    html_pane.object = current_html + check_script
    
    import time
    time.sleep(0.1)
    html_pane.object = current_html
    
    status_pane.object = "**Status:** Storage check triggered - see console"

check_btn.on_click(check_storage)

# Initialize
update_form()

# Layout
layout = pn.Column(
    "# 🧪 Form Sync Experiment",
    "This tests different methods of capturing user input from an iframe form:",
    pn.Row(capture_btn, check_btn),
    status_pane,
    html_pane,
    "## Approaches Being Tested:",
    pn.pane.Markdown("""
**Method 1: Real-time listeners** - `input` and `change` events on every form field
**Method 2: PostMessage** - Iframe sends data to parent window  
**Method 3: LocalStorage** - Iframe writes, parent reads periodically
**Method 4: Manual capture** - Button triggers iframe data extraction

Open browser console to see the sync events in action!
    """),
    data_pane,
    sizing_mode="stretch_width"
)

layout.servable()