"use strict";
// POST /api/portal  { pass }  → { url } to Dodo's customer portal (cancel, change card, invoices).
const dodo = require("../lib/dodo");
const pass = require("../lib/pass");

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ code: "method" });
  }
  res.setHeader("Cache-Control", "no-store");
  const secret = process.env.REPORT_SECRET;
  if (!secret || !process.env.DODO_API_KEY) return res.status(503).json({ code: "not_configured" });
  const body = req.body && typeof req.body === "object" ? req.body : {};
  const member = pass.read(body.pass, secret);
  if (!member || !member.cid) return res.status(401).json({ code: "no_pass" });
  try {
    const url = await dodo.portalLink(member.cid);
    if (!url) throw new Error("no link");
    return res.status(200).json({ url });
  } catch (err) {
    return res.status(502).json({ code: "server" });
  }
};
