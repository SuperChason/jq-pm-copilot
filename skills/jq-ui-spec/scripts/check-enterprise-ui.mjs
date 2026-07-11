#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const target = path.resolve(process.argv[2] || ".");
const extensions = new Set([".html", ".htm", ".css", ".js", ".jsx", ".ts", ".tsx", ".vue"]);
const requiredVariables = [
  "--color-primary",
  "--color-primary-hover",
  "--color-primary-active",
  "--color-text-primary",
  "--color-text-secondary",
  "--color-border",
  "--color-bg",
  "--color-surface",
  "--spacing-sm",
  "--spacing-md",
  "--radius-base",
  "--header-height",
  "--sidebar-width",
  "--font-size-base"
];
const allowedColors = new Set([
  "#3e5bf2", "#5b75ff", "#2842d9", "#f0f2ff", "#52c41a", "#faad14",
  "#f5222d", "#1890ff", "#1a1a1a", "#6e6e73", "#a0a0a5", "#cccccc",
  "#e5e5e5", "#f0f0f0", "#f5f5f7", "#ffffff", "#f9f9fa", "#f5f7fa",
  "#060e36"
]);
const errors = [];
const warnings = [];

function collectFiles(entry) {
  if (!fs.existsSync(entry)) {
    errors.push({ file: entry, rule: "target-exists", message: "检查目标不存在" });
    return [];
  }
  const stat = fs.statSync(entry);
  if (stat.isFile()) return extensions.has(path.extname(entry).toLowerCase()) ? [entry] : [];
  return fs.readdirSync(entry, { withFileTypes: true }).flatMap((item) => {
    if (item.name === "node_modules" || item.name === ".git" || item.name === "dist") return [];
    return collectFiles(path.join(entry, item.name));
  });
}

const files = collectFiles(target);
const contents = files.map((file) => ({ file, text: fs.readFileSync(file, "utf8") }));
const styleText = contents
  .filter(({ file }) => [".css", ".html", ".htm", ".vue", ".jsx", ".tsx"].includes(path.extname(file).toLowerCase()))
  .map(({ text }) => text)
  .join("\n");

if (files.length === 0 && errors.length === 0) {
  errors.push({ file: target, rule: "supported-files", message: "未找到可检查的前端文件" });
}

if (styleText) {
  for (const variable of requiredVariables) {
    if (!styleText.includes(variable + ":")) {
      errors.push({ file: target, rule: "required-token", message: "缺少设计令牌 " + variable });
    }
  }
  if (!styleText.includes(":focus-visible")) {
    warnings.push({ file: target, rule: "visible-focus", message: "未发现 :focus-visible 样式" });
  }
  if (styleText.includes("var(--sidebar-active)")) {
    errors.push({ file: target, rule: "defined-token", message: "请使用已定义的 --sidebar-active-bg" });
  }
  const colors = new Set((styleText.match(/#[0-9a-fA-F]{6}\b/g) || []).map((value) => value.toLowerCase()));
  for (const color of colors) {
    if (!allowedColors.has(color)) {
      warnings.push({ file: target, rule: "approved-color", message: "发现规范外颜色 " + color });
    }
  }
}

for (const { file, text } of contents) {
  const ext = path.extname(file).toLowerCase();
  if (ext === ".html" || ext === ".htm") {
    const emoji = /[\u{1F300}-\u{1FAFF}]/u;
    if (emoji.test(text)) {
      warnings.push({ file, rule: "svg-icons", message: "发现 emoji，请确认没有把它当作界面图标" });
    }
    const images = text.match(/<img\b[^>]*>/gi) || [];
    for (const image of images) {
      if (!/\balt\s*=\s*["'][^"']*["']/i.test(image)) {
        errors.push({ file, rule: "image-alt", message: "图片缺少 alt 属性" });
      }
    }
    const buttons = text.match(/<button\b[\s\S]*?<\/button>/gi) || [];
    for (const button of buttons) {
      const label = button
        .replace(/<svg[\s\S]*?<\/svg>/gi, "")
        .replace(/<[^>]+>/g, "")
        .replace(/\s+/g, "");
      if (!label && !/aria-label\s*=\s*["'][^"']+["']/i.test(button)) {
        errors.push({ file, rule: "button-name", message: "图标按钮缺少 aria-label" });
      }
    }
  }
}

console.log("企业 UI 静态检查");
console.log("目标: " + target);
console.log("文件: " + files.length + "，错误: " + errors.length + "，提醒: " + warnings.length);

for (const item of errors) {
  console.log("[错误] " + item.rule + " | " + path.relative(process.cwd(), item.file) + " | " + item.message);
}
for (const item of warnings) {
  console.log("[提醒] " + item.rule + " | " + path.relative(process.cwd(), item.file) + " | " + item.message);
}

process.exitCode = errors.length > 0 ? 1 : 0;
