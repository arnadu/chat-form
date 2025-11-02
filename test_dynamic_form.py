import panel as pn
import html
import json

pn.extension()

# Test if the exact pattern from working simple form works with dynamic content
def create_test_dynamic_form():
    """Create a form that matches the working pattern but with dynamic content"""
    
    # Test data
    questions = [
        {"id": "1_1", "question": "Project Title", "instructions": "Enter a clear project title"},
        {"id": "1_2", "question": "Project Summary", "instructions": "Describe the project scope"}
    ]
    
    # Generate table rows dynamically (like the main app)
    table_rows = ""
    for q in questions:
        table_rows += f'''
            <tr>
                <td><strong>{q["id"]}</strong></td>
                <td>
                    {q["question"]}
                    <button class="help-btn" onclick="toggle('{q["id"]}')" title="Show/hide instructions">?</button>
                    <div id="inst_{q["id"]}" class="instructions">
                        {q["instructions"]}
                    </div>
                </td>
                <td><input type="text" placeholder="Enter answer..."></td>
            </tr>
        '''
    
    # Generate JavaScript with proper escaping
    js_questions = json.dumps([q["id"] for q in questions])
    
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial; padding: 20px; background: #f5f5f5; }}
        .container {{ background: white; padding: 20px; border-radius: 8px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ padding: 12px; border: 1px solid #ddd; text-align: left; }}
        th {{ background: #007acc; color: white; }}
        input {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
        .help-btn {{ 
            background: #007acc; color: white; border: none; border-radius: 50%; 
            width: 24px; height: 24px; cursor: pointer; margin-left: 8px; 
        }}
        .instructions {{ 
            display: none; background: #e7f3ff; padding: 8px; margin: 4px 0; 
            border-left: 3px solid #007acc; 
        }}
        .show {{ display: block; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 Dynamic Form Test</h1>
        
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Question</th>
                    <th>Answer</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>
    
    <script>
        console.log('✅ Dynamic form JavaScript loaded');
        
        function toggle(id) {{
            console.log('🔘 Toggle called for:', id);
            
            const inst = document.getElementById('inst_' + id);
            const btn = event.target;
            
            if (inst && btn) {{
                if (inst.classList.contains('show')) {{
                    inst.classList.remove('show');
                    btn.textContent = '?';
                    btn.style.background = '#007acc';
                    console.log('✅ Hidden instructions for:', id);
                }} else {{
                    inst.classList.add('show');
                    btn.textContent = '✕';
                    btn.style.background = '#666';
                    console.log('✅ Shown instructions for:', id);
                }}
            }} else {{
                console.error('❌ Element not found - inst:', !!inst, 'btn:', !!btn);
            }}
        }}
        
        // Test restoration with dynamic list
        function restoreStates() {{
            const questions = {js_questions};
            console.log('Questions for restoration:', questions);
            questions.forEach(qid => {{
                console.log('Checking question:', qid);
            }});
        }}
        
        // Initialize
        document.addEventListener('DOMContentLoaded', restoreStates);
    </script>
</body>
</html>'''
    
    # Create iframe
    escaped = html.escape(html_content)
    iframe_html = f'<iframe srcdoc="{escaped}" style="width:100%; height:400px; border:1px solid #ccc;" frameborder="0"></iframe>'
    
    return pn.pane.HTML(iframe_html, height=450, sizing_mode="stretch_width")

# Create test
dynamic_form = create_test_dynamic_form()

layout = pn.Column(
    "# 🧪 Dynamic Form Test (Like Main App)",
    "This tests the same pattern as the main app but simplified",
    dynamic_form,
    sizing_mode="stretch_width"
)

layout.servable()