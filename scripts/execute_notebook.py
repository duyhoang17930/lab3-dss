"""Execute with the invoking Python kernel, no global kernelspec installation."""
from pathlib import Path
from hashlib import sha256
import json
import sys
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpec

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'LabDSS_RECSYS_9_thuat_toan.ipynb'
nb=nbformat.read(path,as_version=4)
km=KernelManager(kernel_name='python3')
km._kernel_spec=KernelSpec(argv=[sys.executable,'-X','utf8','-m','ipykernel_launcher','-f','{connection_file}'],
                           display_name='Python LabDSS',language='python')
client=NotebookClient(nb,km=km,timeout=600,resources={'metadata':{'path':str(ROOT)}},allow_errors=False)
client.execute()
nbformat.write(nb,path)
code=[c for c in nb.cells if c.cell_type=='code']
errors=[o for c in code for o in c.outputs if o.output_type=='error']
assert not errors and all(c.execution_count is not None for c in code)
qa=ROOT/'qa';qa.mkdir(exist_ok=True)
(qa/'notebook_execution.json').write_text(json.dumps({'status':'PASS','code_cells':len(code),'errors':len(errors),
    'sha256':sha256(path.read_bytes()).hexdigest(),'python':sys.version},indent=2),encoding='utf-8')
print(f'PASS: {len(code)} code cells, 0 errors')
