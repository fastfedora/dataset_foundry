#!/bin/bash
set -euo pipefail  # Exit on error, undefined vars, and pipeline failures
IFS=$'\n\t'        # Stricter word splitting

# Accept config file as argument, default to allowed-domains.yaml in current directory
CONFIG_FILE="${1:-firewall.yaml}"

# If not fully qualified, resolve relative to current working directory
if [[ "$CONFIG_FILE" != /* ]]; then
    CONFIG_FILE="$(pwd)/$CONFIG_FILE"
fi

read_domains_from_yaml() {
    local config_file="$1"
    echo "Checking yq installed" >&2
    if ! command -v yq >/dev/null 2>&1; then
        echo "ERROR: yq is required to parse YAML files. Please install yq first." >&2
        echo "Install with: pip install yq or go install github.com/mikefarah/yq/v4@latest" >&2
        exit 1
    fi
    echo "Checking config file exists: $config_file" >&2
    if [ ! -f "$config_file" ]; then
        echo "ERROR: YAML config file not found: $config_file" >&2
        exit 1
    fi
    echo "Attempting to parse YAML file: $config_file" >&2
    yq -r '.allowed_domains[]' "$config_file" | grep -v '^$' | grep -v '^#'
}

resolve_and_add_domains() {
    local domains="$1"
    echo "Resolving and adding domains to ipset..."
    while read -r domain; do
        if [ -z "$domain" ]; then
            continue
        fi
        echo "Resolving $domain..."
        ips=$(dig +short A "$domain")
        if [ -z "$ips" ]; then
            echo "ERROR: Failed to resolve $domain" >&2
            # exit 1
        else
            while read -r ip; do
                if [[ ! "$ip" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
                    echo "ERROR: Invalid IP from DNS for $domain: $ip" >&2
                    exit 1
                fi
                echo "Adding $ip for $domain"
                ipset add allowed-domains "$ip"
            done < <(echo "$ips")
        fi
    done < <(echo "$domains")
}

echo "Reading domains from configuration file: $CONFIG_FILE"
domains=$(read_domains_from_yaml "$CONFIG_FILE")
resolve_and_add_domains "$domains"
