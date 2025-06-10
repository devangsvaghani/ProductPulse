# Stage 1: Builder
# For compiling all dependencies for reducing size of the final image.

FROM public.ecr.aws/lambda/python:3.11-arm64 AS builder

# Doing this because numpy library requires a C and C++ compiler to build.
RUN yum groupinstall -y "Development Tools" && yum install -y openssl-devel

WORKDIR /deps

# Copy only the requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt -t . --no-cache-dir


# Stage 2: Final Image
# The final image 
FROM public.ecr.aws/lambda/python:3.11-arm64

# From documentation of aws lambda
WORKDIR ${LAMBDA_TASK_ROOT}

COPY --from=builder /deps/ ${LAMBDA_TASK_ROOT}/

COPY *.py ${LAMBDA_TASK_ROOT}/

# Download and place the NLTK data directly.
# This ensures it's in the correct final location.
# Because lambda functions have only read access
RUN python3.11 -m nltk.downloader -d ${LAMBDA_TASK_ROOT}/nltk_data vader_lexicon

# Set the final run command
CMD [ "lambda_function.lambda_handler" ]