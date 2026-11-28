/* Under Par sign-up + waitlist forms → Zapier → Stripe Checkout */
(function () {
  function send(url, params) {
    var body = new URLSearchParams(params);
    var ok = false;
    try { ok = navigator.sendBeacon && navigator.sendBeacon(url, body); } catch (e) {}
    if (!ok) { try { fetch(url, { method: "POST", body: body, mode: "no-cors", keepalive: true }); } catch (e) {} }
  }
  function uid() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    return "up-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 10);
  }
  function collect(form) {
    var out = {};
    new FormData(form).forEach(function (v, k) { out[k] = String(v).trim(); });
    return out;
  }
  function showError(form, msg) {
    var el = form.querySelector(".form-error");
    el.textContent = msg || "";
    el.hidden = !msg;
  }

  // Multi-step sign-up survey
  document.querySelectorAll("form.up-signup").forEach(function (form) {
    var steps = form.querySelectorAll(".step");
    var dots = form.querySelectorAll(".progress li");
    var i = 0;
    function show(n) {
      i = n;
      steps.forEach(function (s, k) { s.hidden = k !== n; });
      dots.forEach(function (d, k) { d.classList.toggle("on", k <= n); });
      form.querySelector(".back").hidden = n === 0;
      form.querySelector(".next").hidden = n === steps.length - 1;
      form.querySelector(".submit").hidden = n !== steps.length - 1;
      showError(form, "");
      var top = form.getBoundingClientRect().top + window.scrollY - 110;
      if (window.scrollY > top) window.scrollTo({ top: top, behavior: "smooth" });
    }
    function valid(n) {
      var bad = null;
      steps[n].querySelectorAll("input[required], select[required], textarea[required]").forEach(function (f) {
        if (!bad && !f.checkValidity()) bad = f;
      });
      if (bad) { showError(form, bad.dataset.msg || "Please fill in the highlighted field."); bad.focus(); return false; }
      return true;
    }
    form.querySelector(".next").addEventListener("click", function () { if (valid(i)) show(i + 1); });
    form.querySelector(".back").addEventListener("click", function () { show(i - 1); });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!valid(i)) return;
      var data = collect(form);
      if (data.company) return; // spam trap
      delete data.company;
      var ref = uid();
      data.ref = ref;
      data.plan = form.dataset.plan;
      data.page = location.pathname;
      send(form.dataset.hook, data);
      try { sessionStorage.setItem("up_first_name", data.first_name || ""); } catch (e) {}
      var btn = form.querySelector(".submit");
      btn.disabled = true;
      btn.textContent = "Taking you to secure checkout…";
      var url = form.dataset.checkout + "?prefilled_email=" + encodeURIComponent(data.email) + "&client_reference_id=" + encodeURIComponent(ref);
      setTimeout(function () { location.href = url; }, 350);
    });
    show(0);
  });

  // Single-step waitlist
  document.querySelectorAll("form.up-waitlist").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var bad = null;
      form.querySelectorAll("[required]").forEach(function (f) { if (!bad && !f.checkValidity()) bad = f; });
      if (bad) { showError(form, bad.dataset.msg || "Please fill in the highlighted field."); bad.focus(); return; }
      var data = collect(form);
      if (data.company) return;
      delete data.company;
      data.page = location.pathname;
      send(form.dataset.hook, data);
      form.hidden = true;
      var done = document.getElementById(form.dataset.done);
      if (done) { done.hidden = false; done.querySelector(".who").textContent = data.first_name || "there"; done.scrollIntoView({ behavior: "smooth", block: "center" }); }
    });
  });

  // Welcome page personalisation
  var who = document.querySelector("[data-welcome-name]");
  if (who) { try { var n = sessionStorage.getItem("up_first_name"); if (n) who.textContent = ", " + n; } catch (e) {} }
  var planEl = document.querySelector("[data-welcome-plan]");
  if (planEl) { var p = new URLSearchParams(location.search).get("plan"); if (p === "annual") planEl.textContent = "Annual App Plan ($374/year)"; }
})();
