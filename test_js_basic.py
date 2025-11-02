import panel as pn

pn.extension()

# Very basic JavaScript test
basic_test_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        .test-btn {
            background: #007acc;
            color: white;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            margin: 10px;
        }
        .hidden { display: none; }
        .visible { display: block; }
    </style>
</head>
<body>
    <h2>Basic JavaScript Test in Panel</h2>
    
    <button class="test-btn" onclick="testClick()">Click Me!</button>
    
    <div id="message" class="hidden">JavaScript is working! 🎉</div>
    
    <p><strong>Instructions:</strong> Click the button above. If you see a success message, JavaScript works in Panel HTML panes.</p>

    <script>
        console.log('Script is loading...');
        
        function testClick() {
            console.log('Button clicked!');
            const message = document.getElementById('message');
            if (message.classList.contains('hidden')) {
                message.classList.remove('hidden');
                message.classList.add('visible');
                console.log('Message shown');
            } else {
                message.classList.remove('visible');
                message.classList.add('hidden');
                console.log('Message hidden');
            }
        }
        
        console.log('Script loaded successfully');
        
        // Test if we can modify DOM on load
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM loaded');
        });
    </script>
</body>
</html>
"""

html_pane = pn.pane.HTML(basic_test_html, sizing_mode="stretch_width", height=300)

layout = pn.Column(
    "# JavaScript Test in Panel",
    "If the button below works, then JavaScript is functional in Panel HTML panes.",
    html_pane,
    sizing_mode="stretch_width"
)

layout.servable()