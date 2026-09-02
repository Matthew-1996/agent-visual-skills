import { mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { build } from "esbuild";


const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const nodeRoot = resolve(scriptDirectory, "..");
const outputDirectory = resolve(nodeRoot, "dist");

await mkdir(outputDirectory, { recursive: true });
await build({
  entryPoints: [resolve(nodeRoot, "src", "excalidraw-export.jsx")],
  outfile: resolve(outputDirectory, "excalidraw-export.js"),
  bundle: true,
  format: "iife",
  platform: "browser",
  target: ["chrome120"],
  minify: true,
  legalComments: "eof",
  define: {
    "process.env.NODE_ENV": '"production"',
    "process.env.IS_PREACT": "false",
  },
});
