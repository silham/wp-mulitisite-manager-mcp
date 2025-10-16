# Dockerfile for WordPress MCP Server
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install uv (fast Python package installer)
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml ./
COPY main.py ./
COPY server_http.py ./
COPY .env .env.example* ./

# Install dependencies using uv
RUN uv pip install --system -r pyproject.toml

# Expose port for MCP server HTTP/SSE transport
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the HTTP/SSE MCP server
CMD ["python", "server_http.py"]
