# Use the official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the local Lambda function code to the container
COPY . /app

# Install any dependencies, including lxml
RUN apt-get update && apt install -y \
    build-essential python3-dev libcairo2-dev libpango1.0-dev ffmpeg \
    && pip install -r requirements.txt

# Install the AWS Lambda RIE
RUN apt-get install -y unzip \
    && curl -Lo aws-lambda-rie https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie \
    && chmod +x aws-lambda-rie \
    && mv aws-lambda-rie /usr/local/bin

# Use the AWS Lambda RIE as the entrypoint
ENTRYPOINT [ "/usr/local/bin/aws-lambda-rie" ]

# Command to run your Lambda function
CMD ["python", "-m", "awslambdaric", "lambda_function.lambda_handler"]
