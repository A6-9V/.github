FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY bridge/ /app/bridge/

# Expose port (Cloud Run will override this)
EXPOSE 8080

# Command to run the application
CMD ["python", "bridge/server.py"]
