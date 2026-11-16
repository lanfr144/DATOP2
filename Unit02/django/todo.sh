#!/usr/bin/env bash
# see https://github.com/machadop1407/react-django-tutorial/blob/main/server/newproject/api/serializer.py
# ==============================================================================
# Script Name: setup_django.sh
# Description: Scaffolds a new Django project, creates an app, and registers
#              Django REST Framework and the new app in settings.py.
# ==============================================================================

# Enable strict mode:
# -e: Exit immediately if any command returns a non-zero exit status.
# -u: Treat unset variables as an error and exit immediately.
# -o pipefail: Return the exit status of the last failed command in a pipeline.

# My first draw !
#!/bin/bash
#export Project=firstdjangotest &&
#export API=api &&
#django-admin startproject $Project &&
#cd $Project &&
#python3 manage.py startapp $API &&
#cd $Project &&
#[ -f settings.py ] &&
#grep INSTALLED_APPS settings.py &&
#echo "/INSTALLED_APPS
#/\\]
#-
#a
#    'rest_framework',
#    '$API',
#.
#w
#q" | ed settings.py &&
#echo done ||
#echo "Error $?"
#
#python manage.py makemigrations
#python manage.py migrate
#edit api/serializer.py
#edit api/urls.py

set -euo pipefail

# --- Configuration (Override via environment variables if desired) ---
PROJECT_NAME="${PROJECT_NAME:-firstdjangotest}"
APP_NAME="${APP_NAME:-api}"

# --- Error Handling & Logging ---
log_info() {
    echo "[INFO] $1"
}

log_error() {
    echo "[ERROR] $1" >&2
}

# Trap unexpected failures to display the exact line number and exit code
on_error() {
    local exit_code=$?
    local line_no=$1
    log_error "Script failed at line ${line_no} with exit status ${exit_code}."
    exit "${exit_code}"
}
trap 'on_error $LINENO' ERR

# --- Pre-flight Dependency & State Checks ---
log_info "Running pre-flight checks..."

# 1. Check required CLI binaries
for cmd in python3 django-admin; do
    if ! command -v "${cmd}" >/dev/null 2>&1; then
        log_error "Required command '${cmd}' is not installed or not in PATH."
        exit 1
    fi
done

# 2. Verify 'djangorestframework' is installed in the current Python environment
if ! python3 -c "import rest_framework" >/dev/null 2>&1; then
    log_error "'djangorestframework' is not installed in the active Python environment."
    log_error "Install it first using: pip install djangorestframework"
    exit 1
fi

# 3. Prevent accidental overwrites if the project directory already exists
if [[ -d "${PROJECT_NAME}" ]]; then
    log_error "Directory '${PROJECT_NAME}' already exists. Aborting to prevent overwriting."
    exit 1
fi

# --- Project & App Creation ---
log_info "Creating Django project '${PROJECT_NAME}'..."
django-admin startproject "${PROJECT_NAME}"

log_info "Entering project root '${PROJECT_NAME}'..."
cd "${PROJECT_NAME}"

log_info "Creating Django app '${APP_NAME}'..."
python3 manage.py startapp "${APP_NAME}"

# --- Safely Update settings.py ---
SETTINGS_FILE="${PROJECT_NAME}/settings.py"

if [[ ! -f "${SETTINGS_FILE}" ]]; then
    log_error "Expected settings file '${SETTINGS_FILE}' was not found."
    exit 1
fi

if ! grep -q "INSTALLED_APPS" "${SETTINGS_FILE}"; then
    log_error "'INSTALLED_APPS' list not found in '${SETTINGS_FILE}'."
    exit 1
fi

log_info "Registering 'rest_framework' and '${APP_NAME}' in '${SETTINGS_FILE}'..."

# Using Python instead of 'ed' or 'sed' ensures cross-platform compatibility (Linux/macOS),
# doesn't require legacy packages, and safely parses the INSTALLED_APPS block.
python3 - "${SETTINGS_FILE}" "${APP_NAME}" << 'EOF'
import re
import sys

settings_path = sys.argv[1]
app_name = sys.argv[2]

with open(settings_path, "r", encoding="utf-8") as f:
    content = f.read()

# Match INSTALLED_APPS = [ ... ] across multiple lines
pattern = re.compile(r"(INSTALLED_APPS\s*=\s*\[)(.*?)(\n\])", re.DOTALL)
match = pattern.search(content)

if not match:
    print("Could not reliably parse INSTALLED_APPS structure.", file=sys.stderr)
    sys.exit(1)

header, body, footer = match.groups()

# Ensure trailing comma on the last existing entry if missing
stripped_body = body.rstrip()
if stripped_body and not stripped_body.endswith(","):
    body = stripped_body + ",\n"

# Append the new apps with standard 4-space indentation
addition = f"    'rest_framework',\n    '{app_name}',"
updated_block = f"{header}{body}\n{addition}{footer}"

new_content = content[:match.start()] + updated_block + content[match.end():]

with open(settings_path, "w", encoding="utf-8") as f:
    f.write(new_content)
EOF

# --- Final Verification ---
log_info "Running Django system check to verify configuration..."
python3 manage.py check

log_info "Setup complete! Project '${PROJECT_NAME}' with app '${APP_NAME}' is ready."
