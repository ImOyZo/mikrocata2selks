#!/usr/bin/env python3
import yaml

compose_file = "/srv/SELKS/docker/compose.yml"
new_volume = "${PWD}/containers-data/nginx/custom-rules:/etc/nginx/custom-rules:ro"

with open(compose_file, "r") as f:
    original_lines = f.readlines()
    data = yaml.safe_load("".join(original_lines))

# Quick check using PyYAML to avoid duplicates
nginx = data.get("services", {}).get("nginx", {})
if new_volume in nginx.get("volumes", []):
    print("Volume already exists.")
else:
    output_lines = []
    inside_nginx = False
    inside_volumes = False

    for line in original_lines:
        stripped = line.strip()

        # Detect start of nginx service in yml
        if stripped.startswith("nginx:"):
            inside_nginx = True

        # Detect inside nginx volumes block
        if inside_nginx and stripped.startswith("volumes:"):
            inside_volumes = True

        if inside_volumes and (not stripped.startswith("- ") and not stripped.startswith("volumes:")):
            indent = " " * (line.index(stripped)) + "  "
            output_lines.append(f"{indent}- {new_volume}\n")
            inside_volumes = False

        output_lines.append(line)

    with open(compose_file, "w") as f:
        f.writelines(output_lines)

    print("New volume added successfully.")
