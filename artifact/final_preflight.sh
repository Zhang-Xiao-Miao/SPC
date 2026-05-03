#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1

echo "[1] Check for identity leaks"
if grep -R -I -i -n --exclude='final_preflight.sh' "AUTHOR[_]NAME\|INSTITUTION[_]NAME\|EMAIL[_]ADDRESS\|github[.]com/REALUSER\|/home[/]REALUSER\|/Users[/]REALUSER" .; then
  echo "[FAIL] placeholder identity leak found"
  exit 1
fi
printf '[PASS] placeholder identity leak scan clean\n'

echo "[2] Check unwanted files"
if find . \( -name ".git" -o -name "__MACOSX" -o -name ".DS_Store" -o -name "*.pyc" -o -name "__pycache__" \) | grep -q .; then
  find . \( -name ".git" -o -name "__MACOSX" -o -name ".DS_Store" -o -name "*.pyc" -o -name "__pycache__" \)
  echo "[FAIL] unwanted files found"
  exit 1
fi
printf '[PASS] unwanted-file scan clean\n'

echo "[3] Run cached-output reproduction"
bash artifact/reproduce_main.sh

echo "[4] Run provenance verification"
bash artifact/verify_provenance.sh

echo "[5] Create local extracted-package manifests"
find . -type f | sort > artifact_file_manifest.txt
find . -type f -print0 | sort -z | xargs -0 sha256sum > artifact_sha256_manifest.txt
printf '[PASS] extracted-package manifests created\n'

echo "[6] Check extracted package size"
du -sh .

printf '[PASS] final artifact preflight complete\n'
