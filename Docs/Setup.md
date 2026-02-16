# Setup Guide

## Prerequisites

- Python 3.9 or higher
- An Eventbrite account with an API key

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/NurjahanJ/eventbrite-extractor.git
cd eventbrite-extractor
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

All 62 tests should pass.

---

## Docker Setup (Alternative)

If you prefer not to install Python locally, you can run everything inside Docker.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed and running
- An Eventbrite API key (see above)

### 1. Clone and Configure

```bash
git clone https://github.com/NurjahanJ/eventbrite-extractor.git
cd eventbrite-extractor
cp .env.example .env
# Edit .env and add your Eventbrite Private token
```

### 2. Build the Image

```bash
docker build -t eventbrite-extractor .
```

### 3. Run the Extractor

```bash
docker run --env-file .env -v "$(pwd)/output:/app/output" eventbrite-extractor
```

- `--env-file .env` passes your API key into the container
- `-v "$(pwd)/output:/app/output"` mounts your local `output/` directory so extracted files persist after the container exits

> **Windows (PowerShell):** Replace `$(pwd)` with `${PWD}`:
> ```powershell
> docker run --env-file .env -v "${PWD}/output:/app/output" eventbrite-extractor
> ```

### 4. Run with Custom Arguments

```bash
docker run --env-file .env -v "$(pwd)/output:/app/output" eventbrite-extractor \
  python -m eventbrite_extractor.extract_events -q "machine learning" --pages 5 --free-first
```

### 5. Run Tests in Docker

```bash
docker build --target test -t eventbrite-extractor-test .
docker run eventbrite-extractor-test
```

This builds the test stage of the Dockerfile and runs the full test suite inside the container.
