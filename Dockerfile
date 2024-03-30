# Use AWS Lambda Python runtime as a parent image
FROM public.ecr.aws/lambda/python:3.9

# Set the working directory in the container
WORKDIR /var/task

# Copy the local Lambda function code and dependencies to the container
COPY . .

# Install OS dependencies required for building your dependencies but not ffmpeg
RUN yum install -y gcc python3-devel cairo-devel pango-devel

# Install Python dependencies
RUN pip install -r requirements.txt

# Manually download and install ffmpeg
RUN curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz | tar Jxvf - --strip-components=1 -C /usr/local/bin

# Set the CMD to your handler (the AWS Lambda Python runtime expects a function handler)
CMD ["lambda_function.lambda_handler"]
