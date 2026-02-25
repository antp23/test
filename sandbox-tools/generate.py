#!/usr/bin/env python3
"""
Sandbox Environment Generator

Reads a sandbox.yml config file and generates:
  - .sandbox/docker-compose.yml
  - .sandbox/Dockerfile.<service> for app services
  - .sandbox/entrypoint-<service>.sh for services with init commands

Zero external dependencies — uses only Python 3 standard library.
"""

import json
import os
import re
import stat
import sys
import textwrap

# ---------------------------------------------------------------------------
# Minimal YAML parser (handles the subset needed for sandbox.yml)
# Supports: scalars, quoted strings, maps, lists, nested indentation
# ---------------------------------------------------------------------------

class YAMLParser:
    """Lightweight YAML parser for sandbox config files."""

    def __init__(self, text):
        self.lines = text.splitlines()
        self.pos = 0

    def parse(self):
        return self._parse_mapping(0)

    def _current_indent(self, line):
        return len(line) - len(line.lstrip())

    def _strip_comment(self, value):
        # Remove inline comments (not inside quotes)
        in_quote = None
        for i, ch in enumerate(value):
            if ch in ('"', "'") and in_quote is None:
                in_quote = ch
            elif ch == in_quote:
                in_quote = None
            elif ch == '#' and in_quote is None:
                return value[:i].rstrip()
        return value

    def _parse_value(self, raw):
        raw = self._strip_comment(raw).strip()
        if raw == '':
            return None
        # Quoted string
        if (raw.startswith('"') and raw.endswith('"')) or \
           (raw.startswith("'") and raw.endswith("'")):
            return raw[1:-1]
        # Boolean
        if raw.lower() in ('true', 'yes'):
            return True
        if raw.lower() in ('false', 'no'):
            return False
        # Integer
        try:
            return int(raw)
        except ValueError:
            pass
        # Float
        try:
            return float(raw)
        except ValueError:
            pass
        return raw

    def _skip_empty(self):
        while self.pos < len(self.lines):
            line = self.lines[self.pos]
            stripped = line.strip()
            if stripped == '' or stripped.startswith('#'):
                self.pos += 1
            else:
                break

    def _parse_mapping(self, expected_indent):
        result = {}
        while self.pos < len(self.lines):
            self._skip_empty()
            if self.pos >= len(self.lines):
                break
            line = self.lines[self.pos]
            indent = self._current_indent(line)
            if indent < expected_indent:
                break
            if indent > expected_indent:
                break
            stripped = line.strip()
            # List item at mapping level — shouldn't happen at top level
            if stripped.startswith('- '):
                break
            # Key-value pair
            match = re.match(r'^(\s*)([\w._-]+)\s*:\s*(.*)', line)
            if not match:
                self.pos += 1
                continue
            key = match.group(2)
            value_str = match.group(3).strip()
            if value_str:
                # Inline value
                result[key] = self._parse_value(value_str)
                self.pos += 1
            else:
                # Value is on next lines (nested map or list)
                self.pos += 1
                self._skip_empty()
                if self.pos >= len(self.lines):
                    result[key] = None
                    continue
                next_line = self.lines[self.pos]
                next_indent = self._current_indent(next_line)
                if next_indent <= expected_indent:
                    result[key] = None
                    continue
                if next_line.strip().startswith('- '):
                    result[key] = self._parse_list(next_indent)
                else:
                    result[key] = self._parse_mapping(next_indent)
        return result

    def _parse_list(self, expected_indent):
        result = []
        while self.pos < len(self.lines):
            self._skip_empty()
            if self.pos >= len(self.lines):
                break
            line = self.lines[self.pos]
            indent = self._current_indent(line)
            if indent < expected_indent:
                break
            stripped = line.strip()
            if not stripped.startswith('- '):
                break
            value = stripped[2:].strip()
            result.append(self._parse_value(value))
            self.pos += 1
        return result


def load_config(path):
    with open(path, 'r') as f:
        text = f.read()
    parser = YAMLParser(text)
    return parser.parse()


# ---------------------------------------------------------------------------
# Dockerfile generators per runtime
# ---------------------------------------------------------------------------

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')


def load_template(name):
    path = os.path.join(TEMPLATE_DIR, name)
    with open(path, 'r') as f:
        return f.read()


