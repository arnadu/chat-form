import panel as pn

pn.extension()

# Very simple JavaScript test
simple_test = """
<div style="padding: 20px; font-family: Arial, sans-serif;">
    <h3>Simple JavaScript Test</h3>
    
    <button onclick="alert('Hello from onclick!')">Test Alert</button>
    <br><br>
    
    <button onclick="changeColor()">Change Color</button>
    <div id="test-div" style="padding: 10px; background: lightblue;">Click button to change my color</div>
    <br><br>
    
    <button onclick="addText()">Add Text</button>
    <div id="text-container">Original text</div>
    
    <script>
        console.log('JavaScript loaded in HTML pane');
        
        function changeColor() {
            const div = document.getElementById('test-div');
            div.style.background = div.style.background === 'lightcoral' ? 'lightblue' : 'lightcoral';
            div.innerHTML = 'Color changed!';
        }
        
        function addText() {
            const container = document.getElementById('text-container');
            container.innerHTML += '<br>Text added at ' + new Date().toLocaleTimeString();
        }
    </script>
</div>
"""

# Test the simple approach
pane = pn.pane.HTML(simple_test, height=400, sizing_mode="stretch_width")

# Create status indicator
status = pn.pane.Markdown("**Status:** Testing JavaScript in Panel HTML pane...")

layout = pn.Column(
    "# 🔬 Simple JavaScript Test",
    status,
    pane,
    sizing_mode="stretch_width"
)

layout.servable()