FROM python:3.11-slim

# Install system packages and Rust for Pydantic 2.x
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    curl https://sh.rustup.rs -sSf | sh -s -- -y && \
    echo 'export PATH="/root/.cargo/bin:$PATH"' >> ~/.bashrc

ENV PATH="/root/.cargo/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy dependencies and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY . .

# Expose port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]