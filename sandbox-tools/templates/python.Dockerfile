FROM python:{{python_version}}-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements*.txt pyproject.toml* setup.py* setup.cfg* ./
RUN {{install}}

# Copy source and build
COPY . .
RUN {{build}}

EXPOSE {{port}}

CMD ["sh", "-c", "{{start}}"]
