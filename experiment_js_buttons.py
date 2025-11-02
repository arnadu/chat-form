import panel as pn
import html

pn.extension()

# Simple button experiment - let's try different approaches
def experiment_simple_button():
    """Test different ways to make JavaScript work in Panel"""
    
    # Approach 1: Direct HTML with onclick
    html1 = """
    <div>
        <h3>Approach 1: Direct onclick</h3>
        <button onclick="alert('Direct onclick works!')">Test Direct</button>
    </div>
    """
    
    # Approach 2: Script tag with function
    html2 = """
    <div>
        <h3>Approach 2: Script tag</h3>
        <button id="btn2" onclick="testFunction()">Test Script</button>
        <script>
            function testFunction() {
                alert('Script function works!');
            }
        </script>
    </div>
    """
    
    # Approach 3: addEventListener in script
    html3 = """
    <div>
        <h3>Approach 3: addEventListener</h3>
        <button id="btn3">Test EventListener</button>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const btn = document.getElementById('btn3');
                if (btn) {
                    btn.addEventListener('click', function() {
                        alert('EventListener works!');
                    });
                }
            });
        </script>
    </div>
    """
    
    # Approach 4: Immediate script execution
    html4 = """
    <div>
        <h3>Approach 4: Immediate execution</h3>
        <button id="btn4">Test Immediate</button>
        <div id="output4">Click button above</div>
        <script>
            (function() {
                console.log('Immediate script executing');
                setTimeout(function() {
                    const btn = document.getElementById('btn4');
                    const output = document.getElementById('output4');
                    if (btn && output) {
                        btn.onclick = function() {
                            output.innerHTML = 'Button clicked at ' + new Date().toLocaleTimeString();
                            output.style.color = 'green';
                        };
                    }
                }, 100);
            })();
        </script>
    </div>
    """
    
    # Approach 5: Using Panel's recommended iframe
    complete_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>JavaScript Test</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            button {{ padding: 10px; margin: 5px; background: #007acc; color: white; border: none; border-radius: 4px; cursor: pointer; }}
            button:hover {{ background: #005299; }}
            .test-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h2>JavaScript Button Tests</h2>
        
        <div class="test-section">
            <h3>Test 1: Simple onclick</h3>
            <button onclick="alert('Iframe onclick works!')">Test Alert</button>
        </div>
        
        <div class="test-section">
            <h3>Test 2: DOM manipulation</h3>
            <button onclick="changeText()">Change Text</button>
            <div id="text-target">Original Text</div>
        </div>
        
        <div class="test-section">
            <h3>Test 3: Interactive counter</h3>
            <button onclick="increment()">Count: <span id="counter">0</span></button>
        </div>
        
        <script>
            let count = 0;
            
            function changeText() {{
                document.getElementById('text-target').innerHTML = 'Text changed at ' + new Date().toLocaleTimeString();
                document.getElementById('text-target').style.color = 'blue';
            }}
            
            function increment() {{
                count++;
                document.getElementById('counter').textContent = count;
            }}
            
            console.log('Iframe JavaScript loaded successfully');
        </script>
    </body>
    </html>
    """
    
    # Create HTML panes for each approach
    pane1 = pn.pane.HTML(html1, height=150, sizing_mode="stretch_width")
    pane2 = pn.pane.HTML(html2, height=150, sizing_mode="stretch_width")  
    pane3 = pn.pane.HTML(html3, height=150, sizing_mode="stretch_width")
    pane4 = pn.pane.HTML(html4, height=200, sizing_mode="stretch_width")
    
    # Create iframe approach
    escaped_html = html.escape(complete_html)
    iframe_html = f'<iframe srcdoc="{escaped_html}" style="width:100%; height:500px;" frameborder="0"></iframe>'
    pane5 = pn.pane.HTML(iframe_html, height=550, sizing_mode="stretch_width")
    
    return pn.Column(
        "# 🧪 JavaScript Button Experiments",
        "## Testing different approaches to make JavaScript work in Panel HTML panes",
        
        pane1,
        pane2, 
        pane3,
        pane4,
        
        "## Approach 5: Iframe with srcdoc (Panel's recommended)",
        pane5,
        
        sizing_mode="stretch_width"
    )

# Create the experiment
experiment = experiment_simple_button()

# Test console output
def test_console():
    """Test JavaScript console integration"""
    js_test = """
    <div>
        <h3>Console Test</h3>
        <button onclick="consoleTest()">Test Console</button>
        <div id="console-output"></div>
        <script>
            function consoleTest() {
                console.log('Console test executed');
                console.warn('This is a warning');
                console.error('This is an error test');
                
                // Try to capture console output
                const output = document.getElementById('console-output');
                output.innerHTML += '<div>Console test executed - check browser console</div>';
            }
        </script>
    </div>
    """
    return pn.pane.HTML(js_test, height=150)

console_test = test_console()

# Create layout with both experiments
layout = pn.Column(
    experiment,
    "## Console Integration Test",
    console_test,
    sizing_mode="stretch_width"
)

layout.servable()