# ---- Base stage ----
FROM python:3.13-slim AS base

WORKDIR /app

# Install only runtime dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and install the package
COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir .

# Create output directory
RUN mkdir -p /app/output

# ---- Test stage (used for CI / local verification) ----
FROM base AS test

RUN pip install --no-cache-dir pytest
COPY tests/ tests/

CMD ["pytest", "tests/", "-v"]

# ---- Production stage (default) ----
FROM base AS production

CMD ["python", "-m", "eventbrite_extractor.extract_events"]
