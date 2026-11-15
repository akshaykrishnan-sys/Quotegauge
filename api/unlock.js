"use strict";
// POST /api/unlock  { sealed }
// Opens the sealed full report. While PAYMENTS_LIVE is not "true" this is test
// mode and the report opens without payment. When payments go live, verify the
// payment with the provider here before returning the report.
const { PRODUCTS } = require("../lib/core");
const { unseal } = require("../lib/seal");

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ code: "method" });
  }
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

  if (process.env.PAYMENTS_LIVE === "true") {
    // TODO: verify body.paymentId with the payment provider's server API and confirm it is a
    // paid, unused order for PRODUCTS[payload.product].price before continuing.
    return res.status(402).json({ code: "payment_required", price: PRODUCTS[payload.product].price });
  }

  res.setHeader("Cache-Control", "no-store");
  return res.status(200).json({ product: payload.product, report: payload.report, test: true });
};
