# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copy the current directory contents into the container at /app
COPY . /app

# Make port 8080 available to the world outside this container
# EXPOSE 8080

# Run migracion.py when the container launches
CMD ["python", "migracion.py", "--mysql-table=productos"]