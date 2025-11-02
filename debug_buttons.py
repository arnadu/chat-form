import panel as pn
import html

pn.extension()

def test_iframe_buttons():
    """Test iframe buttons with minimal HTML to debug the issue"""
    
    # Very simple HTML with just one button
    simple_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial; padding: 20px; }
            button { 
                background: #007acc; 
                color: white; 
                border: none; 
                padding: 10px 15px; 
                border-radius: 4px; 
                cursor: pointer; 
                margin: 10px 5px;
            }
            .instructions { 
                display: none; 
                background: #e7f3ff; 
                padding: 10px; 
                margin: 10px 0; 
                border: 1px solid #007acc;
            }
            .show { display: block; }
        </style>
    </head>
    <body>
        <h2>🧪 Iframe Button Test</h2>
        
        <p>Testing basic button functionality:</p>
        
        <button onclick="testAlert()">Test Alert</button>
        <button onclick="toggleDiv()">Toggle Div</button>
        <button onclick="changeColor()">Change Color</button>
        
        <div id="test-div" style="padding: 10px; background: lightblue; margin: 10px 0;">
            Click "Toggle Div" to hide/show me
        </div>
        
        <div id="color-div" style="padding: 10px; background: lightgreen; margin: 10px 0;">
            Click "Change Color" to change my background
        </div>
        
        <h3>? Button Test:</h3>
        <p>Question: What is your name?
           <button onclick="toggleInstructions('name')" id="help-btn-name">?</button>
        </p>
        
        <div id="instructions-name" class="instructions">
            <strong>Instructions:</strong> Enter your full name as it appears on official documents.
        </div>
        
        <input type="text" placeholder="Enter your name..." style="width: 100%; padding: 8px; margin: 5px 0;">
        
        <script>
            console.log('🚀 Simple iframe test loaded');
            
            function testAlert() {
                alert('Alert works!');
                console.log('✅ Alert function called');
            }
            
            function toggleDiv() {
                const div = document.getElementById('test-div');
                if (div.style.display === 'none') {
                    div.style.display = 'block';
                    console.log('✅ Showing div');
                } else {
                    div.style.display = 'none';
                    console.log('✅ Hiding div');
                }
            }
            
            function changeColor() {
                const div = document.getElementById('color-div');
                const colors = ['lightgreen', 'lightcoral', 'lightblue', 'lightyellow'];
                const current = div.style.backgroundColor || 'lightgreen';
                const currentIndex = colors.indexOf(current);
                const nextIndex = (currentIndex + 1) % colors.length;
                div.style.backgroundColor = colors[nextIndex];
                console.log('✅ Changed color to:', colors[nextIndex]);
            }
            
            function toggleInstructions(id) {
                console.log('🔘 Toggling instructions for:', id);
                const instructions = document.getElementById('instructions-' + id);
                const button = document.getElementById('help-btn-' + id);
                
                if (!instructions) {
                    console.error('❌ Instructions element not found');
                    return;
                }
                
                if (!button) {
                    console.error('❌ Button element not found');
                    return;
                }
                
                if (instructions.classList.contains('show')) {
                    instructions.classList.remove('show');
                    button.textContent = '?';
                    button.style.background = '#007acc';
                    console.log('✅ Instructions hidden');
                } else {
                    instructions.classList.add('show');
                    button.textContent = '✕';
                    button.style.background = '#666';
                    console.log('✅ Instructions shown');
                }
            }
        </script>
    </body>
    </html>
    """
    
    # Create iframe using Panel's method
    escaped_html = html.escape(simple_html)
    iframe_html = f'<iframe srcdoc="{escaped_html}" style="width:100%; height:500px; border:1px solid #ddd;" frameborder="0"></iframe>'
    
    iframe_pane = pn.pane.HTML(iframe_html, height=550, sizing_mode="stretch_width")
    
    # Also test direct HTML for comparison
    direct_pane = pn.pane.HTML("""
    <div style="padding: 20px; border: 2px solid orange;">
        <h3>Direct HTML Test (for comparison)</h3>
        <button onclick="alert('Direct HTML alert')">Direct Alert</button>
        <p><em>This might not work due to Panel HTML pane limitations</em></p>
    </div>
    """, height=150, sizing_mode="stretch_width")
    
    return pn.Column(
        "# 🔍 Button Debug Test",
        
        "## Direct HTML Pane (likely won't work):",
        direct_pane,
        
        "## Iframe with srcdoc (should work):",
        iframe_pane,
        
        "### Instructions:",
        "1. Test all buttons in the iframe section",
        "2. Check browser console for logs (F12)",
        "3. The ? button should toggle instructions",
        
        sizing_mode="stretch_width"
    )

# Create test
test = test_iframe_buttons()
test.servable()