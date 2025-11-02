import panel as pn

pn.extension()

# Simple HTML with ? button to test functionality
simple_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .help-btn {
            background: #007acc;
            color: white;
            border: none;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            cursor: pointer;
            font-size: 12px;
            margin-left: 8px;
        }
        .instructions {
            display: none;
            background: #e7f3ff;
            padding: 8px;
            margin-top: 4px;
            border-radius: 4px;
            border-left: 3px solid #007acc;
        }
        .instructions.show {
            display: block;
        }
    </style>
</head>
<body>
    <h2>Simple ? Button Test</h2>
    
    <div>
        Question 1: What is your name?
        <button class="help-btn" onclick="toggleInstructions('q1')">?</button>
        <div id="instructions_q1" class="instructions">
            This is help text for question 1. Enter your full legal name.
        </div>
    </div>
    
    <br><br>
    
    <div>
        Question 2: What is your email?
        <button class="help-btn" onclick="toggleInstructions('q2')">?</button>
        <div id="instructions_q2" class="instructions">
            This is help text for question 2. Enter a valid email address.
        </div>
    </div>

    <script>
        function toggleInstructions(questionId) {
            console.log('Toggle called for:', questionId);
            
            const instructions = document.getElementById('instructions_' + questionId);
            const button = event.target;
            
            console.log('Instructions element:', instructions);
            console.log('Button element:', button);
            
            if (!instructions) {
                console.error('Instructions element not found for:', questionId);
                return;
            }
            
            if (instructions.classList.contains('show')) {
                instructions.classList.remove('show');
                button.textContent = '?';
                console.log('Hiding instructions for:', questionId);
            } else {
                instructions.classList.add('show');
                button.textContent = '✕';
                console.log('Showing instructions for:', questionId);
            }
        }
        
        console.log('JavaScript loaded successfully');
    </script>
</body>
</html>
"""

# Create simple test app
html_pane = pn.pane.HTML(simple_html, sizing_mode="stretch_width", height=400)

layout = pn.Column(
    "# Simple ? Button Test",
    html_pane,
    sizing_mode="stretch_width"
)

layout.servable()