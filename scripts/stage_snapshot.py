"""One-command staging build from local analysis outputs; never publishes."""
from pathlib import Path
import subprocess
import sys
import tempfile

root=Path(__file__).resolve().parents[1]
(root/'tmp').mkdir(exist_ok=True)
dest=Path(tempfile.mkdtemp(prefix='snapshot-',dir=root/'tmp'))
for command in [
    ['scripts/prepare_deployment.py','--output-dir',str(dest)],
    ['scripts/build_team_context.py','--output-dir',str(dest)],
    ['scripts/verify_snapshot.py','--directory',str(dest),'--write-manifest'],
    ['scripts/verify_snapshot.py','--directory',str(dest)],
]:
    subprocess.run([sys.executable,*command],cwd=root,check=True)
print(f'Review the staged files at {dest}. No hosted files were replaced.')
