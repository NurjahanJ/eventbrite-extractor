# Setup Guide

## Prerequisites

- Python 3.9 or higher
- An Eventbrite account with an API key

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/NurjahanJ/newsletter.git
cd newsletter
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it:

- **Windows:** `.venv\Scripts\activate`
- **Linux/macOS:** `source .venv/bin/activate`

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -e ".[dev]"
```

## API Key Configuration

This package requires an Eventbrite **Private token** to access the API.

### Get Your Token

1. Go to https://www.eventbrite.com/platform/api
2. Sign in or create a free Eventbrite account
3. Create an app under "API Keys"
4. Copy the **Private token** value

### Add It to the Project

```bash
cp .env.example .env
```

Open `.env` and replace the placeholder with your token:

```
EVENTBRITE_API_KEY=your_private_token_here
```

> **Important:** The `.env` file is gitignored and will never be committed. Do not share your token publicly.

## Verify Installation

Run the test suite to confirm everything is working:

```bash
pytest tests/ -v
```

All tests should pass.
