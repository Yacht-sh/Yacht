"use strict";

const { spawn } = require("child_process");
const path = require("path");

const vueCliService = path.join(
  __dirname,
  "..",
  "node_modules",
  "@vue",
  "cli-service",
  "bin",
  "vue-cli-service.js"
);

function createFilter(write) {
  let buffer = "";
  let suppressBlock = false;

  function flushLine(line) {
    if (line.startsWith("DEPRECATION WARNING [")) {
      suppressBlock = true;
      return;
    }

    if (
      line.startsWith("WARNING: ") &&
      line.includes("repetitive deprecation warnings omitted")
    ) {
      return;
    }

    if (suppressBlock) {
      if (line.trim() === "") {
        suppressBlock = false;
      }
      return;
    }

    write(`${line}\n`);
  }

  const filter = chunk => {
    buffer += chunk.toString();
    const lines = buffer.split(/\r?\n/);
    buffer = lines.pop();

    for (const line of lines) {
      flushLine(line);
    }
  };

  filter.flush = () => {
    if (buffer) {
      flushLine(buffer);
      buffer = "";
    }
  };

  return filter;
}

const stdoutFilter = createFilter(chunk => process.stdout.write(chunk));
const stderrFilter = createFilter(chunk => process.stderr.write(chunk));

const child = spawn(
  process.execPath,
  [vueCliService, "build"],
  {
    cwd: path.join(__dirname, ".."),
    env: {
      ...process.env,
      SASS_SILENCE_DEPRECATIONS:
        "legacy-js-api,import,global-builtin,if-function,slash-div",
    },
    stdio: ["inherit", "pipe", "pipe"],
  }
);

child.stdout.on("data", stdoutFilter);
child.stderr.on("data", stderrFilter);

child.on("close", code => {
  stdoutFilter.flush();
  stderrFilter.flush();
  process.exit(code ?? 1);
});
