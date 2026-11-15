"use strict";
// POST /api/pay  { sealed }
// Starts a Dodo Payments checkout for the report in `sealed` and returns { url }.
// While PAYMENTS_LIVE is not "true" it returns { test: true } and the page opens reports for free.
const { unseal } = require("../lib/seal");
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
  const secret = process.env.REPORT_SECRET;
  if (!secret) return res.status(503).json({ code: "not_configured" });

  const body = req.body && typeof req.body === "object" ? req.body : {};
  if (typeof body.sealed !== "string" || body.sealed.length > 400000) return res.status(400).json({ code: "bad_input" });

  let payload;
  try {
    payload = unseal(body.sealed, secret);
  } catch (err) {
    return res.status(400).json({ code: "expired" });
  }

  if (process.env.PAYMENTS_LIVE !== "true") return res.status(200).json({ test: true });
  if (!dodo.configured(payload.product)) return res.status(503).json({ code: "not_configured" });

  try {
    const url = await dodo.createCheckout({ product: payload.product, ref: dodo.reportRef(body.sealed), returnUrl: siteUrl(req) + "/" });
    return res.status(200).json({ url });
  } catch (err) {
    return res.status(502).json({ code: "server" });
  }
};
