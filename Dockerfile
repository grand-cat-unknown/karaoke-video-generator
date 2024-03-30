# Use an AWS Lambda Python runtime as a parent image
FROM public.ecr.aws/lambda/python:3.9

# Set the working directory in the container
WORKDIR /var/task

# Copy all files in the current directory to /var/task in the container
COPY . .

# Install OS dependencies
RUN apt-get install -y gcc python3-dev cairo-devel pango-devel ffmpeg

# Install Python dependencies
RUN pip install -r requirements.txt

# Set the CMD to your handler (the AWS Lambda Python runtime expects a function handler)
CMD ["lambda_function.lambda_handler"]