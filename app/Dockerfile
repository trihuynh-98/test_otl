FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy app and requirements
COPY app.py requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
