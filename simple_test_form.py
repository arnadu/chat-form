import panel as pn
import html

pn.extension()

def create_simple_working_form():
    """Create the simplest possible working form with ? buttons"""
    
    # Super simple HTML - just two questions
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 20px; border-radius: 8px; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
        th { background: #007acc; color: white; }
        input, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .help-btn { 
            background: #007acc; color: white; border: none; border-radius: 50%; 
            width: 24px; height: 24px; cursor: pointer; margin-left: 8px; 
        }
        .instructions { 
            display: none; background: #e7f3ff; padding: 8px; margin: 4px 0; 
            border-left: 3px solid #007acc; 
        }
        .show { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ Simple Form Test</h1>
        
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Question</th>
                    <th>Answer</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>1.1</strong></td>
                    <td>
                        Project Title
                        <button class="help-btn" onclick="toggle('1_1')">?</button>
                        <div id="inst_1_1" class="instructions">
                            Provide a concise, descriptive title for this project.
                        </div>
                    </td>
                    <td><input type="text" placeholder="Enter title..."></td>
                </tr>
                <tr>
                    <td><strong>1.2</strong></td>
                    <td>
                        Project Summary
                        <button class="help-btn" onclick="toggle('1_2')">?</button>
                        <div id="inst_1_2" class="instructions">
                            Describe the overall scope and nature of activities.
                        </div>
                    </td>
                    <td><textarea placeholder="Enter summary..." rows="2"></textarea></td>
                </tr>
            </tbody>
        </table>
    </div>
    
    <script>
        console.log('✅ Simple form JavaScript loaded');
        
        function toggle(id) {
            console.log('🔘 Toggle called for:', id);
            
            const inst = document.getElementById('inst_' + id);
            const btn = event.target;
            
            console.log('Element found:', !!inst, 'Button found:', !!btn);
            
            if (inst && btn) {
                if (inst.classList.contains('show')) {
                    inst.classList.remove('show');
                    btn.textContent = '?';
                    btn.style.background = '#007acc';
                    console.log('✅ Hidden instructions for:', id);
                } else {
                    inst.classList.add('show');
                    btn.textContent = '✕';
                    btn.style.background = '#666';
                    console.log('✅ Shown instructions for:', id);
                }
            } else {
                console.error('❌ Element not found - inst:', !!inst, 'btn:', !!btn);
            }
        }
    </script>
</body>
</html>
    """
    
    # Create iframe
    escaped = html.escape(html_content)
    iframe_html = f'<iframe srcdoc="{escaped}" style="width:100%; height:400px; border:1px solid #ccc;" frameborder="0"></iframe>'
    
    return pn.pane.HTML(iframe_html, height=450, sizing_mode="stretch_width")

# Create simple test
simple_form = create_simple_working_form()

layout = pn.Column(
    "# 🧪 Super Simple Form Test",
    "Click the ? buttons to test functionality",
    simple_form,
    sizing_mode="stretch_width"
)

layout.servable()