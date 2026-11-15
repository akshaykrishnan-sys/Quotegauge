"use strict";
// Run with: npm test
const assert = require("assert");
const { PRODUCTS, parseJson, cleanVehicle } = require("../lib/core");
const { seal, unseal } = require("../lib/seal");

const car = { year: "2017", make: "Honda", model: "Accord", zip: "30301" };

// Vehicle validation
assert.strictEqual(cleanVehicle({ ...car, zip: "3030" }), null);
assert.strictEqual(cleanVehicle({ ...car, year: "1890" }), null);
assert.strictEqual(cleanVehicle({ ...car, make: "Honda<script>", shop: "nonsense" }).make, "Hondascript");
assert.deepStrictEqual(parseJson('Here: {"a": 1} thanks'), { a: 1 });
assert.throws(() => parseJson("no json here"));

// 1. Checker
const C = PRODUCTS.check;
assert.strictEqual(C.clean({ vehicle: car }), null, "needs text or photo");
const ci = C.clean({ vehicle: car, text: "Brakes $689" });
assert.ok(C.prompt(ci).includes("2017 Honda Accord") && C.prompt(ci).includes("Brakes $689"));
const cr = C.normalise({
  summary: "s", script: "say this", labor_rate_low: 110, labor_rate_high: 160,
  items: [
    { name: "Brakes", quoted: 689, fair_low: 480, fair_high: 700 },
    { name: "Cabin filter", quoted: "$119.00", fair_low: 90, fair_high: 55 },
    { name: "Fuel cleaning", quoted: 229, fair_low: 90, fair_high: 150, needs_verification: true, questionable: true },
    { name: "No range", quoted: 50 },
  ],
});
assert.strictEqual(cr.items.length, 3, "line without a range dropped");
assert.deepStrictEqual(cr.items.map((i) => i.rating), ["fair", "above", "verify"]);
assert.strictEqual(cr.items[1].hi, 90, "swapped range corrected");
assert.strictEqual(cr.quoted, 1037);
assert.strictEqual(cr.over, 29, "verify lines are not counted as overcharge");
assert.strictEqual(cr.verdict, "mixed", "small overcharge plus a questionable line is not a clean 'fair'");
assert.strictEqual(cr.questioned, 229);
assert.strictEqual(C.normalise({ items: [{ name: "Brakes", quoted: 600, fair_low: 480, fair_high: 700 }] }).verdict, "fair");
assert.strictEqual(cr.flagged, 2);
assert.ok(C.valid(cr));
const ct = JSON.stringify(C.teaser(cr));
assert.ok(!ct.includes("say this") && !ct.includes('"lo"') && !ct.includes('"note"') && !ct.includes("rateLo"), "teaser leaks nothing paid");

// Vehicle can be left blank only when a document image is attached
assert.strictEqual(C.clean({ vehicle: {}, text: "Brakes $689" }), null, "typed estimate still needs the vehicle");
const cu = C.clean({ vehicle: { shop: "a national repair chain" }, images: ["x"] });
assert.ok(cu && cu.vehicle.unknown && C.prompt(cu).includes("Read the vehicle year"));
assert.strictEqual(C.clean({ vehicle: { year: "2017" }, images: ["x"] }), null, "partly filled vehicle is rejected");
assert.strictEqual(C.normalise({ vehicle_read: "2017 Honda Accord", items: [] }).vehicleRead, "2017 Honda Accord");

