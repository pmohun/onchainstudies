import { build } from 'esbuild';
await build({ entryPoints: ['dev-tools/agentation.jsx'], bundle: true, format: 'esm', platform: 'browser', target: 'es2020', outfile: '.local/agentation.js', define: { 'process.env.NODE_ENV': '"development"' } });
