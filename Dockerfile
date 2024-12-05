FROM python:3.12.3

WORKDIR /app

# Copy the entire src directory
COPY requirements.txt .


# Set timezone
RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*
ENV TZ=Asia/Kolkata

# Upgrade pip and setuptools
RUN pip install --upgrade pip setuptools

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set the command to run the application
CMD [ "python", "main.py" ]
