# stage 1: Builder
# use python image as the base
FROM python:3.11-slim AS builder

# setting working directory
WORKDIR /app

# create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# copy the requirements file first to leverage Docker's layer caching
COPY requirements.txt .

# install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# stage 2: final image
# start from a fresh, clean base image
FROM python:3.11-slim

# set the same working directory
WORKDIR /app

# copy the virtual environment with all its packages from the 'builder' stage
COPY --from=builder /opt/venv /opt/venv

# copy the application source code
COPY . .

# activate the virtual environment for all subsequent commands
ENV PATH="/opt/venv/bin:$PATH"

# create a non-root user to run the application
RUN useradd --create-home appuser && \
    chown -R appuser:appuser /app

# expose the port that the application will run on
EXPOSE 8000

# The command to run the application in production using Gunicorn
# -w 1: Use 1 worker process
# -k uvicorn.workers.UvicornWorker: Use Uvicorn's high-performance worker class
# -b 0.0.0.0:8000: Bind to all network interfaces on port 8000
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "main:app", "-b", "0.0.0.0:8000"]