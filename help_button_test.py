import panel as pn
import html

pn.extension()

# Test specifically for ? button functionality
def create_help_button_test():
    """Test help button functionality with different approaches"""
    
    # Approach 1: Direct HTML with ? button
    html_direct = """
    <div style="padding: 20px; font-family: Arial, sans-serif;">
        <h3>Direct HTML ? Button Test</h3>
        
        <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0;">
            <strong>Question 1.1: Project Title</strong>
            <button onclick="toggleInstructions('1_1', this)" 
                    style="margin-left: 10px; background: #007acc; color: white; border: none; border-radius: 50%; width: 24px; height: 24px; cursor: pointer;">?</button>
            
            <div id="instructions_1_1" style="display: none; background: #e7f3ff; padding: 10px; margin: 5px 0; border-left: 3px solid #007acc;">
                <strong>Instructions:</strong> Provide a concise, descriptive title for this data processing project.
            </div>
            
            <input type="text" placeholder="Enter project title..." style="width: 100%; padding: 8px; margin: 5px 0;">
        </div>
        
        <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0;">
            <strong>Question 1.2: Project Summary</strong>
            <button onclick="toggleInstructions('1_2', this)" 
                    style="margin-left: 10px; background: #007acc; color: white; border: none; border-radius: 50%; width: 24px; height: 24px; cursor: pointer;">?</button>
            
            <div id="instructions_1_2" style="display: none; background: #e7f3ff; padding: 10px; margin: 5px 0; border-left: 3px solid #007acc;">
                <strong>Instructions:</strong> Describe the overall scope and nature of data processing activities.
            </div>
            
            <textarea placeholder="Enter project summary..." style="width: 100%; padding: 8px; margin: 5px 0; height: 60px;"></textarea>
        </div>
        
        <script>
            console.log('? Button JavaScript loaded (FIXED VERSION)');
            
            // FIXED: Pass button element explicitly instead of relying on event.target
            function toggleInstructions(id, buttonElement) {
                console.log('Toggling instructions for:', id);
                const instructions = document.getElementById('instructions_' + id);
                
                if (!instructions) {
                    console.error('Instructions element not found for id:', id);
                    return;
                }
                
                if (!buttonElement) {
                    console.error('Button element not provided');
                    return;
                }
                
                if (instructions.style.display === 'none' || instructions.style.display === '') {
                    instructions.style.display = 'block';
                    buttonElement.textContent = '✕';
                    buttonElement.style.background = '#666';
                    console.log('Showing instructions for:', id);
                } else {
                    instructions.style.display = 'none';
                    buttonElement.textContent = '?';
                    buttonElement.style.background = '#007acc';
                    console.log('Hiding instructions for:', id);
                }
            }
        </script>
    </div>
    """
    
    # Approach 2: Using iframe with complete HTML
    complete_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .question-row { border: 1px solid #ddd; padding: 15px; margin: 10px 0; }
            .help-btn { 
                margin-left: 10px; 
                background: #007acc; 
                color: white; 
                border: none; 
                border-radius: 50%; 
                width: 24px; 
                height: 24px; 
                cursor: pointer; 
            }
            .help-btn:hover { background: #005299; }
            .instructions { 
                display: none; 
                background: #e7f3ff; 
                padding: 10px; 
                margin: 5px 0; 
                border-left: 3px solid #007acc; 
            }
            input, textarea { 
                width: 100%; 
                padding: 8px; 
                margin: 5px 0; 
                border: 1px solid #ddd; 
                border-radius: 4px; 
            }
        </style>
    </head>
    <body>
        <h3>Iframe ? Button Test</h3>
        
        <div class="question-row">
            <strong>Question 1.1: Project Title</strong>
            <button class="help-btn" onclick="toggleInstructions('iframe_1_1')">?</button>
            
            <div id="instructions_iframe_1_1" class="instructions">
                <strong>Instructions:</strong> Provide a concise, descriptive title for this data processing project.
            </div>
            
            <input type="text" placeholder="Enter project title...">
        </div>
        
        <div class="question-row">
            <strong>Question 1.2: Project Summary</strong>
            <button class="help-btn" onclick="toggleInstructions('iframe_1_2')">?</button>
            
            <div id="instructions_iframe_1_2" class="instructions">
                <strong>Instructions:</strong> Describe the overall scope and nature of data processing activities.
            </div>
            
            <textarea placeholder="Enter project summary..." rows="3"></textarea>
        </div>
        
        <script>
            console.log('Iframe ? Button JavaScript loaded');
            
            function toggleInstructions(id) {
                console.log('Iframe toggling instructions for:', id);
                const instructions = document.getElementById('instructions_' + id);
                const button = event.target;
                
                if (instructions.style.display === 'none' || instructions.style.display === '') {
                    instructions.style.display = 'block';
                    button.textContent = '✕';
                    button.style.background = '#666';
                    console.log('Showing instructions for:', id);
                } else {
                    instructions.style.display = 'none';
                    button.textContent = '?';
                    button.style.background = '#007acc';
                    console.log('Hiding instructions for:', id);
                }
            }
        </script>
    </body>
    </html>
    """
    
    # Create panes
    pane_direct = pn.pane.HTML(html_direct, height=400, sizing_mode="stretch_width")
    
    # Iframe approach
    escaped_html = html.escape(complete_html)
    iframe_html = f'<iframe srcdoc="{escaped_html}" style="width:100%; height:400px;" frameborder="0"></iframe>'
    pane_iframe = pn.pane.HTML(iframe_html, height=450, sizing_mode="stretch_width")
    
    return pn.Column(
        "# 🔘 ? Button Functionality Tests",
        
        "## Approach 1: Direct HTML in Panel pane",
        pane_direct,
        
        "## Approach 2: Iframe with srcdoc",
        pane_iframe,
        
        "## Test Instructions:",
        "1. Click the ? buttons to toggle instructions",
        "2. Check browser console for JavaScript logs", 
        "3. See which approach works better",
        
        sizing_mode="stretch_width"
    )

# Create the test
test = create_help_button_test()
test.servable()