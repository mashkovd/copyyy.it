# Use an official Python runtime as a parent image
FROM python:3.12-slim
ENV PATH="/root/.local/bin:$PATH"\
    POETRY_VERSION="1.8.2"

# Install system dependencies
RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python -

# Set the working directory in the container
WORKDIR /app

# Copy only the 'pyproject.toml' and 'poetry.lock' files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create true \
    && poetry install --no-root --no-dev --no-interaction --no-ansi

# Copy the rest of the application
COPY . .

# Expose port 8000 if needed for other services
EXPOSE 8000
