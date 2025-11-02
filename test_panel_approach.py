import panel as pn

pn.extension()

# Let's try using Panel's JavaScript hooks differently
# Instead of onclick in HTML, let's use Panel's JS execution

class InteractiveForm(pn.viewable.Viewer):
    
    def __init__(self, **params):
        super().__init__(**params)
        
        # State to track which instructions are visible
        self.instruction_states = {"q1": False, "q2": False}
        
        # Create the HTML content
        self.html_content = self._generate_html()
        self.html_pane = pn.pane.HTML(self.html_content, sizing_mode="stretch_width", height=400)
        
        # Add some buttons using Panel widgets to test
        self.toggle_q1_btn = pn.widgets.Button(name="Toggle Q1 Help", button_type="primary")
        self.toggle_q2_btn = pn.widgets.Button(name="Toggle Q2 Help", button_type="primary")
        
        # Bind button clicks
        self.toggle_q1_btn.on_click(lambda event: self.toggle_instructions("q1"))
        self.toggle_q2_btn.on_click(lambda event: self.toggle_instructions("q2"))
    
    def _generate_html(self):
        return f"""
        <div style="font-family: Arial, sans-serif;">
            <h3>Questions with Help</h3>
            
            <div style="margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
                <strong>Question 1: What is your name?</strong>
                <div id="instructions_q1" style="display: {'block' if self.instruction_states['q1'] else 'none'}; 
                     background: #e7f3ff; padding: 8px; margin-top: 8px; border-radius: 4px; border-left: 3px solid #007acc;">
                    This is help text for question 1. Enter your full legal name as it appears on official documents.
                </div>
            </div>
            
            <div style="margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
                <strong>Question 2: What is your email?</strong>
                <div id="instructions_q2" style="display: {'block' if self.instruction_states['q2'] else 'none'}; 
                     background: #e7f3ff; padding: 8px; margin-top: 8px; border-radius: 4px; border-left: 3px solid #007acc;">
                    This is help text for question 2. Enter a valid email address that you check regularly.
                </div>
            </div>
        </div>
        """
    
    def toggle_instructions(self, question_id):
        # Toggle the state
        self.instruction_states[question_id] = not self.instruction_states[question_id]
        
        # Regenerate HTML with new state
        self.html_content = self._generate_html()
        self.html_pane.object = self.html_content
        
        print(f"Toggled {question_id}: {self.instruction_states[question_id]}")
    
    def __panel__(self):
        return pn.Column(
            "# Interactive Form Test",
            "Using Panel widgets to control HTML content:",
            pn.Row(self.toggle_q1_btn, self.toggle_q2_btn),
            self.html_pane,
            sizing_mode="stretch_width"
        )

# Create and serve the app
form = InteractiveForm()
form.servable()