def render_template(template, variables):
    """Simple {{var}} template rendering."""
    def replacer(match):
        key = match.group(1)
        return str(variables.get(key, ''))
    return re.sub(r'\{\{(\w+)\}\}', replacer, template)


def generate_dockerfile(service_name, service_config, output_dir):
    runtime = service_config.get('runtime', '')
    template_file = f'{runtime}.Dockerfile'
    template_path = os.path.join(TEMPLATE_DIR, template_file)

    if not os.path.exists(template_path):
        print(f"  Warning: No template for runtime '{runtime}', skipping Dockerfile for {service_name}")
        return None

    template = load_template(template_file)
    variables = {
        'node_version': str(service_config.get('node_version', '22')),
        'python_version': str(service_config.get('python_version', '3.12')),
        'install': service_config.get('install', 'echo "no install step"'),
        'build': service_config.get('build', 'echo "no build step"'),
        'start': service_config.get('start', 'echo "no start command"'),
        'port': str(service_config.get('port', '8080')),
    }

    content = render_template(template, variables)
    dockerfile_path = os.path.join(output_dir, f'Dockerfile.{service_name}')
    with open(dockerfile_path, 'w') as f:
        f.write(content)
    print(f"  Generated {dockerfile_path}")
    return dockerfile_path


def generate_entrypoint(service_name, service_config, output_dir):
    """Generate an entrypoint script for services with init commands."""
    init_cmds = service_config.get('init')
    if not init_cmds:
        return None

    start_cmd = service_config.get('start', 'echo "no start command"')

    lines = ['#!/bin/sh', 'set -e', '']
    lines.append('MARKER="/tmp/.sandbox-initialized"')
    lines.append('')
    lines.append('if [ ! -f "$MARKER" ]; then')
    lines.append('  echo "==> Running initialization commands..."')
    for cmd in init_cmds:
        lines.append(f'  echo "  -> {cmd}"')
        lines.append(f'  {cmd}')
    lines.append('  touch "$MARKER"')
    lines.append('  echo "==> Initialization complete."')
    lines.append('else')
    lines.append('  echo "==> Already initialized, skipping init."')
    lines.append('fi')
    lines.append('')
    lines.append(f'echo "==> Starting {service_name}..."')
    lines.append(f'exec {start_cmd}')
    lines.append('')

    entrypoint_path = os.path.join(output_dir, f'entrypoint-{service_name}.sh')
    with open(entrypoint_path, 'w') as f:
        f.write('\n'.join(lines))
    os.chmod(entrypoint_path, os.stat(entrypoint_path).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    print(f"  Generated {entrypoint_path}")
    return entrypoint_path


# ---------------------------------------------------------------------------
# docker-compose.yml generator
# ---------------------------------------------------------------------------

def indent(text, level=0):
    prefix = '  ' * level
    return '\n'.join(prefix + line if line.strip() else '' for line in text.splitlines())


def generate_compose(config, output_dir, project_root):
    """Generate docker-compose.yml from sandbox config."""
    project_name = config.get('name', 'sandbox')
    services = config.get('services', {})
    volumes_config = config.get('volumes', {})

    compose_lines = []
    compose_lines.append(f'# Auto-generated by sandbox tool — do not edit manually')
    compose_lines.append(f'# Source: sandbox.yml')
    compose_lines.append(f'')
    compose_lines.append(f'name: {project_name}-sandbox')
    compose_lines.append(f'')
    compose_lines.append(f'services:')

    for svc_name, svc_config in services.items():
        compose_lines.append(f'  {svc_name}:')

        if isinstance(svc_config, str):
            # Simple image reference
            compose_lines.append(f'    image: {svc_config}')
            compose_lines.append(f'')
            continue

        # Image-based service (database, cache, etc.)
        if 'image' in svc_config:
            compose_lines.append(f'    image: {svc_config["image"]}')
        elif 'runtime' in svc_config:
            # Build from generated Dockerfile
            svc_path = svc_config.get('path', f'./{svc_name}')
            # Docker context is the service path; Dockerfile is in .sandbox/
            abs_sandbox = os.path.abspath(output_dir)
            rel_sandbox = os.path.relpath(abs_sandbox, project_root)
            compose_lines.append(f'    build:')
            compose_lines.append(f'      context: {svc_path}')
            compose_lines.append(f'      dockerfile: {os.path.join(os.path.abspath(output_dir), f"Dockerfile.{svc_name}")}')

        # Container name
        compose_lines.append(f'    container_name: {project_name}-{svc_name}')

        # Entrypoint override for services with init commands
        if svc_config.get('init'):
            entrypoint_abs = os.path.abspath(os.path.join(output_dir, f'entrypoint-{svc_name}.sh'))
            compose_lines.append(f'    entrypoint: ["/entrypoint.sh"]')
            compose_lines.append(f'    volumes:')
            compose_lines.append(f'      - {entrypoint_abs}:/entrypoint.sh:ro')
            # Add any user-defined volumes too
            if svc_config.get('volumes'):
                for vol in svc_config['volumes']:
                    compose_lines.append(f'      - {vol}')
        elif svc_config.get('volumes'):
            compose_lines.append(f'    volumes:')
            for vol in svc_config['volumes']:
                if isinstance(vol, str):
                    compose_lines.append(f'      - {vol}')

        # Ports
        port = svc_config.get('port')
        if port:
            compose_lines.append(f'    ports:')
            compose_lines.append(f'      - "{port}:{port}"')

        # Environment variables
        env = svc_config.get('environment', {})
        if env:
            compose_lines.append(f'    environment:')
            for k, v in env.items():
                compose_lines.append(f'      {k}: "{v}"')

        # Depends on
        depends = svc_config.get('depends_on', {})
        if depends:
            compose_lines.append(f'    depends_on:')
            if isinstance(depends, dict):
                for dep_name, dep_condition in depends.items():
                    compose_lines.append(f'      {dep_name}:')
                    if dep_condition == 'healthy':
                        compose_lines.append(f'        condition: service_healthy')
                    else:
                        compose_lines.append(f'        condition: service_started')
            elif isinstance(depends, list):
                for dep_name in depends:
                    compose_lines.append(f'      - {dep_name}')

        # Healthcheck
        hc = svc_config.get('healthcheck', {})
        if hc:
            compose_lines.append(f'    healthcheck:')
            if 'test' in hc:
                compose_lines.append(f'      test: ["CMD-SHELL", "{hc["test"]}"]')
            if 'interval' in hc:
                compose_lines.append(f'      interval: {hc["interval"]}')
            if 'timeout' in hc:
                compose_lines.append(f'      timeout: {hc["timeout"]}')
            else:
                compose_lines.append(f'      timeout: 5s')
            if 'retries' in hc:
                compose_lines.append(f'      retries: {hc["retries"]}')

        # Restart policy
        restart = svc_config.get('restart', 'unless-stopped')
        compose_lines.append(f'    restart: {restart}')

        # Network
        compose_lines.append(f'    networks:')
        compose_lines.append(f'      - sandbox-net')
        compose_lines.append(f'')

    # Volumes
    if volumes_config:
        compose_lines.append(f'volumes:')
        for vol_name in volumes_config:
            compose_lines.append(f'  {vol_name}:')
        compose_lines.append(f'')

    # Networks
    compose_lines.append(f'networks:')
    compose_lines.append(f'  sandbox-net:')
    compose_lines.append(f'    driver: bridge')
    compose_lines.append(f'')

    compose_path = os.path.join(output_dir, 'docker-compose.yml')
    with open(compose_path, 'w') as f:
        f.write('\n'.join(compose_lines))
    print(f"  Generated {compose_path}")
    return compose_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: generate.py <sandbox.yml> [output_dir] [project_root]")
        sys.exit(1)

    config_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '.sandbox'
    project_root = sys.argv[3] if len(sys.argv) > 3 else os.path.dirname(os.path.abspath(config_path))

    if not os.path.exists(config_path):
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)

    print(f"Reading config from {config_path}")
    config = load_config(config_path)

    os.makedirs(output_dir, exist_ok=True)
    print(f"Generating files in {output_dir}/")

    services = config.get('services', {})
    for svc_name, svc_config in services.items():
        if isinstance(svc_config, str):
            continue
        # Generate Dockerfile for runtime services
        if 'runtime' in svc_config:
            generate_dockerfile(svc_name, svc_config, output_dir)
        # Generate entrypoint for services with init commands
        if svc_config.get('init'):
            generate_entrypoint(svc_name, svc_config, output_dir)

    # Generate docker-compose.yml
    generate_compose(config, output_dir, project_root)

    print("Done.")


if __name__ == '__main__':
    main()
