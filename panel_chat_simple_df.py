import json
import re
import param
import pandas as pd
from typing import Dict, List, Any
import panel as pn

pn.extension('tabulator')

# Simple Python array format - easy to modify!
FORM_TEMPLATE = [
    {
        "id": "1.1",
        "question": "Project Title",
        "instructions": "Provide a concise, descriptive title for this data processing project."
    },
    {
        "id": "1.2.1", 
        "question": "Project Summary",
        "instructions": "Describe the overall scope and nature of data processing activities."
    },
    {
        "id": "1.2.2",
        "question": "Purpose of Processing", 
        "instructions": "Explain why this data processing is necessary. What business need does it fulfill?"
    },
    {
        "id": "2.1",
        "question": "Data Types",
        "instructions": "List all categories of personal data that will be processed."
    },
    {
        "id": "2.2",
        "question": "Legal Basis",
        "instructions": "Identify the lawful basis for processing under GDPR Article 6.",
        "options": ["Consent", "Contract", "Legal Obligation", "Vital Interests", "Public Task", "Legitimate Interests"]
    },
]

class SimpleFormState(param.Parameterized):
    """Much simpler - just watch the DataFrame directly"""
    
    form_data = param.DataFrame(doc="The entire form as a DataFrame")
    last_updated = param.String(default="", doc="Last update timestamp")
    update_count = param.Integer(default=0, doc="Number of updates")
    
    def __init__(self, form_template, **params):
        # Initialize DataFrame from template
        data = []
        for question in form_template:
            data.append({
                'ID': question["id"],
                'Question': question["question"], 
                'Instructions': question["instructions"],
                'Answer': "",
                'Rationale': "",
                'Options': str(question.get("options", [])) if question.get("options") else ""
            })
        
        initial_df = pd.DataFrame(data)
        super().__init__(form_data=initial_df, **params)
        
        # Watch the DataFrame for changes
        self.param.watch(self._on_dataframe_change, 'form_data')
        self._update_callbacks = []
    
    def _on_dataframe_change(self, event):
        """Called whenever the DataFrame changes"""
        import datetime
        self.last_updated = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.update_count += 1
        
        print(f"📊 DataFrame updated! (Update #{self.update_count})")
        
        # Notify callbacks
        for callback in self._update_callbacks:
            callback(event.old, event.new)
    
    def add_change_callback(self, callback):
        """Add a callback to be called when form state changes"""
        self._update_callbacks.append(callback)
    
    def get_form_dict(self):
        """Get form data as dictionary compatible with LLM functions"""
        form_dict = {}
        for index, row in self.form_data.iterrows():
            form_dict[row['ID']] = {
                "question": row['Question'],
                "answer": row['Answer'],
                "rationale": row['Rationale']
            }
        return form_dict
    
    def apply_edits(self, edits: List[Dict[str, Any]]):
        """Apply edits from LLM to form state"""
        df = self.form_data.copy()
        
        for edit in edits:
            qid = edit.get("id")
            mask = df['ID'] == qid
            
            if mask.any():
                if "answer" in edit:
                    df.loc[mask, 'Answer'] = edit["answer"]
                if "rationale" in edit:
                    df.loc[mask, 'Rationale'] = edit["rationale"]
        
        # This will trigger the watcher
        self.form_data = df
    
    def clear_all(self):
        """Clear all form data"""
        df = self.form_data.copy()
        df['Answer'] = ""
        df['Rationale'] = ""
        self.form_data = df

# Create simple form state
form_state = SimpleFormState(FORM_TEMPLATE)

