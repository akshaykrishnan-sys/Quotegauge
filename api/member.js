"use strict";
// POST /api/member  { subscriptionId }  → { pass, plan, renews } when the Pro subscription is active.
// Used after checkout, to restore access on a new device, and to renew an expired pass.
const dodo = require("../lib/dodo");
const pass = require("../lib/pass");

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ code: "method" });
  }
  res.setHeader("Cache-Control", "no-store");
  const secret = process.env.REPORT_SECRET;
  if (!secret || !dodo.plansConfigured()) return res.status(503).json({ code: "not_configured" });
  const body = req.body && typeof req.body === "object" ? req.body : {};
  const id = typeof body.subscriptionId === "string" && /^[A-Za-z0-9_-]{4,80}$/.test(body.subscriptionId.trim()) ? body.subscriptionId.trim() : null;
  if (!id) return res.status(400).json({ code: "bad_input" });

  let sub;
  try {
    sub = await dodo.getSubscription(id);
  } catch (err) {
    return res.status(err.status === 404 ? 404 : 502).json({ code: err.status === 404 ? "not_found" : "server" });
  }
  const problem = dodo.checkSubscription(sub);
  if (problem) return res.status(402).json({ code: problem, status: sub && sub.status });
  const plan = sub.product_id === dodo.planId("yearly") ? "yearly" : "monthly";
  return res.status(200).json({ pass: pass.issue(sub, secret), plan, renews: sub.next_billing_date || null, cancelling: !!sub.cancel_at_next_billing_date });
};