// 2. Comparator
const M = PRODUCTS.compare;
assert.strictEqual(M.clean({ vehicle: car, quotes: [{ text: "one" }] }), null, "needs two estimates");
assert.strictEqual(M.clean({ vehicle: car, quotes: [{ text: "a", image: true }, { text: "b" }], images: [] }), null, "image count must match");
const mi = M.clean({ vehicle: car, quotes: [{ label: "Joe's", text: "Pads $689" }, { text: "Pads $495" }, { text: "" }] });
assert.strictEqual(mi.quotes.length, 2);
assert.strictEqual(mi.quotes[1].label, "Estimate B");
assert.ok(M.prompt(mi).includes("Estimate 2 (Estimate B)"));
const mr = M.normalise({
  job: "Front brakes",
  quotes: [{ index: 1, total: 913, parts_total: 400, labor_total: 513, includes: ["rotors"], missing: [] }, { index: 2, total: 520, missing: ["Brake fluid flush"] }],
  value_ranking: [1, 2, 2, 9], best_reason: "More complete",
}, mi);
assert.strictEqual(mr.quotes[1].priceRank, 1);
assert.strictEqual(mr.quotes[0].valueRank, 1);
assert.strictEqual(mr.best, "Joe's");
assert.strictEqual(mr.spread, 393);
assert.ok(M.valid(mr));
const mt = JSON.stringify(M.teaser(mr));
assert.ok(!mt.includes("More complete") && !mt.includes("valueRank") && !mt.includes("Brake fluid flush"), "teaser leaks nothing paid");

// 3. Necessity
const N = PRODUCTS.need;
const ni = N.clean({ vehicle: { ...car, mileage: "84,000 mi", detail: "2.0T <Sport>" }, text: "Brake pads 3mm", symptoms: "squeal" });
assert.strictEqual(ni.vehicle.mileage, "84000");
assert.strictEqual(ni.vehicle.detail, "2.0T Sport");
assert.ok(N.prompt(ni).includes("about 84000 miles") && N.prompt(ni).includes("(2.0T Sport)"));
assert.strictEqual(C.clean({ vehicle: car, images: [1, 2, 3, 4] }), null, "at most three pages");
assert.ok(N.prompt(ni).includes("never \"later\""));
const nr = N.normalise({ items: [
  { name: "Front brake pads", what: "w", urgency: "now", why: "y", symptoms: ["squeal"], questions: ["show me"], second_opinion: false },
  { name: "Injector cleaning", urgency: "whenever" },
  { what: "no name" },
] });
assert.strictEqual(nr.items.length, 2);
assert.strictEqual(nr.items[1].urgency, "verify", "unknown urgency falls back to verify");
assert.deepStrictEqual(nr.counts, { now: 1, soon: 0, later: 0, verify: 1 });
const nt = JSON.stringify(N.teaser(nr));
assert.ok(!nt.includes("show me") && !nt.includes("urgency"), "teaser leaks nothing paid");

// Sealing
const sealed = seal({ product: "check", report: cr }, "secret-one");
assert.deepStrictEqual(unseal(sealed, "secret-one").report, cr);
assert.throws(() => unseal(sealed, "secret-two"));
assert.throws(() => unseal(sealed.slice(0, -4) + "AAAA", "secret-one"));
assert.throws(() => unseal(seal({}, "secret-one", -1000), "secret-one"));

console.log("All tests passed.");

// Payment verification
{
  process.env.DODO_PRODUCT_CHECK = "pdt_check";
  const dodo = require("../lib/dodo");
  const ref = dodo.reportRef("sealed-abc");
  const good = { status: "succeeded", metadata: { ref, product: "check" }, product_cart: [{ product_id: "pdt_check", quantity: 1 }] };
  const assert = require("assert");
  assert.strictEqual(dodo.checkPayment(good, { product: "check", ref }), null);
  assert.strictEqual(dodo.checkPayment({ ...good, status: "processing" }, { product: "check", ref }), "not_paid");
  assert.strictEqual(dodo.checkPayment({ ...good, refund_status: "full" }, { product: "check", ref }), "refunded");
  assert.strictEqual(dodo.checkPayment(good, { product: "check", ref: dodo.reportRef("other") }), "other_report");
  assert.strictEqual(dodo.checkPayment({ ...good, product_cart: [{ product_id: "pdt_x" }] }, { product: "check", ref }), "wrong_product");
  assert.strictEqual(dodo.checkPayment({ ...good, metadata: { ref, product: "need" } }, { product: "check", ref }), "other_report");
  console.log("Payment checks passed.");
}
