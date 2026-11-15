"use strict";
// POST /api/unlock  { sealed, paymentId } or { sealed, pass } for QuoteGauge Pro members
// Opens the sealed full report. While PAYMENTS_LIVE is not "true" this is test mode and the
// report opens without payment. When live, the payment is confirmed with Dodo Payments first:
// it must have succeeded, not been refunded, and have been made for this exact report.
const { unseal } = require("../lib/seal");
const dodo = require("../lib/dodo");
const pass = require("../lib/pass");

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

  if (process.env.PAYMENTS_LIVE !== "true") {
    return res.status(200).json({ product: payload.product, report: payload.report, test: true });
  }

  if (body.pass) {
    if (!pass.read(body.pass, secret)) return res.status(401).json({ code: "pass_expired" });
    return res.status(200).json({ product: payload.product, report: payload.report, pro: true });
  }

  const paymentId = typeof body.paymentId === "string" && /^[A-Za-z0-9_-]{4,80}$/.test(body.paymentId) ? body.paymentId : null;
  if (!paymentId) return res.status(402).json({ code: "payment_required" });
  if (!dodo.configured(payload.product)) return res.status(503).json({ code: "not_configured" });

  let payment;
  try {
    payment = await dodo.getPayment(paymentId);
  } catch (err) {
    return res.status(err.status === 404 ? 402 : 502).json({ code: err.status === 404 ? "not_paid" : "server" });
  }
  const problem = dodo.checkPayment(payment, { product: payload.product, ref: dodo.reportRef(body.sealed) });
  if (problem) return res.status(402).json({ code: problem });

  return res.status(200).json({ product: payload.product, report: payload.report });
};
