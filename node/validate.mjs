// Khronos glTF validator on one GLB. Usage: node validate.mjs <file.glb>  -> JSON on stdout
import { readFile } from "node:fs/promises";
import validator from "gltf-validator";

const file = process.argv[2];
const data = new Uint8Array(await readFile(file));
const report = await validator.validateBytes(data, { maxIssues: 200 });
const issues = report.issues;
console.log(JSON.stringify({
  ok: issues.numErrors === 0,
  errors: issues.numErrors,
  warnings: issues.numWarnings,
  infos: issues.numInfos,
  messages: issues.messages.filter((m) => m.severity <= 1).map((m) => ({ severity: m.severity === 0 ? "error" : "warning", code: m.code, message: m.message, pointer: m.pointer })),
  generator: report.info?.generator,
  animationCount: report.info?.animationCount,
}));
