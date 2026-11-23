"use strict";
// POST /api/subscribe  { plan: "monthly" | "yearly" }  → { url } (Dodo checkout) or { test: true }
const dodo = require("../lib/dodo");

function siteUrl(req) {
  if (process.env.SITE_URL) return process.env.SITE_URL.replace(/\/+$/, "");
  return "https://" + String(req.headers["x-forwarded-host"] || req.headers.host || "").split(",")[0].trim();
}

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ code: "method" });
  }
  res.setHeader("Cache-Control", "no-store");
  const body = req.body && typeof req.body === "object" ? req.body : {};
  const plan = ["monthly", "yearly", "team", "portfolio"].includes(body.plan) ? body.plan : null;
  if (!plan) return res.status(400).json({ code: "bad_input" });
  if (process.env.PAYMENTS_LIVE !== "true") return res.status(200).json({ test: true });
  if (!process.env.DODO_API_KEY || (!dodo.planId(plan) && !["team","portfolio"].includes(plan))) return res.status(503).json({ code: "not_configured" });
  try {
    const url = await dodo.createSubscriptionCheckout({ plan, returnUrl: siteUrl(req) + (plan === "team" || plan === "portfolio" ? "/property-managers?subscribed=1" : "/?pro=1") });
    return res.status(200).json({ url });
  } catch (err) {
    console.error("subscribe_fail", plan, err.status, err.detail);
    return res.status(502).json({ code: "server" });
  }
};
