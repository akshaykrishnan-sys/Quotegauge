"use strict";
// A short-lived, signed QuoteGauge Pro pass. The page keeps it; the server re-checks the
// subscription with Dodo whenever the page renews it (at most every PASS_HOURS hours).
const crypto = require("crypto");
const PASS_HOURS = 24;

const sign = (body, secret) => crypto.createHmac("sha256", "qg-pass:" + String(secret)).update(body).digest("base64url");

function issue(sub, secret, now = Date.now()) {
  const body = Buffer.from(JSON.stringify({ sid: sub.subscription_id, cid: (sub.customer && sub.customer.customer_id) || "", exp: now + PASS_HOURS * 3600e3 })).toString("base64url");
  return body + "." + sign(body, secret);
}
// Returns the pass contents, or null when it is forged or expired.
function read(pass, secret, now = Date.now()) {
  if (typeof pass !== "string" || pass.length > 600) return null;
  const [body, mac] = pass.split(".");
  if (!body || !mac) return null;
  const want = Buffer.from(sign(body, secret)), got = Buffer.from(mac);
  if (want.length !== got.length || !crypto.timingSafeEqual(want, got)) return null;
  let data;
  try { data = JSON.parse(Buffer.from(body, "base64url").toString("utf8")); } catch (e) { return null; }
  if (!data || typeof data.exp !== "number" || data.exp < now) return null;
  return data;
}

module.exports = { issue, read, PASS_HOURS };
