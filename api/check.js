"use strict";
// POST /api/check  { product: "check" | "compare" | "need", vehicle, ...inputs, images: [base64 JPEG] }
// Returns the free first answer plus a sealed copy of the full report.
const { PRODUCTS, parseJson } = require("../lib/core");
const { seal } = require("../lib/seal");

const MAX_IMAGE_B64 = 3 * 1024 * 1024;

// Best-effort limit per visitor. It only holds within one running instance, so also add a
// platform rate limit on /api/check (see README) before sending real traffic.
const HITS = new Map();
const LIMIT = 12, WINDOW_MS = 60 * 60 * 1000;
function limited(req) {
  const ip = String(req.headers["x-forwarded-for"] || "").split(",")[0].trim() || "unknown";
  const now = Date.now();
  const recent = (HITS.get(ip) || []).filter((t) => now - t < WINDOW_MS);
  recent.push(now);
  HITS.set(ip, recent);
  if (HITS.size > 5000) HITS.clear();
  return recent.length > LIMIT;
}

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ code: "method" });
  }
  const apiKey = process.env.ANTHROPIC_API_KEY;
  const secret = process.env.REPORT_SECRET;
  if (!apiKey || !secret) return res.status(503).json({ code: "not_configured" });

  if (limited(req)) return res.status(429).json({ code: "rate_limited" });

  const body = req.body && typeof req.body === "object" ? req.body : {};
  const product = Object.prototype.hasOwnProperty.call(PRODUCTS, body.product) ? PRODUCTS[body.product] : null;
  const images = Array.isArray(body.images) ? body.images : [];
  const imagesOk = images.length <= 5 && images.every((s) => typeof s === "string" && s.length > 0 && s.length <= MAX_IMAGE_B64 && /^[A-Za-z0-9+/=]+$/.test(s));
  const input = product && imagesOk ? product.clean(body) : null;
  if (!input) return res.status(400).json({ code: "bad_input" });

  const content = images.map((data) => ({ type: "image", source: { type: "base64", media_type: "image/jpeg", data } }));
  content.push({ type: "text", text: product.prompt(input) });

  let reply;
  try {
    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "content-type": "application/json", "x-api-key": apiKey, "anthropic-version": "2023-06-01" },
      body: JSON.stringify({
        model: process.env.ANTHROPIC_MODEL || "claude-sonnet-5-5",
        max_tokens: 4000,
        temperature: 0,
        messages: [{ role: "user", content }],
      }),
    });
    if (r.status === 429) return res.status(429).json({ code: "rate_limited" });
    if (!r.ok) return res.status(502).json({ code: "server" });
    const data = await r.json();
    reply = (data.content || []).filter((b) => b.type === "text").map((b) => b.text).join("");
  } catch (err) {
    return res.status(502).json({ code: "server" });
  }

  let raw;
  try {
    raw = parseJson(reply);
  } catch (err) {
    return res.status(502).json({ code: "parse" });
  }
  if (raw.readable === false) return res.status(422).json({ code: "unreadable" });

  const report = product.normalise(raw, input);
  if (!product.valid(report)) return res.status(422).json({ code: "unreadable" });

  res.setHeader("Cache-Control", "no-store");
  return res.status(200).json({ teaser: product.teaser(report), sealed: seal({ product: body.product, report }, secret) });
};
