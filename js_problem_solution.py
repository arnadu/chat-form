import panel as pn
import html

pn.extension()

# Demonstration of JavaScript issues and solutions in Panel
def create_js_comparison():
    """Show the exact problem and multiple solutions"""
    
    # BROKEN APPROACH (like your original error)
    broken_html = """
    <div style="padding: 20px; font-family: Arial, sans-serif; border: 2px solid red;">
        <h3 style="color: red;">❌ BROKEN: Using event.target (causes error)</h3>
        
        <button onclick="brokenToggle('test1')" 
                style="background: #007acc; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer;">
            Click me (will error)
        </button>
        
        <div id="broken_test1" style="display: none; background: #ffe6e6; padding: 10px; margin: 10px 0;">
            This won't work because event.target is undefined in Panel HTML panes
        </div>
        
        <script>
            // This will throw: Cannot read properties of undefined (reading 'target')
            function brokenToggle(id) {
                console.error('BROKEN: Trying to use event.target...');
                const div = document.getElementById('broken_' + id);
                const button = event.target; // ❌ THIS FAILS - event is undefined
                
                if (div.style.display === 'none') {
                    div.style.display = 'block';
                    button.textContent = 'Hide';
                } else {
                    div.style.display = 'none'; 
                    button.textContent = 'Show';
                }
            }
        </script>
    </div>
    """
    
    # FIXED APPROACH 1: Pass 'this' explicitly
    fixed1_html = """
    <div style="padding: 20px; font-family: Arial, sans-serif; border: 2px solid green;">
        <h3 style="color: green;">✅ FIXED 1: Pass 'this' explicitly</h3>
        
        <button onclick="fixedToggle1('test2', this)" 
                style="background: #007acc; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer;">
            ? Show Instructions
        </button>
        
        <div id="fixed_test2" style="display: none; background: #e6ffe6; padding: 10px; margin: 10px 0;">
            <strong>Instructions:</strong> This works because we pass 'this' (the button element) explicitly to the function.
        </div>
        
        <script>
            function fixedToggle1(id, buttonElement) {
                console.log('FIXED 1: Using passed button element');
                const div = document.getElementById('fixed_' + id);
                
                if (div.style.display === 'none' || div.style.display === '') {
                    div.style.display = 'block';
                    buttonElement.textContent = '✕ Hide Instructions';
                    buttonElement.style.background = '#666';
                } else {
                    div.style.display = 'none'; 
                    buttonElement.textContent = '? Show Instructions';
                    buttonElement.style.background = '#007acc';
                }
            }
        </script>
    </div>
    """
    
    # FIXED APPROACH 2: Use getElementById to find button
    fixed2_html = """
    <div style="padding: 20px; font-family: Arial, sans-serif; border: 2px solid blue;">
        <h3 style="color: blue;">✅ FIXED 2: Use getElementById for button</h3>
        
        <button id="btn_test3" onclick="fixedToggle2('test3')" 
                style="background: #007acc; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer;">
            ? Show Instructions
        </button>
        
        <div id="fixed2_test3" style="display: none; background: #e6f3ff; padding: 10px; margin: 10px 0;">
            <strong>Instructions:</strong> This works by finding the button using getElementById instead of relying on event.target.
        </div>
        
        <script>
            function fixedToggle2(id) {
                console.log('FIXED 2: Using getElementById to find button');
                const div = document.getElementById('fixed2_' + id);
                const button = document.getElementById('btn_' + id);
                
                if (div.style.display === 'none' || div.style.display === '') {
                    div.style.display = 'block';
                    button.textContent = '✕ Hide Instructions';
                    button.style.background = '#666';
                } else {
                    div.style.display = 'none'; 
                    button.textContent = '? Show Instructions';
                    button.style.background = '#007acc';
                }
            }
        </script>
    </div>
    """
    
    # Create iframe version (which works perfectly)
    iframe_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .container { border: 2px solid purple; padding: 20px; }
            button { background: #007acc; color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; }
            .instructions { display: none; background: #f3e6ff; padding: 10px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h3 style="color: purple;">🚀 IFRAME: Works perfectly (Panel's recommended)</h3>
            
            <button onclick="iframeToggle('test4')">? Show Instructions</button>
            
            <div id="iframe_test4" class="instructions">
                <strong>Instructions:</strong> In iframe context, event.target works perfectly because it's a complete HTML document with proper JavaScript isolation.
            </div>
            
            <script>
                function iframeToggle(id) {
                    console.log('IFRAME: Using event.target (works perfectly here)');
                    const div = document.getElementById('iframe_' + id);
                    const button = event.target; // ✅ This works in iframe!
                    
                    if (div.style.display === 'none' || div.style.display === '') {
                        div.style.display = 'block';
                        button.textContent = '✕ Hide Instructions';
                        button.style.background = '#666';
                    } else {
                        div.style.display = 'none'; 
                        button.textContent = '? Show Instructions';
                        button.style.background = '#007acc';
                    }
                }
            </script>
        </div>
    </body>
    </html>
    """
    
    # Create panes
    pane_broken = pn.pane.HTML(broken_html, height=200, sizing_mode="stretch_width")
    pane_fixed1 = pn.pane.HTML(fixed1_html, height=200, sizing_mode="stretch_width")
    pane_fixed2 = pn.pane.HTML(fixed2_html, height=200, sizing_mode="stretch_width")
    
    # Iframe approach
    escaped_html = html.escape(iframe_html)
    iframe_content = f'<iframe srcdoc="{escaped_html}" style="width:100%; height:300px;" frameborder="0"></iframe>'
    pane_iframe = pn.pane.HTML(iframe_content, height=350, sizing_mode="stretch_width")
    
    return pn.Column(
        "# 🔧 JavaScript in Panel: Problem & Solutions",
        
        "## The Problem You Found:",
        "**Error:** `Cannot read properties of undefined (reading 'target')`",
        "**Cause:** In Panel HTML panes, the `event` object is not available in onclick handlers",
        
        pane_broken,
        pane_fixed1, 
        pane_fixed2,
        pane_iframe,
        
        "## Summary:",
        "- ❌ **Don't use** `event.target` in Panel HTML panes",
        "- ✅ **Do pass** `this` explicitly: `onclick=\"func('id', this)\"`", 
        "- ✅ **Do use** `getElementById` to find elements",
        "- 🚀 **Best approach:** Use iframe with srcdoc for complex JavaScript",
        
        sizing_mode="stretch_width"
    )

# Create the comparison
comparison = create_js_comparison()
comparison.servable()