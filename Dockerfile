# Use the ultra-fast uv Python image
FROM ghcr.io/astral-sh/uv:python3.9-bookworm-slim

WORKDIR /app

# Copy your uv dependency files
COPY pyproject.toml uv.lock ./

# Install the dependencies exactly as they are on your Mac
RUN uv sync --frozen

# Copy your application code
COPY main.py .

# Expose the port
EXPOSE 8000

# Command to run the FastAPI server
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
