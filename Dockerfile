FROM python:3.11-slim

# Install system deps and Rust, then install Python packages in same RUN block
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    curl https://sh.rustup.rs -sSf | sh -s -- -y && \
    export PATH="$HOME/.cargo/bin:$PATH" && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Set working directory
WORKDIR /app

# Copy app files after dependencies are installed
COPY . .

# Reinstall just in case any app-local changes
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]