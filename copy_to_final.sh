#!/bin/bash
set -euo pipefail

# Determine script and root directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${SCRIPT_DIR}/../ft_irc_final"

echo "Creating target directory: ${TARGET_DIR}"
mkdir -p "${TARGET_DIR}"

echo "Copying directories..."
for dir in Channel Client helpers Server; do
    if [ -d "${SCRIPT_DIR}/${dir}" ]; then
        echo "  - Copying ${dir}/"
        cp -r "${SCRIPT_DIR}/${dir}" "${TARGET_DIR}/"
    else
        echo "  [WARNING] Directory '${dir}' not found!"
    fi
done

# Ensure helpers/libtest is not included in final submission
if [ -d "${TARGET_DIR}/helpers/libtest" ]; then
    echo "  - Excluding helpers/libtest/"
    rm -rf "${TARGET_DIR}/helpers/libtest"
fi

echo "Copying files..."
if [ -f "${SCRIPT_DIR}/.gitignore" ]; then
    echo "  - Copying .gitignore"
    cp "${SCRIPT_DIR}/.gitignore" "${TARGET_DIR}/"
elif [ -f "${SCRIPT_DIR}/gitignore" ]; then
    echo "  - Copying gitignore as .gitignore"
    cp "${SCRIPT_DIR}/gitignore" "${TARGET_DIR}/.gitignore"
fi

if [ -f "${SCRIPT_DIR}/main.cpp" ]; then
    echo "  - Copying main.cpp"
    cp "${SCRIPT_DIR}/main.cpp" "${TARGET_DIR}/"
fi

if [ -f "${SCRIPT_DIR}/Makefile_FINAL" ]; then
    echo "  - Copying Makefile_FINAL as Makefile"
    cp "${SCRIPT_DIR}/Makefile_FINAL" "${TARGET_DIR}/Makefile"
else
    echo "  [WARNING] Makefile_FINAL not found!"
fi

if [ -f "${SCRIPT_DIR}/README.md" ]; then
    echo "  - Copying README.md"
    cp "${SCRIPT_DIR}/README.md" "${TARGET_DIR}/"
fi

echo "Successfully exported project to ${TARGET_DIR}"
