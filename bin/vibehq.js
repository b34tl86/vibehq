#!/usr/bin/env node
/**
 * VibeHQ CLI Node wrapper.
 * Invokes python -m vibehq with all passed arguments.
 */
const { spawn } = require('child_process');
const path = require('path');

const args = process.argv.slice(2);
const pythonCmd = process.env.VIBEHQ_PYTHON || 'python3';

const proc = spawn(pythonCmd, ['-m', 'vibehq.cli', ...args], {
  stdio: 'inherit',
  env: {
    ...process.env,
    PYTHONPATH: path.resolve(__dirname, '..') + (process.env.PYTHONPATH ? ':' + process.env.PYTHONPATH : '')
  }
});

proc.on('error', (err) => {
  if (err.code === 'ENOENT') {
    console.error(`\n❌ Error: '${pythonCmd}' was not found in your PATH.`);
    console.error(`   Please ensure Python 3.9+ is installed or set VIBEHQ_PYTHON.\n`);
  } else {
    console.error('Failed to run VibeHQ:', err);
  }
  process.exit(1);
});

proc.on('exit', (code) => {
  process.exit(code || 0);
});

