FROM homebrew/ubuntu22.04
USER root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y curl git build-essential software-properties-common && \
    rm -rf /var/lib/apt/lists/*

RUN brew install codex

WORKDIR /workspace

ENV LANG=en_US.UTF-8
ENV PYTHONUNBUFFERED=1

# Default command (will be overridden by entrypoint)
CMD ["bash"]