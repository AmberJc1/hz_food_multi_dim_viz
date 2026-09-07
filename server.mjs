import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL(".", import.meta.url));
const port = Number(process.env.PORT || 4173);
const types = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".csv": "text/csv; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png"
};

const json = (res, status, body) => {
  res.writeHead(status, { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" });
  res.end(JSON.stringify(body));
};

async function readJson(req) {
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > 200_000) throw new Error("请求内容过大");
    chunks.push(chunk);
  }
  return JSON.parse(Buffer.concat(chunks).toString("utf8") || "{}");
}

function aiPrompt(task, payload) {
  const instructions = {
    predict: `根据商家特征和杭州同类商家基线预测 0-5 分评分。返回 JSON：{"score":4.35,"confidence":82,"factors":[{"name":"因素名","value":0.6,"impact":0.18}]}。factors 最多 6 项，value 范围 -1 到 1，impact 是对评分的增减。`,
    recommend: `理解用户选餐需求，只能从给定候选商家中推荐。返回 JSON：{"recommendations":[{"id":"候选商家原始id","reason":"一句具体推荐理由"}]}。推荐 3-5 家，不得编造候选列表之外的商家。`
  };
  if (!instructions[task]) throw new Error("不支持的 AI 任务");
  return `${instructions[task]}\n只输出合法 JSON，不要 Markdown。\n输入数据：${JSON.stringify(payload)}`;
}

function parseModelJson(content) {
  const text = String(content || "").trim().replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/, "");
  const start = text.indexOf("{");
  const end = text.lastIndexOf("}");
  if (start < 0 || end < start) throw new Error("模型未返回有效 JSON");
  return JSON.parse(text.slice(start, end + 1));
}

function chatCompletionsUrl(baseUrl) {
  const normalized = String(baseUrl || "").trim().replace(/\/+$/, "");
  return normalized.endsWith("/chat/completions") ? normalized : `${normalized}/chat/completions`;
}

async function handleAi(req, res) {
  const apiKey = process.env.AI_API_KEY;
  const baseUrl = process.env.AI_BASE_URL;
  const model = process.env.AI_MODEL;
  if (!apiKey || !baseUrl || !model) return json(res, 503, { code: "AI_NOT_CONFIGURED", message: "AI 服务尚未配置" });
  const { task, payload } = await readJson(req);
  const upstream = await fetch(chatCompletionsUrl(baseUrl), {
    method: "POST",
    headers: { "Authorization": `Bearer ${apiKey}`, "Content-Type": "application/json" },
    body: JSON.stringify({ model, temperature: 0.2, response_format: { type: "json_object" }, messages: [{ role: "system", content: "你是杭州餐饮选店平台的结构化分析模型。所有输出必须基于输入数据。" }, { role: "user", content: aiPrompt(task, payload) }] })
  });
  const data = await upstream.json().catch(() => ({}));
  if (!upstream.ok) throw new Error(data?.error?.message || `AI 服务响应异常（${upstream.status}）`);
  const content = data?.choices?.[0]?.message?.content;
  return json(res, 200, { result: parseModelJson(content), model });
}

createServer(async (req, res) => {
  try {
    const pathname = decodeURIComponent(new URL(req.url, `http://${req.headers.host}`).pathname);
    if (pathname === "/api/ai") {
      if (req.method !== "POST") return json(res, 405, { message: "仅支持 POST 请求" });
      return await handleAi(req, res);
    }
    const relative = pathname === "/" ? "index.html" : pathname.replace(/^\/+/, "");
    const file = normalize(join(root, relative));
    if (!file.startsWith(normalize(root))) throw new Error("Invalid path");
    const info = await stat(file);
    const target = info.isDirectory() ? join(file, "index.html") : file;
    res.writeHead(200, { "Content-Type": types[extname(target)] || "application/octet-stream", "Cache-Control": "no-store" });
    res.end(await readFile(target));
  } catch (error) {
    if (req.url?.startsWith("/api/ai")) return json(res, 500, { message: error.message || "AI 服务调用失败" });
    res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
    res.end("Not found");
  }
}).listen(port, "127.0.0.1", () => {
  console.log(`杭州味觉图谱已运行：http://127.0.0.1:${port}`);
});
