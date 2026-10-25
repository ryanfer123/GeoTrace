"""Execute the real restore adapter against controlled source responses."""
from pathlib import Path
import shutil
import subprocess
import unittest


class CloudRestoreTests(unittest.TestCase):
    def test_restores_revalidate_sources_and_report_changed_bytes(self):
        node = shutil.which('node')
        if node is None:
            self.skipTest('Node.js is required for adapter tests')
        script = r'''
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
let adapter, shown, applied, message, requested;
const elements = new Map();
const context = {
  current: null, busy: false,
  $: id => { if (!elements.has(id)) elements.set(id, {value:'',addEventListener(){}}); return elements.get(id); },
  CloudWorkspace: {init: value => {adapter=value; return {open(){}};}},
  api: async (path, spec) => { requested={path,spec}; return fresh; },
  applySpec: spec => {applied=spec;},
  showComparison: value => {shown=value;}, notice: value => {message=value;},
};
vm.createContext(context);
const source=fs.readFileSync(process.argv[1],'utf8').split('// Cloud copies keep the source description')[1];
assert.ok(source,'adapter source must exist');
vm.runInContext('// Cloud copies keep the source description'+source,context);
let fresh={spec:{name:'validated'},sources:{before:{sha256:'before'},after:{sha256:'after'}}};
const payload={schema:'geotrace-investigation-v1',spec:{name:'saved'},sources:{before:{sha256:'before',url:'https://untrusted.invalid'},after:{sha256:'after'}}};
(async()=>{
  await adapter.onLoad(payload);
  assert.equal(requested.path,'/api/compare');assert.equal(requested.spec,payload.spec);
  assert.equal(applied,fresh.spec);assert.equal(shown,fresh);
  assert.match(message,/freshly validated/);
  payload.sources.after.sha256='old-response';
  await adapter.onLoad(payload);
  assert.equal(shown,fresh);assert.match(message,/Source bytes changed since this cloud copy/);
  context.api=async()=>{throw Error('source unavailable');};shown=null;applied=null;
  await assert.rejects(adapter.onLoad(payload),/source unavailable/);
  assert.equal(shown,null);assert.equal(applied,null);
  await assert.rejects(adapter.onLoad({schema:'unknown',spec:{}}),/not a supported/);
})().catch(error=>{console.error(error);process.exitCode=1;});
'''
        path = Path(__file__).resolve().parents[1] / 'geotrace/web/app.js'
        result = subprocess.run([node, '-e', script, str(path)], capture_output=True,
                                text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
