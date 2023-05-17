# Use a Python image base
FROM python:3.9

# Sets the working directory on the container
WORKDIR /app

# Copies the requirements.txt file to the container
COPY requirements.txt .

# Installs the dependencies specified in the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Copies all files from the current directory to the container
COPY . .

# Set environment variables
ENV DB_HOSTNAME=db
ENV DB_PORT=5432
ENV DB_NAME=postgres
ENV DB_USER=postgres
ENV DB_PASSWORD=postgres123456*
ENV API_URL=https://storage.googleapis.com/xcc-de-assessment/events.json

# Run the command to initialize the database
CMD python -u app.py

# Exposes the application port
EXPOSE 8000

