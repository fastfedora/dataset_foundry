FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Install Python testing dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    pytest-mock

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash guest

# Copy the init script
COPY init.sh /usr/local/bin/init.sh
RUN chmod +x /usr/local/bin/init.sh

USER guest

# Install dependencies, if needed
ENTRYPOINT ["sh", "-c", "/usr/local/bin/init.sh && bash -c \"$*\"", "--"]

# Default command (can be overridden)
CMD ["python"]