class SimpleFormApp(param.Parameterized):
    """Super simple form app that just watches the DataFrame"""
    
    def __init__(self, **params):
        super().__init__(**params)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        
        # Create Tabulator - no automatic syncing, we'll sync only when needed
        self.tabulator = pn.widgets.Tabulator(
            form_state.form_data,  # Start with initial data
            pagination='remote',
            page_size=20,
            sizing_mode='stretch_width',
            height=400,
            show_index=False,
            configuration={
                'columns': [
                    {'field': 'ID', 'title': 'ID', 'width': 80, 'editor': False},
                    {
                        'field': 'Question', 
                        'title': 'Question', 
                        'width': 200, 
                        'editor': False,
                        'formatter': 'textarea'
                    },
                    {
                        'field': 'Answer', 
                        'title': 'Answer', 
                        'editor': 'textarea',
                        'formatter': 'textarea'
                    },
                    {
                        'field': 'Rationale', 
                        'title': 'Rationale', 
                        'editor': 'textarea', 
                        'formatter': 'textarea'
                    }
                ],
                'layout': 'fitColumns',
                'resizableColumns': True,
                'movableColumns': False,
                'selectable': True,
                'cellEdited': True
            }
        )
        
        # No automatic watching - we'll sync manually when sending chat messages
        
        # Create control buttons
        self.clear_btn = pn.widgets.Button(
            name="🗑️ Clear All", 
            button_type="light",
            margin=(5, 5)
        )
        self.clear_btn.on_click(self.clear_all_data)

    
    def clear_all_data(self, event):
        """Clear all form data"""
        form_state.clear_all()
        print("🗑️ All form data cleared")
    
    def get_current_form_data(self):
        """Get the current form data from Tabulator (sync on demand)"""
        if hasattr(self.tabulator, 'value') and self.tabulator.value is not None:
            print(f"📥 Syncing current Tabulator data ({len(self.tabulator.value)} rows)")
            return self.tabulator.value
        else:
            print("⚠️ Using form_state data (Tabulator not ready)")
            return form_state.form_data
    
    def df_to_form_dict(self, df):
        """Convert DataFrame to form dictionary"""
        form_dict = {}
        for index, row in df.iterrows():
            form_dict[row['ID']] = {
                "question": row['Question'],
                "answer": row['Answer'],
                "rationale": row['Rationale']
            }
        return form_dict
    
    def create_layout(self):
        """Create the main layout"""
        
        # Create chat interface
        chat = pn.chat.ChatInterface(
            callback=self.on_chat_message,
            show_clear=False,
            placeholder_text="Try: 'title: My Project', 'autofill example', 'show form', 'clear form'",
            sizing_mode="stretch_both",
        )
        
        # Send welcome message
        chat.send(f"**🚀 SIMPLE DATAFRAME SOLUTION**\n\n✅ **One DataFrame parameter** - No complexity!\n📊 **Direct Tabulator binding** - Automatic sync\n🔄 **Single watcher** - Clean and simple\n📝 **Template-driven** - Easy to modify\n⚡ **Real-time sync** - Just works!\n\n📋 **Current template has {len(FORM_TEMPLATE)} questions**\n\n🎮 **Try these commands:**\n• `title: My Project Name`\n• `autofill example`\n• `show form`\n• `clear form`", user="System")
        
        # Main layout
        return pn.Row(
            pn.Column(
                "# 💬 Chat Assistant",
                chat,
                sizing_mode="stretch_both"
            ),
            pn.Column(
                "# 📊 Simple DataFrame Form",
                self.clear_btn,
                self.tabulator,
                sizing_mode="stretch_both"
            ),
            min_height=700,
            sizing_mode="stretch_both"
        )
    
    def on_chat_message(self, contents, user, **kwargs):
        """Handle chat messages"""
        # Get current data from Tabulator (sync only when sending)
        current_df = self.get_current_form_data()
        current_form = self.df_to_form_dict(current_df)
        
        print(f"🔍 Chat processing with current data: {[(k, v['answer'][:20] + '...' if len(v['answer']) > 20 else v['answer']) for k, v in current_form.items()]}")
        
        raw = self.fake_llm(str(contents), current_form)
        payload = self.parse_json(raw)
        
        if not payload:
            return "Could not parse valid JSON from model output."
        
        return self.handle_json_payload(payload)
    
    def parse_json(self, text: str) -> Dict[str, Any]:
        """Parse JSON from text"""
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        return {}
    
    def handle_json_payload(self, payload: Dict[str, Any]) -> str:
        """Handle JSON payload from LLM"""
        explanation = str(payload.get("explanation of edits", "")).strip()
        edits = payload.get("edits", [])
        follow_up = str(payload.get("follow-up question", "")).strip()
        
        if isinstance(edits, list):
            # Apply edits to current Tabulator data and update both
            current_df = self.get_current_form_data().copy()
            
            for edit in edits:
                qid = edit.get("id")
                mask = current_df['ID'] == qid
                
                if mask.any():
                    if "answer" in edit:
                        current_df.loc[mask, 'Answer'] = edit["answer"]
                    if "rationale" in edit:
                        current_df.loc[mask, 'Rationale'] = edit["rationale"]
            
            # Update both Tabulator and form_state
            self.tabulator.value = current_df
            form_state.form_data = current_df
        
        reply = ""
        if explanation:
            reply += f"**Update:** {explanation}\n\n"
        if follow_up:
            reply += f"**Next:** {follow_up}"
        
        return reply or "Done."
    
    def fake_llm(self, user_msg: str, current_form: Dict[str, Dict[str, str]]) -> str:
        """Simulate LLM responses"""
        if user_msg.lower().startswith("title:"):
            val = user_msg.split(":", 1)[1].strip()
            return json.dumps({
                "explanation of edits": f"Set the project title to '{val}' using simple DataFrame approach.",
                "edits": [{"id": "1.1", "answer": val}],
                "follow-up question": "Would you like me to help with the project summary?"
            })
        
        if "autofill example" in user_msg.lower():
            return json.dumps({
                "explanation of edits": f"Filled out example data for all {len(FORM_TEMPLATE)} template questions.",
                "edits": [
                    {"id": "1.1", "answer": "AI-Powered Customer Analytics Platform"},
                    {"id": "1.2.1", "answer": "Advanced customer behavior analysis using machine learning and data processing."},
                    {"id": "1.2.2", "answer": "Enhancing customer experience through predictive analytics and personalization."},
                    {"id": "2.1", "answer": "Customer profiles, transaction history, behavioral patterns, preferences, contact information."},
                    {"id": "2.2", "answer": "Legitimate Interests"}
                ],
                "follow-up question": "Should I help you complete the rationale fields for these answers?"
            })
        
        if "show form" in user_msg.lower():
            form_summary = []
            for qid, data in current_form.items():
                status = "✅" if data["answer"] else "❌"
                form_summary.append(f"{status} **{qid}**: {data['question']}")
            form_status = f"**Simple DataFrame Form Status ({len(FORM_TEMPLATE)} questions):**\n\n" + "\n".join(form_summary)
            return json.dumps({
                "explanation of edits": form_status,
                "edits": [],
                "follow-up question": "Would you like me to help fill out any incomplete fields?"
            })
        
        if "clear form" in user_msg.lower():
            return json.dumps({
                "explanation of edits": f"Cleared all data for {len(FORM_TEMPLATE)} template questions.",
                "edits": [],
                "follow-up question": "Ready to start fresh! What would you like to fill out first?"
            })
        
        return json.dumps({
            "explanation of edits": "",
            "edits": [],
            "follow-up question": "Try: 'title: My Project', 'autofill example', 'show form', or 'clear form'."
        })

# Create and serve the application
app = SimpleFormApp()
layout = app.create_layout()

layout.servable()