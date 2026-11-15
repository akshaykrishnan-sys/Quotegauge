"use strict";
// Encrypts the full report so it can pass through the browser unread until the unlock step.
const crypto = require("crypto");

const key = (secret) => crypto.createHash("sha256").update(String(secret)).digest();

function seal(payload, secret, ttlMs = 7 * 24 * 60 * 60 * 1000) {
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv("aes-256-gcm", key(secret), iv);
  const body = Buffer.concat([cipher.update(JSON.stringify({ payload, exp: Date.now() + ttlMs }), "utf8"), cipher.final()]);
  return Buffer.concat([iv, cipher.getAuthTag(), body]).toString("base64url");
}

function unseal(sealed, secret) {
  const buf = Buffer.from(String(sealed), "base64url");
  if (buf.length < 29) throw new Error("bad seal");
  const decipher = crypto.createDecipheriv("aes-256-gcm", key(secret), buf.subarray(0, 12));
  decipher.setAuthTag(buf.subarray(12, 28));
  const data = JSON.parse(Buffer.concat([decipher.update(buf.subarray(28)), decipher.final()]).toString("utf8"));
  if (!data.exp || data.exp < Date.now()) throw new Error("expired");
  return data.payload;
}

module.exports = { seal, unseal };
