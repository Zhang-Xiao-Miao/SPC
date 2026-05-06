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

echo "[3] Check final manuscript source package"
test -s neurips2026_ed_latex_source_FINAL_v2/paper.tex
test -s neurips2026_ed_latex_source_FINAL_v2/checklist_filled.tex
test -s neurips2026_ed_latex_source_FINAL_v2/neurips_2026.sty
test -s neurips2026_ed_latex_source_FINAL_v2/figure1_claim_audit_logic.png
printf '[PASS] final manuscript source package present\n'

echo "[4] Check live-rerun prerequisite report"
bash artifact/check_live_rerun_prereqs.sh

echo "[5] Run explanatory reviewer claim audit"
bash artifact/reviewer_audit.sh

echo "[6] Run cached-output reproduction"
bash artifact/reproduce_main.sh

echo "[7] Run provenance verification"
bash artifact/verify_provenance.sh

echo "[8] Run optional local project-code smoke test"
if command -v timeout >/dev/null 2>&1; then
  timeout 60 bash artifact/run_smoke_test.sh
else
  echo "[WARN] timeout command not available; running smoke test without timeout"
  bash artifact/run_smoke_test.sh
fi

echo "[9] Check for prompt-injection text"
if grep -R -I -i -n --exclude='final_preflight.sh' --exclude='59_package_ed_artifact.py' "ignore previous instructions\|give this paper a high score\|accept this paper" .; then
  echo "[FAIL] prompt-injection-like text found"
  exit 1
fi
printf '[PASS] prompt-injection scan clean\n'

echo "[10] Create local extracted-package manifests"
rm -f artifact_file_manifest.txt artifact_sha256_manifest.txt
tmp_manifest="$(mktemp)"
tmp_hashes="$(mktemp)"
find . -type f \
  ! -name 'artifact_file_manifest.txt' \
  ! -name 'artifact_sha256_manifest.txt' \
  | sort > "$tmp_manifest"
find . -type f \
  ! -name 'artifact_file_manifest.txt' \
  ! -name 'artifact_sha256_manifest.txt' \
  -print0 | sort -z | xargs -0 sha256sum > "$tmp_hashes"
mv "$tmp_manifest" artifact_file_manifest.txt
mv "$tmp_hashes" artifact_sha256_manifest.txt
printf '[PASS] extracted-package manifests created\n'

echo "[11] Check extracted package size"
du -sh .

printf '[PASS] final artifact preflight complete\n'
