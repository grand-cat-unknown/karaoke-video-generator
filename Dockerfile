# Use the official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the local Lambda function code to the container
COPY . /app

# Install any dependencies, including lxml
RUN apt-get update && apt install build-essential python3-dev libcairo2-dev libpango1.0-dev ffmpeg -y
RUN pip install -r requirements.txt

# Command to run your Lambda function
CMD ["lambda_function.lambda_handler"]

