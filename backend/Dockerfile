# Use the official AWS base image for Python 3.11 Lambda functions
FROM public.ecr.aws/lambda/python:3.11

# --- FINAL FIX ---
# Install the complete "Development Tools" group, which includes gcc, g++, make, etc.
# This provides a full C and C++ compilation environment.
RUN yum groupinstall -y "Development Tools"

# Copy the requirements file into the container
COPY requirements.txt ${LAMBDA_TASK_ROOT}/

# Install the Python dependencies from requirements.txt
# With the full toolset installed, all packages will now compile successfully.
RUN pip install -r requirements.txt --no-cache-dir

# Copy the rest of your application code into the container
COPY *.py ${LAMBDA_TASK_ROOT}/

# Set the command to run when the Lambda function is invoked.
CMD [ "lambda_function.lambda_handler" ]