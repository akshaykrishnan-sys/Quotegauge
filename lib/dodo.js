"use strict";
// Dodo Payments (merchant of record). Creates hosted checkouts and confirms payments server-side.
// Env: DODO_API_KEY, DODO_MODE ("test" | "live"), DODO_PRODUCT_CHECK, DODO_PRODUCT_COMPARE, DODO_PRODUCT_NEED,
// DODO_PRODUCT_ANY, and for QuoteGauge Pro: DODO_PLAN_MONTHLY, DODO_PLAN_YEARLY (subscription products).
const crypto = require("crypto");

const PRODUCT_ENV = { check: "DODO_PRODUCT_CHECK", compare: "DODO_PRODUCT_COMPARE", need: "DODO_PRODUCT_NEED", any: "DODO_PRODUCT_ANY" };
const PLAN_ENV = { monthly: "DODO_PLAN_MONTHLY", yearly: "DODO_PLAN_YEARLY" };

function base() {
  return process.env.DODO_MODE === "live" ? "https://live.dodopayments.com" : "https://test.dodopayments.com";
}
function productId(product) {
  return process.env[PRODUCT_ENV[product]] || "";
}
function configured(product) {
  return !!(process.env.DODO_API_KEY && productId(product));
}
// Ties a payment to one report, so one payment can't open a different report.
function reportRef(sealed) {
  return crypto.createHash("sha256").update(String(sealed)).digest("hex").slice(0, 40);
}

async function call(method, path, body) {
  const r = await fetch(base() + path, {
    method,
    headers: { authorization: "Bearer " + process.env.DODO_API_KEY, "content-type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) {
    const err = new Error("dodo " + r.status);
    err.status = r.status;
    throw err;
  }
  return data;
}

async function createCheckout({ product, ref, returnUrl }) {
  const data = await call("POST", "/checkouts", {
    product_cart: [{ product_id: productId(product), quantity: 1 }],
    return_url: returnUrl,
    metadata: { ref, product },
    feature_flags: { redirect_immediately: true },
  });
  if (!data.checkout_url) throw new Error("no checkout url");
  return data.checkout_url;
}

// Returns null when the payment is fine for this report, or a short reason code when it isn't.
function checkPayment(payment, { product, ref }) {
  if (!payment || payment.status !== "succeeded") return "not_paid";
  if (payment.refund_status) return "refunded";
  const meta = payment.metadata || {};
  if (meta.ref !== ref || meta.product !== product) return "other_report";
  const cart = Array.isArray(payment.product_cart) ? payment.product_cart : [];
  if (!cart.some((i) => i && i.product_id === productId(product))) return "wrong_product";
  return null;
}

async function getPayment(paymentId) {
  return call("GET", "/payments/" + encodeURIComponent(paymentId));
}

// QuoteGauge Pro subscriptions
function planId(plan) {
  return Object.prototype.hasOwnProperty.call(PLAN_ENV, plan) ? process.env[PLAN_ENV[plan]] || "" : "";
}
function plansConfigured() {
  return !!(process.env.DODO_API_KEY && planId("monthly"));
}
async function createSubscriptionCheckout({ plan, returnUrl }) {
  const data = await call("POST", "/checkouts", {
    product_cart: [{ product_id: planId(plan), quantity: 1 }],
    return_url: returnUrl,
    metadata: { plan },
    feature_flags: { redirect_immediately: true },
  });
  if (!data.checkout_url) throw new Error("no checkout url");
  return data.checkout_url;
}
async function getSubscription(id) {
  return call("GET", "/subscriptions/" + encodeURIComponent(id));
}
// Null when the subscription grants Pro, otherwise a reason code.
function checkSubscription(sub) {
  if (!sub) return "not_found";
  const ours = [planId("monthly"), planId("yearly")].filter(Boolean);
  if (!ours.includes(sub.product_id)) return "wrong_product";
  if (sub.status !== "active") return "inactive";
  return null;
}
async function portalLink(customerId) {
  const data = await call("POST", "/customers/" + encodeURIComponent(customerId) + "/customer-portal/session", null);
  return data.link || data.url || null;
}

module.exports = { base, productId, configured, reportRef, createCheckout, checkPayment, getPayment,
  planId, plansConfigured, createSubscriptionCheckout, getSubscription, checkSubscription, portalLink };
