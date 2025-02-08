# Use the official Python image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app/graduation_projects_management

# Copy only requirements first for better caching
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the project files
COPY . /app/

# Expose the port for Django
EXPOSE 8000

# Default command for running the container
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
