(function () {
  "use strict";
  var C = window.QGCore, P = C.PRODUCTS;
  var $ = function (id) { return document.getElementById(id); };
  var usd = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
  var inPreview = !!(window.claude && window.claude.use);
  var state = { product: "check", report: null, full: false, unlocked: false, sealed: null, vehicle: null };

  var COPY = {
    check: {
      step: "Estimate", go: "Check this estimate", busy: "Pricing every line (and squinting at \"shop supplies\")…",
      unlock: "Fair range for every line, local parts and labor benchmarks, questionable charges explained, and a negotiation script.",
      missing: "Add a photo of the estimate or type its lines."
    },
    compare: {
      step: "Estimates", go: "Compare these estimates", busy: "Lining the quotes up side by side…",
      unlock: "Parts and labor differences, what each estimate leaves out, the value ranking and a best-value recommendation.",
      missing: "Add at least two estimates, each as a photo or typed lines."
    },
    need: {
      step: "Repair list", go: "Check these repairs", busy: "Sorting the must-dos from the nice-to-haves…",
      unlock: "Urgency for every item, what each repair does, symptoms to look for, questions to ask and where a second inspection is worth it.",
      missing: "Add a photo of the inspection report or type the recommended repairs."
    },
    any: {
      step: "Quote", go: "Check this quote", busy: "Pricing every line (and every \"misc. materials\")…",
      unlock: "Fair range for every line, local labor and materials benchmarks, vague or padded charges explained, and a script for the provider.",
      missing: "Add a photo of the quote or type its lines."
    }
  };
  var CAT = { hvac: "Heating & air conditioning", roofing: "Roofing", plumbing: "Plumbing", electrical: "Electrical", appliance: "Appliance repair", remodel: "Remodeling / contractor", landscaping: "Landscaping / tree work", pest: "Pest control", moving: "Moving", autobody: "Auto body / collision", other: "Service quote" };
  var VERDICT = { fair: "Looks fair", mixed: "Mostly fair, but question some charges", above: "Above market", verify: "Needs verification" };
  var TAG = { fair: "Fair", above: "Above market", verify: "Needs verification" };
  var URG = { now: "Do now", soon: "Do soon", later: "Can wait", verify: "Verify first" };
  var SHOP = {}; SHOP[C.SHOPS[0]] = "Independent shop"; SHOP[C.SHOPS[1]] = "Dealership"; SHOP[C.SHOPS[2]] = "National chain";

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; });
  }
  function money(n) { return n == null ? "n/a" : usd.format(n); }
  function range(a, b) { return money(a) + "–" + money(b); }
  function ul(items) { return items.length ? "<ul>" + items.map(function (s) { return "<li>" + esc(s) + "</li>"; }).join("") + "</ul>" : "<p class=\"dim\">None listed</p>"; }

  /* Photos: shrink large phone pictures before sending */
  function shrink(file) {
    return new Promise(function (resolve, reject) {
      var url = URL.createObjectURL(file), img = new Image();
      img.onload = function () {
        var k = Math.min(1, 1600 / Math.max(img.width, img.height)), c = document.createElement("canvas");
        c.width = Math.round(img.width * k); c.height = Math.round(img.height * k);
        c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
        URL.revokeObjectURL(url);
        c.toBlob(function (b) { b ? resolve(b) : reject(new Error("x")); }, "image/jpeg", 0.85);
      };
      img.onerror = function () { URL.revokeObjectURL(url); reject(new Error("x")); };
      img.src = url;
    });
  }
  /* PDFs are turned into page images in the browser, up to three pages */
  var PDFJS = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/";
  function loadPdfJs() {
    if (window.pdfjsLib) return Promise.resolve(window.pdfjsLib);
    return new Promise(function (resolve, reject) {
      var s = document.createElement("script");
      s.src = PDFJS + "pdf.min.js";
      s.onload = function () { window.pdfjsLib.GlobalWorkerOptions.workerSrc = PDFJS + "pdf.worker.min.js"; resolve(window.pdfjsLib); };
      s.onerror = function () { reject(new Error("pdf")); };
      document.head.appendChild(s);
    });
  }
  function pdfPages(file, max) {
    return loadPdfJs().then(function (lib) {
      return file.arrayBuffer().then(function (buf) { return lib.getDocument({ data: buf }).promise; });
    }).then(function (doc) {
      var n = Math.min(doc.numPages, max), out = [];
      var next = function (i) {
        if (i > n) return out;
        return doc.getPage(i).then(function (page) {
          var vp = page.getViewport({ scale: 1 }), view = page.getViewport({ scale: Math.min(2, 1500 / Math.max(vp.width, vp.height)) });
          var c = document.createElement("canvas"); c.width = Math.round(view.width); c.height = Math.round(view.height);
          return page.render({ canvasContext: c.getContext("2d"), viewport: view }).promise.then(function () {
            return new Promise(function (res) { c.toBlob(res, "image/jpeg", 0.85); });
          });
        }).then(function (b) { if (b) out.push(b); return next(i + 1); });
      };
      return next(1);
    });
  }
  function take(input, f, maxPages) {
      var note = input.parentNode.querySelector(".file-note");
      input._blobs = []; if (note) note.hidden = true;
      if (!f) return Promise.resolve();
      var isPdf = f.type === "application/pdf" || /\.pdf$/i.test(f.name);
      return (isPdf ? pdfPages(f, maxPages || 3) : shrink(f).then(function (b) { return [b]; })).then(function (blobs) {
        if (!blobs.length) throw new Error("empty");
        input._blobs = blobs;
        if (note) { note.textContent = isPdf ? "PDF added (" + blobs.length + (blobs.length === 1 ? " page)" : " pages)") : "Photo added"; note.hidden = false; }
      }).catch(function () { showError(isPdf ? "That PDF couldn't be read. Add a photo or screenshot of it instead." : "That image couldn't be read. Try a JPG or PNG photo."); });
  }
  function wirePhoto(input, maxPages) { input.addEventListener("change", function () { take(input, input.files[0], maxPages); }); }
  function toBase64(blob) {
    return new Promise(function (resolve, reject) {
      var r = new FileReader();
      r.onload = function () { resolve(String(r.result).split(",")[1] || ""); };
      r.onerror = function () { reject(new Error("read")); };
      r.readAsDataURL(blob);
    });
  }

  /* Comparator slots */
  var EXAMPLES = [
    "Front brake pads and rotors (OEM) ... $689.00\nBrake fluid flush ................. $179.00\nShop supplies .....................  $45.00\n12 month warranty",
    "Front pads + rotors (aftermarket) . $495.00\nShop fee ..........................  $25.00\n90 day warranty"
  ];
  function addQuote(text) {
    var n = $("quotes").children.length;
    if (n >= 5) return;
    var d = document.createElement("div");
    d.className = "slot";
    d.innerHTML = "<div class=\"slot-head\"><span class=\"slot-n\">" + "ABCDE".charAt(n) + "</span><input type=\"text\" class=\"q-label\" id=\"q-label-" + n + "\" aria-label=\"Shop name for estimate " + (n + 1) + "\" placeholder=\"Shop name (optional)\" maxlength=\"40\"></div>" +
      "<div class=\"filebox\"><input type=\"file\" class=\"q-photo\" id=\"q-photo-" + n + "\" accept=\"image/*,application/pdf\" aria-label=\"Photo or PDF of estimate " + (n + 1) + "\"><span class=\"file-note\" hidden></span></div>" +
      "<textarea class=\"q-text\" id=\"q-text-" + n + "\" rows=\"4\" spellcheck=\"false\" aria-label=\"Typed lines for estimate " + (n + 1) + "\" placeholder=\"Or type the lines and prices\"></textarea>";
    $("quotes").appendChild(d);
    d.querySelector(".q-text").value = text || "";
    wirePhoto(d.querySelector(".q-photo"), 1);
    $("add-quote").hidden = $("quotes").children.length >= 5;
  }

  /* Steps and product switching */
  function showError(msg) { var el = $("form-error"); el.textContent = msg; el.hidden = false; }
  function setStep(n) {
    $("step-1").hidden = n !== 1; $("step-2").hidden = n !== 2;
    [1, 2, 3].forEach(function (i) { $("st-" + i).className = i === n ? "on" : (i < n ? "done" : ""); });
  }
  function setProduct(p) {
    state.product = p;
    ["check", "compare", "need", "any"].forEach(function (k) {
      $("tab-" + k).setAttribute("aria-selected", k === p ? "true" : "false");
      $("tab-" + k).tabIndex = k === p ? 0 : -1;
      $("in-" + k).hidden = k !== p;
    });
    $("st-1").textContent = COPY[p].step;
    $("check-btn").textContent = COPY[p].go;
    $("shop-field").hidden = p === "compare";
    $("st-2").textContent = p === "any" ? "Job details" : "Your car";
    $("car-fields").hidden = p === "any"; $("any-fields").hidden = p !== "any";
    $("form-error").hidden = true;
    if (!$("result").hidden) { $("result").hidden = true; $("quote-form").hidden = false; }
    setStep(1);
  }
  function vehicleNow() {
    var shop = document.querySelector("input[name=shop]:checked");
    return { year: $("car-year").value.trim(), make: $("car-make").value.trim(), model: $("car-model").value.trim(), zip: $("car-zip").value.trim(), shop: shop ? shop.value : C.SHOPS[0], detail: $("car-detail").value, mileage: $("car-mileage").value };
  }

  function collect() {
    var p = state.product, v = vehicleNow(), blobs = [], body = { vehicle: v };
    if (p === "check") { body.text = $("check-text").value; blobs = ($("check-photo")._blobs || []).slice(); }
    if (p === "need") {
      body.text = $("need-text").value; body.symptoms = $("need-symptoms").value;
      blobs = ($("need-photo")._blobs || []).slice();
    }
    if (p === "any") {
      body = { category: $("any-cat").value, zip: $("any-zip").value.trim(), provider: $("any-provider").value, text: $("any-text").value };
      blobs = ($("any-photo")._blobs || []).slice();
    }
    if (p === "compare") {
      body.quotes = [];
      Array.prototype.forEach.call($("quotes").children, function (slot) {
        var blob = (slot.querySelector(".q-photo")._blobs || [])[0], text = slot.querySelector(".q-text").value.trim();
        if (!blob && !text) return;
        if (blob) blobs.push(blob);
        body.quotes.push({ label: slot.querySelector(".q-label").value, text: text, image: !!blob });
      });
    }
    return { body: body, blobs: blobs };
  }

  /* Analysis: inside Claude's preview the page asks Claude directly; on its own domain it calls the site's server. */
  function analysePreview(input, blobs) {
    var prod = P[state.product];
    return window.claude.use("sample").then(function (sample) {
      if (!sample) throw { code: "unavailable" };
      return Promise.resolve(blobs.length && sample.limits ? sample.limits() : {}).then(function (lim) {
        if (blobs.length && !(lim && lim.images)) throw { code: "no_images" };
        var opts = { modelTier: "complex", cache: false };
        if (blobs.length) opts.images = blobs;
        return sample(prod.prompt(input), opts);
      });
    }).then(function (res) {
      var raw;
      try { raw = C.parseJson(res.text || ""); } catch (e) { throw { code: "parse" }; }
      if (raw.readable === false) throw { code: "unreadable" };
      var report = prod.normalise(raw, input);
      if (!prod.valid(report)) throw { code: "unreadable" };
      return { report: report, sealed: null, full: true };
    });
  }
  function analyseServer(body, blobs) {
    return Promise.all(blobs.map(toBase64)).then(function (b64) {
      var payload = Object.assign({ product: state.product }, body, { images: b64 });
      return fetch("/api/check", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(payload) });
    }).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) {
        if (!r.ok) throw { code: j.code || "server" };
        return { report: j.teaser, sealed: j.sealed, full: false };
      });
    });
  }

  /* Reports */
  function tag(cls, text) { return "<span class=\"tag " + cls + "\">" + esc(text) + "</span>"; }
  function lock(text) { return "<span class=\"lock\">" + esc(text) + "</span>"; }

  function renderCheck(r, open, any) {
    var h = "<div class=\"verdict " + r.verdict + "\"><span class=\"k\">Verdict</span><strong>" + VERDICT[r.verdict] + "</strong><p>" + esc(r.summary || (r.flagged + " of " + r.items.length + " lines need a second look.")) + "</p></div>";
    h += "<div class=\"figs\"><div><span class=\"k\">Quoted</span><b>" + money(r.quoted) + "</b></div><div><span class=\"k\">Fair range</span><b>" + (open ? range(r.lo, r.hi) : lock("$•••–$•••")) + "</b></div><div><span class=\"k\">Above market by</span><b>" + money(Math.max(0, r.over)) + "</b></div></div>";
    if (open && r.rateLo != null && r.rateHi != null) h += "<p class=\"bench\"><span class=\"k\">Local labor benchmark</span> " + range(r.rateLo, r.rateHi) + " per hour for this " + (any ? "trade" : "type of shop") + "</p>";
    h += "<div class=\"k sub\">Line by line · " + r.flagged + " of " + r.items.length + " flagged</div><div class=\"rows\">";
    h += r.items.map(function (it) {
      var m = tag(it.rating, TAG[it.rating]) + (it.questionable ? tag("q", "Questionable charge") : "");
      if (open && it.lo != null) {
        m += "<span>Fair: " + range(it.lo, it.hi) + "</span>";
        var b = [];
        if (it.hours != null) b.push(it.hours + " labor hr");
        if (it.pLo != null && it.pHi != null) b.push((any ? "materials " : "parts ") + range(it.pLo, it.pHi));
        if (b.length) m += "<span>" + esc(b.join(" · ")) + "</span>";
        if (it.note) m += "<span class=\"wide\">" + esc(it.note) + "</span>";
      } else m += lock("Fair: $•••–$•••");
      return "<div class=\"row\"><div class=\"row-name\">" + esc(it.name) + "</div><div class=\"row-num\">" + money(it.quoted) + "</div><div class=\"row-meta\">" + m + "</div></div>";
    }).join("") + "</div>";
    if (open && r.script) h += "<div class=\"k sub\">What to say to the " + (any ? "provider" : "shop") + "</div><pre class=\"script\" id=\"script-text\">" + esc(r.script) + "</pre>";
    if (open) h += "<p class=\"dim\">Confidence: " + esc(r.confidence) + ". " + esc(r.caveats) + "</p>";
    return h;
  }

  function renderCompare(r, open) {
    var h = "<div class=\"verdict fair\"><span class=\"k\">" + (open ? "Best value" : "Price spread") + "</span><strong>" + (open ? esc(r.best) : money(r.spread) + " apart") + "</strong><p>" + esc(open ? r.bestReason : (r.job ? "For: " + r.job + ". " : "") + "The cheapest estimate is not always the best value.") + "</p></div>";
    h += "<div class=\"rows\">" + r.quotes.map(function (q) {
      var m = q.priceRank === 1 ? tag("fair", "Lowest price") : "";
      if (open) {
        m += tag(q.valueRank === 1 ? "fair" : "q", "Value rank " + q.valueRank) + "<span>Parts " + money(q.parts) + " · Labor " + money(q.labor) + "</span>";
        if (q.note) m += "<span class=\"wide\">" + esc(q.note) + "</span>";
        m += "<div class=\"wide two\"><div><span class=\"k\">Includes</span>" + ul(q.includes) + "</div><div><span class=\"k\">Leaves out</span>" + ul(q.missing) + "</div></div>";
      } else m += lock("Value rank • · what it leaves out •••");
      return "<div class=\"row\"><div class=\"row-name\">" + esc(q.label) + "</div><div class=\"row-num\">" + money(q.total) + "</div><div class=\"row-meta\">" + m + "</div></div>";
    }).join("") + "</div>";
    if (open) {
      h += "<div class=\"k sub\">Differences that matter</div>" + ul(r.differences);
      if (r.caveats) h += "<p class=\"dim\">" + esc(r.caveats) + "</p>";
    }
    return h;
  }

  function renderNeed(r, open) {
    var c = r.counts, urgent = c.now + c.verify;
    var h = "<div class=\"verdict " + (c.now ? "above" : "fair") + "\"><span class=\"k\">" + r.items.length + " recommended repairs</span><strong>" + c.now + " to do now, " + c.later + " can wait</strong><p>" + esc(open && r.summary ? r.summary : urgent + " of " + r.items.length + " items are urgent or need evidence before you approve them.") + "</p></div>";
    h += "<div class=\"figs four\">" + ["now", "soon", "later", "verify"].map(function (k) { return "<div><span class=\"k\">" + URG[k] + "</span><b>" + c[k] + "</b></div>"; }).join("") + "</div><div class=\"rows\">";
    h += r.items.map(function (it) {
      if (!open) return "<div class=\"row\"><div class=\"row-name\">" + esc(it.name) + "</div><div class=\"row-num\"></div><div class=\"row-meta\">" + lock("Urgency ••• · questions to ask •••") + "</div></div>";
      var m = tag("u-" + it.urgency, URG[it.urgency]) + (it.second ? tag("q", "Get a second inspection") : "");
      m += "<span class=\"wide\">" + esc(it.what) + "</span><span class=\"wide\"><b>Why:</b> " + esc(it.why) + "</span>";
      m += "<div class=\"wide two\"><div><span class=\"k\">Symptoms you'd notice</span>" + ul(it.symptoms) + "</div><div><span class=\"k\">Ask the mechanic</span>" + ul(it.questions) + "</div></div>";
      return "<div class=\"row\"><div class=\"row-name\">" + esc(it.name) + "</div><div class=\"row-num\"></div><div class=\"row-meta\">" + m + "</div></div>";
    }).join("") + "</div>";
    if (open && r.caveats) h += "<p class=\"dim\">" + esc(r.caveats) + "</p>";
    return h;
  }

  function render() {
    var p = state.product, r = state.report, open = state.unlocked, v = state.vehicle, head;
    if (p === "any") {
      head = "<div class=\"rep-head\"><div><b>" + esc(r.jobRead || CAT[v.category] || "Your quote") + "</b><span>" + esc(CAT[v.category] || "") + " · " + esc(v.zip ? "ZIP " + v.zip : (r.locationRead || "Location not shown")) + "</span></div><span class=\"k\">" + esc(P[p].title) + "</span></div>";
    } else {
      var carName = v.unknown ? (r.vehicleRead || "Vehicle not shown on the estimate") : v.year + " " + v.make + " " + v.model;
      var place = v.unknown ? (r.locationRead || "Location not shown") : "ZIP " + v.zip;
      head = "<div class=\"rep-head\"><div><b>" + esc(carName) + "</b><span>" + esc(place) + (p === "compare" ? "" : " · " + esc(SHOP[v.shop])) + "</span></div><span class=\"k\">" + esc(P[p].title) + "</span></div>";
    }
    $("report").innerHTML = head + (p === "check" || p === "any" ? renderCheck(r, open, p === "any") : p === "compare" ? renderCompare(r, open) : renderNeed(r, open));
    $("r-unlock").hidden = open;
    $("unlock-copy").textContent = COPY[p].unlock;
    var price = "$" + P[p].price.toFixed(2), title, anchor;
    if (p === "check" || p === "any") {
      var avoid = (r.over || 0) + (r.questioned || 0);
      title = avoid > 0 ? "Up to " + money(avoid) + " of this estimate may be avoidable. See exactly where." : (r.flagged ? r.flagged + " lines need a closer look. See which, and what to ask." : "Looks fair. See the fair range for every line.");
      anchor = price + " to check a " + money(r.quoted) + (p === "any" ? " quote. " : " estimate. ");
    } else if (p === "compare") {
      title = "These estimates are " + money(r.spread) + " apart. See which is the best value.";
      anchor = price + " before you commit to one of them. ";
    } else {
      title = (r.counts.now + r.counts.verify) + " of " + r.items.length + " repairs are urgent or need evidence. See which ones.";
      anchor = price + " before you approve the work. ";
    }
    $("unlock-title").textContent = title;
    $("unlock-anchor").textContent = anchor + "Not useful? Full refund within 7 days.";
    $("unlock-btn").textContent = member() ? "Open my full report · Unlimited" : "Unlock my full report · " + price;
    $("pro-line").hidden = !!member();
    var alt = { check: [["compare", "Got a second quote? Compare them"], ["need", "Not sure you need it all? Check the repairs"]], compare: [["check", "Check one estimate line by line"], ["need", "Check whether the repairs are needed"]], need: [["check", "Check the prices on the estimate"], ["compare", "Compare estimates from other shops"]], any: [["any", "Check another quote"], ["check", "Got a car repair estimate? Check it"]] }[p];
    $("cross").innerHTML = alt.map(function (x) { return "<button type=\"button\" class=\"btn-quiet\" data-go=\"" + x[0] + "\">" + esc(x[1]) + "</button>"; }).join("");
    $("copy-btn").hidden = !(open && (p === "check" || p === "any") && r.script);
    $("fb-thanks").hidden = true; Array.prototype.forEach.call(document.querySelectorAll("[data-fb]"), function (b) { b.hidden = false; });
    try { localStorage.setItem("qg-last", JSON.stringify({ product: p, report: r, full: state.full, unlocked: open, sealed: state.sealed, vehicle: v, at: Date.now() })); } catch (e) {}
  }

  /* Usage events, on the live site only (Vercel Web Analytics) */
  var LIVE = !(window.claude && window.claude.use) && /^https?:$/.test(location.protocol) && !/claude/.test(location.hostname);
  if (LIVE) {
    window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
    var va = document.createElement("script"); va.defer = true; va.src = "/_vercel/insights/script.js"; document.head.appendChild(va);
    $("print-btn").hidden = false;
  }
  function track(name) { try { if (LIVE) window.va("event", { name: name, data: { product: state.product } }); } catch (e) {} }

  function setBusy(busy) {
    var b = $("check-btn");
    b.disabled = busy;
    b.innerHTML = busy ? "<span class=\"spin\"></span>" + COPY[state.product].busy : COPY[state.product].go;
  }

  /* Events */
  ["check", "compare", "need", "any"].forEach(function (k) { $("tab-" + k).addEventListener("click", function () { setProduct(k); }); });
  Array.prototype.forEach.call(document.querySelectorAll("[data-start]"), function (el) {
    el.addEventListener("click", function () { setProduct(el.getAttribute("data-start")); });
  });
  wirePhoto($("check-photo")); wirePhoto($("need-photo")); wirePhoto($("any-photo"));
  addQuote(""); addQuote("");
  $("add-quote").addEventListener("click", function () { addQuote(""); });

  try {
    var saved = JSON.parse(localStorage.getItem("qg-vehicle") || "null");
    if (saved) ["car-year", "car-make", "car-model", "car-zip"].forEach(function (k) { if (saved[k]) $(k).value = saved[k]; });
  } catch (e) {}

  $("next-btn").addEventListener("click", function () {
    $("form-error").hidden = true;
    var c = collect(), ok = state.product === "compare" ? (c.body.quotes || []).length >= 2 : !!(String(c.body.text || "").trim() || c.blobs.length);
    if (!ok) return showError(COPY[state.product].missing);
    $("car-hint").hidden = !c.blobs.length; $("any-hint").hidden = !c.blobs.length;
    setStep(2);
  });
  var EX = {
    check: "Front brake pads and rotors ... $689.00\nBrake fluid flush .............. $179.00\nEngine air filter ..............  $89.00\nCabin air filter ............... $119.00\nFuel system cleaning service ... $229.00\nShop supplies / disposal fee ...  $45.00",
    any: "Replace 3-ton AC condenser and evaporator coil ... $8,900\nRefrigerant (R-454B) recharge ................. $650\nNew thermostat, installed ...................... $425\nWhole-house duct cleaning ...................... $499\nPermit and disposal ............................ $275",
    need: "Front brake pads at 3 mm, recommend replacement\nBrake fluid flush\nSerpentine belt cracked, recommend replacement\nFuel injector cleaning service\nEngine air filter dirty\nRear shocks leaking, recommend replacement"
  };
  $("example-btn").addEventListener("click", function () {
    var p = state.product;
    if (p === "check") $("check-text").value = EX.check;
    else if (p === "need") $("need-text").value = EX.need;
    else if (p === "any") { $("any-text").value = EX.any; $("any-cat").value = "hvac"; $("any-zip").value = "30301"; }
    else Array.prototype.forEach.call($("quotes").children, function (slot, i) { if (EXAMPLES[i]) slot.querySelector(".q-text").value = EXAMPLES[i]; });
    $("car-year").value = "2017"; $("car-make").value = "Honda"; $("car-model").value = "Accord"; $("car-zip").value = "30301";
    $("next-btn").click();
  });
  /* Uploading from the top of the page drops the file straight into the check */
  function heroTake(f) {
    if (!f) return;
    setProduct("check"); $("tool").scrollIntoView({ block: "start" }); track("hero_upload");
    take($("check-photo"), f, 3).then(function () { if (($("check-photo")._blobs || []).length) { $("car-hint").hidden = false; setStep(2); } });
  }
  $("hero-file").addEventListener("change", function () { heroTake($("hero-file").files[0]); });
  ["dragenter", "dragover"].forEach(function (ev) { $("hero-upload").addEventListener(ev, function (e) { e.preventDefault(); $("hero-upload").classList.add("over"); }); });
  ["dragleave", "drop"].forEach(function (ev) { $("hero-upload").addEventListener(ev, function () { $("hero-upload").classList.remove("over"); }); });
  $("hero-upload").addEventListener("drop", function (e) { e.preventDefault(); var f = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]; if (f && /^(image\/|application\/pdf)/.test(f.type)) heroTake(f); });
  $("hero-upload").addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); $("hero-file").click(); } });
  $("cross").addEventListener("click", function (e) {
    var go = e.target && e.target.getAttribute && e.target.getAttribute("data-go");
    if (go) { setProduct(go); $("tool").scrollIntoView({ block: "start" }); }
  });
  $("back-btn").addEventListener("click", function () { $("form-error").hidden = true; setStep(1); });

  $("quote-form").addEventListener("submit", function (e) {
    e.preventDefault();
    if ($("step-2").hidden) { $("next-btn").click(); return; }
    $("form-error").hidden = true;
    var c = collect();
    var input = P[state.product].clean(Object.assign({}, c.body, { images: c.blobs }));
    if (!input) return showError(state.product === "any" ? "Choose what the quote is for and add the 5-digit ZIP code of the job" + (c.blobs.length ? ", or leave the ZIP blank and we'll read it from what you uploaded." : ".") : "Add your car's year, make, model and a 5-digit ZIP code" + (c.blobs.length ? ", or leave all four blank and we'll read them from what you uploaded." : "."));
    if (input.vehicle && !input.vehicle.unknown) { try { localStorage.setItem("qg-vehicle", JSON.stringify({ "car-year": input.vehicle.year, "car-make": input.vehicle.make, "car-model": input.vehicle.model, "car-zip": input.vehicle.zip })); } catch (e2) {} }
    setBusy(true); track("check_started");
    (inPreview ? analysePreview(input, c.blobs) : analyseServer(c.body, c.blobs)).then(function (out) {
      state.report = out.report; state.sealed = out.sealed; state.full = out.full; state.unlocked = false; state.vehicle = input.vehicle || { any: true, category: input.category, zip: input.zip };
      $("quote-form").hidden = true; $("result").hidden = false; setStep(3);
      render(); track("check_done");
      $("tool").scrollIntoView({ block: "start" });
    }).catch(function (err) {
      var code = err && err.code, msg = "The check didn't finish. Try again in a moment.";
      if (code === "unavailable" || code === "not_granted") msg = "The check can't run in this view. Open the page in Claude while signed in and allow it to ask Claude.";
      else if (code === "rate_limited") msg = "Too many checks in a short time. Wait a minute and try again.";
      else if (code === "no_images") msg = "Photos can't be read in this view. Type the lines instead.";
      else if (code === "unreadable") msg = "Nothing readable was found. Use a sharper photo, or type each line with its price.";
      else if (code === "parse") msg = "The result came back garbled. Run the check again.";
      else if (code === "bad_input") msg = "Some details are missing or too long. Check the form and try again.";
      else if (code === "not_configured") msg = "Checks aren't switched on for this site yet.";
      showError(msg);
    }).then(function () { setBusy(false); });
  });

  function unlockError(msg) { var el = $("unlock-error"); el.textContent = msg; el.hidden = false; }
  /* QuoteGauge Pro: a signed pass kept on this device, renewed from the subscription when it expires */
  function proSaved() { try { return JSON.parse(localStorage.getItem("qg-pro") || "null"); } catch (e) { return null; } }
  function member() { var m = proSaved(); return m && m.sid ? m : null; }
  function passExp(pass) { try { return JSON.parse(atob(pass.split(".")[0].replace(/-/g, "+").replace(/_/g, "/"))).exp || 0; } catch (e) { return 0; } }
  function post(url, data) {
    return fetch(url, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(data) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { if (!r.ok) { var e = new Error(url); e.code = j.code; e.status = r.status; throw e; } return j; }); });
  }
  function joinPro(sid) {
    return post("/api/member", { subscriptionId: sid }).then(function (j) {
      try { localStorage.setItem("qg-pro", JSON.stringify({ sid: sid, pass: j.pass, plan: j.plan, renews: j.renews })); } catch (e) {}
      showPro(); return j.pass;
    });
  }
  function freshPass() {
    var m = member();
    if (!m) return Promise.reject(new Error("no pro"));
    if (m.pass && passExp(m.pass) > Date.now() + 60e3) return Promise.resolve(m.pass);
    return joinPro(m.sid).catch(function (e) { if (e.status === 402 || e.status === 404) { try { localStorage.removeItem("qg-pro"); } catch (x) {} showPro(); } throw e; });
  }
  function showPro() {
    var m = member();
    $("pro-chip").hidden = !m; $("manage-btn").hidden = !m; $("restore-open").hidden = !!m;
    Array.prototype.forEach.call(document.querySelectorAll("[data-plan]"), function (b) { b.disabled = !!m; if (m) b.textContent = "You're on Pro"; });
  }
  function toast(msg) { var t = $("toast"); t.textContent = msg; t.hidden = false; clearTimeout(toast.t); toast.t = setTimeout(function () { t.hidden = true; }, 6000); }

  function openReport(paymentId, pass) {
    return fetch("/api/unlock", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ sealed: state.sealed, paymentId: paymentId || undefined, pass: pass || undefined }) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { if (!r.ok || !j.report) { var e = new Error("unlock"); e.code = j.code; throw e; } return j.report; }); })
      .then(function (report) { state.report = report; state.full = true; state.unlocked = true; render(); if (paymentId) track("unlock_paid"); });
  }
  function testDialog() {
    $("pay-continue").hidden = false;
    $("pay-text").textContent = "Payments aren't switched on yet, so no card is charged. Once they are, this step takes a $" + P[state.product].price.toFixed(2) + " payment and then opens the full report.";
    $("pay-dialog").showModal();
  }
  $("unlock-btn").addEventListener("click", function () {
    $("unlock-error").hidden = true; track("unlock_clicked");
    if (state.full || inPreview) { testDialog(); return; }
    if (member()) {
      freshPass().then(function (pass) { return openReport(null, pass); }).then(function () { track("unlock_pro"); })
        .catch(function () { unlockError("Your Pro membership couldn't be confirmed. Restore it from the Pricing section, or unlock this report on its own."); showPro(); render(); });
      return;
    }
    var b = $("unlock-btn"), label = b.textContent;
    b.disabled = true; b.textContent = "Opening secure checkout…";
    fetch("/api/pay", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ sealed: state.sealed }) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { if (!r.ok) { var e = new Error("pay"); e.code = j.code; throw e; } return j; }); })
      .then(function (j) {
        if (j.test) { b.disabled = false; b.textContent = label; testDialog(); return; }
        try { localStorage.setItem("qg-pending", JSON.stringify({ product: state.product, sealed: state.sealed, at: Date.now() })); } catch (e) {}
        location.href = j.url;
      })
      .catch(function (e) {
        b.disabled = false; b.textContent = label;
        unlockError(e.code === "expired" ? "This check is more than a week old. Run it again to unlock it." : "Checkout couldn't be opened. Please try again in a moment.");
      });
  });
  $("pay-cancel").addEventListener("click", function () { $("pay-dialog").close(); });
  $("pay-continue").addEventListener("click", function () {
    $("pay-dialog").close();
    if (state.full) { state.unlocked = true; render(); return; }
    openReport().catch(function () { unlockError("The full report couldn't be opened. Run the check again."); });
  });
  $("copy-btn").addEventListener("click", function () {
    var b = $("copy-btn");
    navigator.clipboard.writeText(state.report.script).then(function () { b.textContent = "Copied"; }).catch(function () { b.textContent = "Select the script and copy it"; });
    setTimeout(function () { b.textContent = "Copy script"; }, 2500);
  });
  $("again-btn").addEventListener("click", function () {
    $("result").hidden = true; $("quote-form").hidden = false; setStep(1);
    $("tool").scrollIntoView({ block: "start" });
  });

  $("copytext-btn").addEventListener("click", function () {
    var b = $("copytext-btn");
    navigator.clipboard.writeText($("report").innerText).then(function () { b.textContent = "Copied"; }).catch(function () { b.textContent = "Select the report and copy it"; });
    setTimeout(function () { b.textContent = "Copy report"; }, 2500);
  });
  $("print-btn").addEventListener("click", function () { window.print(); });

  /* Arrow keys move between the three checks */
  var ORDER = ["check", "compare", "need"];
  ORDER.forEach(function (k, i) {
    $("tab-" + k).addEventListener("keydown", function (e) {
      var d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
      if (!d) return;
      var n = ORDER[(i + d + 3) % 3]; setProduct(n); $("tab-" + n).focus();
    });
  });

  setProduct("check");

  /* Reopen the last report after a refresh */
  var last = null;
  try { last = JSON.parse(localStorage.getItem("qg-last") || "null"); } catch (e) {}
  if (last && last.report && P[last.product] && last.vehicle && Date.now() - last.at < 30 * 864e5) $("resume-btn").hidden = false;
  $("resume-btn").addEventListener("click", function () {
    try {
      setProduct(last.product);
      state.report = last.report; state.full = !!last.full; state.unlocked = !!last.unlocked; state.sealed = last.sealed || null; state.vehicle = last.vehicle;
      $("quote-form").hidden = true; $("result").hidden = false; setStep(3); render();
    } catch (e) { $("result").hidden = true; $("quote-form").hidden = false; $("resume-btn").hidden = true; setStep(1); }
  });

  /* Pro: plan buttons, restore, manage */
  Array.prototype.forEach.call(document.querySelectorAll("[data-plan]"), function (b) {
    b.addEventListener("click", function () {
      var plan = b.getAttribute("data-plan"), label = b.textContent;
      track("pro_clicked");
      if (inPreview) { $("pay-text").textContent = "Unlimited isn't switched on in this preview. On the live site this opens a secure checkout."; $("pay-continue").hidden = true; $("pay-dialog").showModal(); return; }
      b.disabled = true; b.textContent = "Opening secure checkout…";
      post("/api/subscribe", { plan: plan }).then(function (j) {
        if (j.test) { b.disabled = false; b.textContent = label; $("pay-text").textContent = "Payments aren't switched on yet, so Unlimited can't be bought today. Every full report opens free while the site is in test mode."; $("pay-continue").hidden = true; $("pay-dialog").showModal(); return; }
        location.href = j.url;
      }).catch(function () { b.disabled = false; b.textContent = label; toast("Checkout couldn't be opened. Please try again in a moment."); });
    });
  });
  $("restore-open").addEventListener("click", function () { $("restore-error").hidden = true; $("restore-dialog").showModal(); });
  $("restore-cancel").addEventListener("click", function () { $("restore-dialog").close(); });
  $("restore-go").addEventListener("click", function () {
    var id = $("restore-id").value.trim(), el = $("restore-error");
    if (!/^[A-Za-z0-9_-]{4,80}$/.test(id)) { el.textContent = "That doesn't look like a subscription ID. It starts with sub_."; el.hidden = false; return; }
    joinPro(id).then(function () { $("restore-dialog").close(); toast("Pro is active on this device."); if (!$("result").hidden && state.report) render(); })
      .catch(function (e) { el.textContent = e.code === "inactive" ? "That subscription isn't active. Renew it, or email us." : e.code === "not_configured" ? "Pro isn't switched on yet." : "We couldn't find an active Pro subscription with that ID."; el.hidden = false; });
  });
  $("manage-btn").addEventListener("click", function () {
    freshPass().then(function (pass) { return post("/api/portal", { pass: pass }); }).then(function (j) { location.href = j.url; })
      .catch(function () { toast("The subscription page couldn't be opened. Email hello@quotegauge.pro and we'll help."); });
  });
  $("pay-cancel").addEventListener("click", function () { $("pay-continue").hidden = false; });
  Array.prototype.forEach.call(document.querySelectorAll("[data-fb]"), function (b) {
    b.addEventListener("click", function () {
      var v = b.getAttribute("data-fb");
      try { if (LIVE) window.va("event", { name: "feedback", data: { product: state.product, answer: v, verdict: (state.report && state.report.verdict) || "" } }); } catch (e) {}
      Array.prototype.forEach.call(document.querySelectorAll("[data-fb]"), function (x) { x.hidden = true; });
      $("fb-thanks").textContent = v === "yes" ? "Thank you. It helps us get the next one right." : "Thanks for telling us. Email hello@quotegauge.pro with what was off and we'll look at it, and refund you if the report didn't help.";
      $("fb-thanks").hidden = false;
    });
  });
  showPro();

  /* Coming back from a Pro checkout */
  (function () {
    var q = new URLSearchParams(location.search), sid = q.get("subscription_id");
    if (!q.get("pro") || !sid) return;
    try { history.replaceState(null, "", location.pathname + location.hash); } catch (e) {}
    var tries = 0;
    (function attempt() {
      joinPro(sid).then(function () { toast("Welcome to QuoteGauge Unlimited. Every full report is now unlocked on this device."); track("pro_joined"); })
        .catch(function (e) { if (e.code === "inactive" && tries++ < 5) { setTimeout(attempt, 2500); return; } toast("We couldn't confirm your Pro subscription yet. Use Restore access with the ID from your receipt."); });
    })();
  })();

  /* Coming back from checkout: open the paid report */
  (function () {
    var q = new URLSearchParams(location.search), pid = q.get("payment_id");
    if (!pid) return;
    var status = q.get("status");
    try { history.replaceState(null, "", location.pathname + location.hash); } catch (e) {}
    if (!last || !last.report || !last.sealed) return;
    $("resume-btn").click();
    $("tool").scrollIntoView({ block: "start" });
    if (status && status !== "succeeded") { unlockError("The payment didn't go through, so you haven't been charged. You can try again."); return; }
    var tries = 0;
    (function attempt() {
      openReport(pid).then(function () { try { localStorage.removeItem("qg-pending"); } catch (e) {} }).catch(function (e) {
        if (e.code === "not_paid" && tries++ < 5) { setTimeout(attempt, 2500); return; }
        unlockError(e.code === "other_report" ? "That payment was for a different report." : "We couldn't confirm the payment yet. If you were charged, email us with your receipt and we'll send the full report.");
      });
    })();
  })();

  /* Links such as /#compare open the matching check */
  function fromHash() {
    var h = (location.hash || "").slice(1);
    if (P[h]) { setProduct(h); $("tool").scrollIntoView({ block: "start" }); }
  }
  window.addEventListener("hashchange", fromHash);
  fromHash();

  /* Scroll story: on wide screens the pinned estimate changes as each step reaches mid-screen */
  var story = $("story");
  if (story && "IntersectionObserver" in window && window.matchMedia("(min-width: 900px)").matches && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    story.classList.add("live"); story.setAttribute("data-step", "1");
    var stepEls = Array.prototype.slice.call(story.querySelectorAll(".step")), counted = false;
    var storyIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var n = en.target.getAttribute("data-step");
        story.setAttribute("data-step", n);
        stepEls.forEach(function (s) { s.classList.toggle("on", s === en.target); });
        if (n === "3" && !counted) {
          counted = true;
          var el = $("story-amt"), t0 = null;
          var tick = function (t) { if (!t0) t0 = t; var k = Math.min(1, (t - t0) / 800); el.textContent = "$" + Math.round(287 * k); if (k < 1) requestAnimationFrame(tick); };
          requestAnimationFrame(tick);
        }
      });
    }, { rootMargin: "-45% 0px -45% 0px" });
    stepEls.forEach(function (el) { storyIO.observe(el); });
  }

  /* Phone-width call to action, hidden while the tool itself is on screen */
  var sticky = $("sticky");
  if ("IntersectionObserver" in window) {
    /* Show the bar only when neither the hero button nor the tool is on screen, so there is one button at a time */
    var seen = {};
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { seen[en.target.id] = en.isIntersecting; });
      sticky.className = seen["hero-upload"] || seen.tool ? "sticky" : "sticky show";
    });
    io.observe($("tool")); io.observe($("hero-upload"));
  }

  /* Contact form: compose an email to us in the visitor's own mail app */
  var cf = $("contact-form");
  if (cf) cf.addEventListener("submit", function (e) {
    e.preventDefault();
    var n = $("c-name").value.trim(), m = $("c-email").value.trim(), t = $("c-msg").value.trim();
    var body = t + (n || m ? "\n\n" + n + (m ? " <" + m + ">" : "") : "");
    window.location.href = "mailto:hello@quotegauge.pro?subject=" + encodeURIComponent("QuoteGauge question" + (n ? " from " + n : "")) + "&body=" + encodeURIComponent(body);
    track("contact_send");
  });
})();
