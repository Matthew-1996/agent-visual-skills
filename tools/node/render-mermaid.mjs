#!/usr/bin/env node

import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import puppeteer from "puppeteer-core";

const toolRoot = path.dirname(fileURLToPath(import.meta.url));
const mermaidBundle = path.join(
  toolRoot,
  "node_modules",
  "@mermaid-js",
  "mermaid-cli",
  "node_modules",
  "mermaid",
  "dist",
  "mermaid.min.js",
);
const networkProtocols = new Set(["http:", "https:", "ws:", "wss:"]);
const hardenedArgs = [
  "--disable-background-networking",
  "--disable-component-update",
  "--disable-default-apps",
  "--disable-domain-reliability",
  "--disable-features=AutofillServerCommunication,CertificateTransparencyComponentUpdater,InterestFeedContentSuggestions,MediaRouter,OptimizationHints,ServiceWorker,Translate",
  "--disable-sync",
  "--metrics-recording-only",
  "--no-default-browser-check",
  "--no-first-run",
  "--safebrowsing-disable-auto-update",
];

function argumentsFrom(commandLine) {
  const result = {};
  for (let index = 0; index < commandLine.length; index += 2) {
    const key = commandLine[index];
    const value = commandLine[index + 1];
    if (!key?.startsWith("--") || !value) throw new Error("expected --input, --output, and --chrome");
    result[key.slice(2)] = value;
  }
  for (const key of ["input", "output", "chrome"]) {
    if (!result[key]) throw new Error(`missing --${key}`);
  }
  if (!new Set([".svg", ".png"]).has(path.extname(result.output).toLowerCase())) {
    throw new Error("Mermaid output must use .svg or .png");
  }
  return result;
}

async function hardenPage(page, blockedRequests) {
  await page.setBypassServiceWorker(true);
  await page.evaluateOnNewDocument(() => {
    globalThis.WebSocket = class BlockedWebSocket {
      constructor() {
        throw new DOMException("WebSocket disabled by local-only Mermaid bridge", "SecurityError");
      }
    };
    if (navigator.serviceWorker) {
      navigator.serviceWorker.register = async () => {
        throw new DOMException("Service workers disabled by local-only Mermaid bridge", "SecurityError");
      };
    }
  });
  await page.setRequestInterception(true);
  page.on("request", (request) => {
    let protocol = "";
    try {
      protocol = new URL(request.url()).protocol;
    } catch {
      protocol = "";
    }
    if (networkProtocols.has(protocol)) {
      blockedRequests.push(request.url());
      void request.abort("blockedbyclient");
    } else {
      void request.continue();
    }
  });
  const session = await page.createCDPSession();
  await session.send("Network.enable");
  await session.send("Network.setBlockedURLs", {
    urls: ["http://*", "https://*", "ws://*", "wss://*"],
  });
  await session.send("Network.emulateNetworkConditions", {
    offline: true,
    latency: 0,
    downloadThroughput: 0,
    uploadThroughput: 0,
  });
}

async function main() {
  const options = argumentsFrom(process.argv.slice(2));
  const source = await fs.readFile(options.input, "utf8");
  const browser = await puppeteer.launch({
    executablePath: options.chrome,
    headless: true,
    args: hardenedArgs,
  });
  const blockedRequests = [];
  try {
    browser.on("targetcreated", async (target) => {
      const candidate = await target.page();
      if (candidate && candidate.url() !== "about:blank") await hardenPage(candidate, blockedRequests);
    });
    const page = await browser.newPage();
    await hardenPage(page, blockedRequests);
    await page.setViewport({ width: 1440, height: 1000, deviceScaleFactor: 1 });
    await page.setContent(
      "<!doctype html><html><head><meta charset='utf-8'></head><body><main id='diagram'></main></body></html>",
    );
    await page.addScriptTag({ content: await fs.readFile(mermaidBundle, "utf8") });
    const svg = await page.evaluate(async (diagramSource) => {
      mermaid.initialize({
        startOnLoad: false,
        securityLevel: "strict",
        secure: ["securityLevel", "startOnLoad"],
        fontFamily: "PingFang SC, Hiragino Sans GB, Microsoft YaHei, Noto Sans CJK SC, sans-serif",
      });
      const rendered = await mermaid.render("local-mermaid-diagram", diagramSource);
      document.querySelector("#diagram").innerHTML = rendered.svg;
      const root = document.querySelector("#diagram svg");
      if (!root) throw new Error("Mermaid did not produce an SVG root");
      return new XMLSerializer().serializeToString(root);
    }, source);
    if (blockedRequests.length) {
      throw new Error(`local-only Mermaid bridge blocked network request: ${blockedRequests[0]}`);
    }
    if (path.extname(options.output).toLowerCase() === ".svg") {
      await fs.writeFile(options.output, svg, "utf8");
    } else {
      const element = await page.$("#diagram svg");
      if (!element) throw new Error("Mermaid did not produce an SVG root");
      await element.screenshot({ path: options.output, omitBackground: false });
    }
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(`local-only Mermaid bridge failed: ${error.message}`);
  process.exitCode = 1;
});
