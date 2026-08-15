/** Chọn Python của virtual environment theo hệ điều hành và xuất OpenAPI. */
import { existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const projectRoot = fileURLToPath(new URL('../', import.meta.url));
const virtualEnvironmentPython = process.platform === 'win32'
  ? path.join(projectRoot, '.venv', 'Scripts', 'python.exe')
  : path.join(projectRoot, '.venv', 'bin', 'python');
const pythonCommand = existsSync(virtualEnvironmentPython)
  ? virtualEnvironmentPython
  : 'python';
const exporterPath = path.join(projectRoot, 'scripts', 'export_openapi.py');
const result = spawnSync(pythonCommand, [exporterPath], {
  cwd: projectRoot,
  stdio: 'inherit',
});

if (result.error) throw result.error;
process.exitCode = result.status ?? 1;
