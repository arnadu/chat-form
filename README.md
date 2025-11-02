# Panel Chat Applications

This repository contains Panel-based chat applications for interactive document and form editing.

## Files

- `panel_chat.py` - Chat interface with live Markdown document editing
- `panel_chat_2.py` - Chat interface with form-based editing using ReactiveHTML
- `panel_chat_simple.py` - Simplified chat interface with native Panel widgets
- `basic_test.py` - Basic Panel chat functionality test
- `debug_panel.py` - Simple debug Panel application

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
.\venv\Scripts\Activate.ps1
```

3. Install dependencies:
```bash
pip install panel watchfiles
```

## Running the Applications

Run any of the applications with Panel serve:

```bash
# Basic markdown editor chat
panel serve panel_chat.py --show --autoreload

# Form-based chat (ReactiveHTML version)  
panel serve panel_chat_2.py --show --autoreload --port 5007

# Simple form-based chat (native widgets)
panel serve panel_chat_simple.py --show --autoreload --port 5009

# Basic chat test
panel serve basic_test.py --show --autoreload --port 5010
```

## Features

- Interactive chat interfaces
- Live document/form updates
- JSON-based edit protocols
- Document append/replace operations
- Form field management with string IDs

## Requirements

- Panel >= 1.4
- Python 3.8+
- watchfiles (for auto-reload)