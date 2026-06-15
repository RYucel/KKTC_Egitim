/* KGS Arşivi — geçmiş yıl KGS sınavlarını online çözme uygulaması.
   Tamamen istemci tarafı: PDF.js ile orijinal kitapçık görüntülenir,
   cevaplar localStorage'da saklanır, sonuç anında hesaplanır. */
"use strict";

pdfjsLib.GlobalWorkerOptions.workerSrc =
  "https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.worker.min.js";

const $ = (sel) => document.querySelector(sel);
const els = {
  home: $("#view-home"), exam: $("#view-exam"), result: $("#view-result"),
  list: $("#exam-list"), title: $("#exam-title"), timer: $("#timer"),
  start: $("#btn-start"), finish: $("#btn-finish"),
  pdfScroll: $("#pdf-scroll"), pageInd: $("#page-indicator"),
  zoomIn: $("#zoom-in"), zoomOut: $("#zoom-out"), zoomLabel: $("#zoom-label"),
  sheet: $("#sheet-pane"), sections: $("#sheet-sections"), progress: $("#answer-progress"),
  resultMain: $("#result-main"), resultTitle: $("#result-title"),
};

const DURATION = 90 * 60; // saniye
let DATA = null;
let current = null;        // aktif sınav
let state = null;          // {answers:{sec:[..]}, startedAt, remaining, finished}
let pdfDoc = null, zoom = 1.0, renderedPages = new Map(), pageObserver = null;
let timerInterval = null;
let reviewMode = false;

/* ---------------- localStorage ---------------- */
const storeKey = (id) => "kgs-state-" + id;
function loadState(id) {
  try { return JSON.parse(localStorage.getItem(storeKey(id))); } catch { return null; }
}
function saveState() {
  if (current && state) localStorage.setItem(storeKey(current.id), JSON.stringify(state));
}

/* ---------------- yardımcılar ---------------- */
function examName(e) {
  return `${e.year} KGS-${e.basamak} · ${e.oturum}. Oturum`;
}
function sectionNames(e) {
  return e.keys ? Object.keys(e.keys)
       : (e.oturum === 1 ? ["Türkçe", "Fen ve Teknoloji", "Sosyal Bilgiler"] : ["İngilizce", "Matematik"]);
}
function sectionLens(e) {
  if (e.keys) return Object.values(e.keys).map((k) => k.length);
  return e.oturum === 1 ? [27, 14, 10] : [22, 27];
}
function totalQuestions(e) { return sectionLens(e).reduce((a, b) => a + b, 0); }
function fmtTime(s) {
  const m = Math.floor(s / 60), ss = s % 60;
  return `${String(m).padStart(2, "0")}:${String(ss).padStart(2, "0")}`;
}

/* ---------------- Ana sayfa ---------------- */
function renderHome() {
  const byYear = {};
  for (const e of DATA.exams) (byYear[e.year] ||= []).push(e);
  const years = Object.keys(byYear).sort((a, b) => b - a);
  els.list.innerHTML = "";
  for (const y of years) {
    const g = document.createElement("div");
    g.className = "year-group";
    g.innerHTML = `<h2>${y}</h2>`;
    const cards = document.createElement("div");
    cards.className = "cards";
    for (const e of byYear[y].sort((a, b) => a.basamak - b.basamak || a.oturum - b.oturum)) {
      const st = loadState(e.id);
      const names = sectionNames(e).join(" · ");
      const card = document.createElement("div");
      card.className = "card";
      let badge = "";
      if (!e.keys) badge = `<span class="badge nokey">cevap anahtarı yok</span>`;
      else if (st?.finished) badge = `<span class="badge done">son puan: ${st.lastScore ?? "—"}</span>`;
      card.innerHTML = `
        <div class="name">KGS-${e.basamak} · ${e.oturum}. Oturum ${badge}</div>
        <div class="subjects">${names} — ${totalQuestions(e)} soru</div>
        <div class="row">
          <button class="btn primary small" data-act="solve">${st && !st.finished && Object.values(st.answers).some(a => a.some(x => x)) ? "Devam Et" : "Sınavı Çöz"}</button>
          <a class="btn ghost small" href="${e.pdf}" target="_blank" rel="noopener">PDF</a>
          ${e.answerSheet ? `<a class="btn ghost small" href="${e.answerSheet}" target="_blank" rel="noopener" title="Orijinal cevap anahtarı">Anahtar</a>` : ""}
        </div>`;
      card.querySelector("[data-act=solve]").addEventListener("click", () => openExam(e));
      cards.appendChild(card);
    }
    g.appendChild(cards);
    els.list.appendChild(g);
  }
}

/* ---------------- Ders kitapları ---------------- */
function renderBooks(data) {
  const host = $("#books");
  if (!host) return;
  if (!data || !data.subjects?.length) { host.hidden = true; return; }
  const subjects = data.subjects.map((s) => {
    const books = s.books.map((b) => `
      <div class="book-row">
        <span class="book-title">${b.title}</span>
        <span class="book-actions">
          <a class="btn ghost small" href="${b.url}" target="_blank" rel="noopener">Görüntüle</a>
          <a class="btn primary small" href="${b.url}" download target="_blank" rel="noopener">İndir</a>
        </span>
      </div>`).join("");
    return `
      <div class="book-card">
        <div class="book-head"><span class="book-icon">${s.icon || "📘"}</span><h3>${s.name}</h3></div>
        ${books}
      </div>`;
  }).join("");
  host.innerHTML = `
    <div class="books-inner">
      <h2 class="books-heading">📚 Ders Kitapları — ${data.grade}</h2>
      <p class="books-sub">${data.source} resmî ders kitapları. Tarayıcıda görüntüleyebilir veya indirebilirsiniz.</p>
      <div class="book-grid">${subjects}</div>
      ${data.note ? `<p class="books-note">${data.note}</p>` : ""}
    </div>`;
  host.hidden = false;
}

/* ---------------- Sınav Analizi ---------------- */
function renderAnalysis(data) {
  const host = $("#analysis");
  if (!host) return;
  if (!data || !data.charts?.length) { host.hidden = true; return; }

  const charts = data.charts.map((c) => `
    <figure class="analysis-chart">
      <a href="${c.src}" target="_blank" rel="noopener"><img src="${c.src}" alt="${c.title}" loading="lazy"></a>
      <figcaption><strong>${c.title}</strong> — ${c.caption}</figcaption>
    </figure>`).join("");

  const table = (t) => !t ? "" : `
    <div class="analysis-table-wrap">
      <table class="analysis-table">
        <caption>${t.caption}</caption>
        <thead><tr>${t.head.map((h) => `<th>${h}</th>`).join("")}</tr></thead>
        <tbody>${t.rows.map((r) => `<tr>${r.map((v, i) => `<td${i === 0 ? ' class="lbl"' : ""}>${v}</td>`).join("")}</tr>`).join("")}</tbody>
      </table>
    </div>`;

  const tips = (title, icon, arr) => `
    <div class="analysis-tips">
      <h4>${icon} ${title}</h4>
      <ul>${arr.map((t) => `<li>${t}</li>`).join("")}</ul>
    </div>`;

  const links = data.links?.length
    ? `<div class="analysis-links">${data.links.map((l) => `<a class="btn ghost small" href="${l.url}" target="_blank" rel="noopener">${l.label}</a>`).join("")}</div>`
    : "";

  host.innerHTML = `
    <div class="analysis-inner">
      <h2 class="analysis-heading">📊 ${data.title} <span class="analysis-period">${data.period}</span></h2>
      <p class="analysis-tldr">${data.tldr}</p>
      <details class="analysis-details">
        <summary>Ayrıntılı analizi görüntüle</summary>
        <p class="analysis-intro">${data.intro}</p>
        <div class="analysis-charts">${charts}</div>
        <div class="analysis-tables">${table(data.loadTable)}${table(data.successTable)}</div>
        <div class="analysis-tips-grid">
          ${tips("Öğrenciler için", "🎓", data.studentTips || [])}
          ${tips("Eğitimciler için", "🧑‍🏫", data.teacherTips || [])}
        </div>
        ${data.note ? `<p class="analysis-note">⚠️ ${data.note}</p>` : ""}
        ${links}
      </details>
    </div>`;
  host.hidden = false;
}

/* ---------------- Sınav görünümü ---------------- */
function show(view) {
  document.querySelectorAll("#app > .view").forEach((v) => { v.hidden = v !== view; });
  window.scrollTo(0, 0);
}

async function openExam(e) {
  current = e;
  reviewMode = false;
  state = loadState(e.id);
  const lens = sectionLens(e);
  const names = sectionNames(e);
  if (!state || state.finished) {
    state = {
      answers: Object.fromEntries(names.map((n, i) => [n, Array(lens[i]).fill(null)])),
      remaining: DURATION, startedAt: null, finished: false, lastScore: state?.lastScore ?? null,
    };
  }
  els.title.textContent = examName(e);
  els.start.hidden = !!state.startedAt;
  els.finish.hidden = !state.startedAt;
  els.timer.hidden = !state.startedAt;
  updateTimerLabel();
  buildSheet();
  show(els.exam);
  await loadPdf(e.pdf);
  if (state.startedAt) startTimer();
}

async function loadPdf(url) {
  els.pdfScroll.innerHTML = `<p style="color:#555">Kitapçık yükleniyor…</p>`;
  renderedPages.clear();
  if (pageObserver) pageObserver.disconnect();
  try {
    pdfDoc = await pdfjsLib.getDocument(encodeURI(url)).promise;
  } catch (err) {
    els.pdfScroll.innerHTML = `<p style="color:#c00">PDF yüklenemedi: ${err.message}</p>`;
    return;
  }
  els.pdfScroll.innerHTML = "";
  const canvases = [];
  for (let p = 1; p <= pdfDoc.numPages; p++) {
    const c = document.createElement("canvas");
    c.className = "pdf-page";
    c.dataset.page = p;
    els.pdfScroll.appendChild(c);
    canvases.push(c);
  }
  els.pageInd.textContent = `${pdfDoc.numPages} sayfa`;
  pageObserver = new IntersectionObserver((entries) => {
    for (const en of entries) {
      const p = Number(en.target.dataset.page);
      if (en.isIntersecting) {
        renderPage(p);
        els.pageInd.textContent = `Sayfa ${p} / ${pdfDoc.numPages}`;
      }
    }
  }, { root: els.pdfScroll, rootMargin: "300px 0px" });
  canvases.forEach((c) => pageObserver.observe(c));
  // ilk sayfanın genişliğine göre "sayfaya sığdır" ölçeği
  const page1 = await pdfDoc.getPage(1);
  const vw = els.pdfScroll.clientWidth - 40;
  zoom = Math.min(1.4, Math.max(0.5, vw / page1.getViewport({ scale: 1 }).width));
  updateZoomLabel();
  renderPage(1);
}

async function renderPage(num) {
  const key = `${num}@${zoom}`;
  if (renderedPages.get(num) === key) return;
  renderedPages.set(num, key);
  const page = await pdfDoc.getPage(num);
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const vp = page.getViewport({ scale: zoom });
  const canvas = els.pdfScroll.querySelector(`canvas[data-page="${num}"]`);
  if (!canvas) return;
  canvas.width = Math.floor(vp.width * dpr);
  canvas.height = Math.floor(vp.height * dpr);
  canvas.style.width = vp.width + "px";
  canvas.style.height = vp.height + "px";
  const ctx = canvas.getContext("2d");
  await page.render({ canvasContext: ctx, viewport: vp, transform: dpr !== 1 ? [dpr, 0, 0, dpr, 0, 0] : null }).promise;
}

function rerenderAll() {
  renderedPages.clear();
  els.pdfScroll.querySelectorAll("canvas").forEach((c) => {
    const r = c.getBoundingClientRect();
    const sr = els.pdfScroll.getBoundingClientRect();
    if (r.bottom > sr.top - 400 && r.top < sr.bottom + 400) renderPage(Number(c.dataset.page));
  });
}
function updateZoomLabel() { els.zoomLabel.textContent = Math.round(zoom * 100) + "%"; }
els.zoomIn.addEventListener("click", () => { zoom = Math.min(2.5, zoom + 0.15); updateZoomLabel(); rerenderAll(); });
els.zoomOut.addEventListener("click", () => { zoom = Math.max(0.4, zoom - 0.15); updateZoomLabel(); rerenderAll(); });

/* ---------------- Cevap kâğıdı ---------------- */
function buildSheet() {
  els.sections.innerHTML = "";
  const names = sectionNames(current);
  const lens = sectionLens(current);
  names.forEach((name, si) => {
    const sec = document.createElement("div");
    sec.className = "section";
    sec.innerHTML = `<h3>${name}</h3>`;
    for (let q = 0; q < lens[si]; q++) {
      const row = document.createElement("div");
      row.className = "qrow";
      row.dataset.sec = name; row.dataset.q = q;
      const no = document.createElement("span");
      no.className = "qno"; no.textContent = q + 1;
      row.appendChild(no);
      for (const L of ["A", "B", "C", "D"]) {
        const b = document.createElement("button");
        b.className = "opt"; b.textContent = L;
        if (state.answers[name][q] === L) b.classList.add("sel");
        b.addEventListener("click", () => pick(name, q, L, row));
        row.appendChild(b);
      }
      sec.appendChild(row);
    }
    els.sections.appendChild(sec);
  });
  updateProgress();
}

function pick(sec, q, L, row) {
  if (state.finished || reviewMode) return;
  const cur = state.answers[sec][q];
  state.answers[sec][q] = cur === L ? null : L; // tekrar tıklayınca sil
  row.querySelectorAll(".opt").forEach((b) => b.classList.toggle("sel", b.textContent === state.answers[sec][q]));
  saveState();
  updateProgress();
}

function answeredCount() {
  return Object.values(state.answers).reduce((n, arr) => n + arr.filter(Boolean).length, 0);
}
function updateProgress() {
  els.progress.textContent = `${answeredCount()} / ${totalQuestions(current)}`;
}

/* ---------------- Zamanlayıcı ---------------- */
function startTimer() {
  clearInterval(timerInterval);
  els.timer.hidden = false;
  updateTimerLabel();
  timerInterval = setInterval(() => {
    state.remaining -= 1;
    if (state.remaining % 10 === 0) saveState();
    updateTimerLabel();
    if (state.remaining <= 0) { finishExam(true); }
  }, 1000);
}
function updateTimerLabel() {
  els.timer.textContent = fmtTime(Math.max(0, state.remaining));
  els.timer.classList.toggle("low", state.remaining <= 300);
}

els.start.addEventListener("click", () => {
  state.startedAt = Date.now();
  els.start.hidden = true; els.finish.hidden = false;
  saveState();
  startTimer();
});

els.finish.addEventListener("click", () => {
  const blank = totalQuestions(current) - answeredCount();
  if (blank > 0 && !confirm(`${blank} soru boş. Sınavı bitirmek istediğinize emin misiniz?`)) return;
  finishExam(false);
});

/* ---------------- Değerlendirme ---------------- */
function grade() {
  const out = { sections: [], correct: 0, wrong: 0, blank: 0, total: 0 };
  for (const [name, key] of Object.entries(current.keys)) {
    const ans = state.answers[name];
    let c = 0, w = 0, b = 0;
    const detail = [];
    for (let i = 0; i < key.length; i++) {
      const a = ans[i];
      if (!a) { b++; detail.push("e"); }
      else if (a === key[i]) { c++; detail.push("c"); }
      else { w++; detail.push("w"); }
    }
    out.sections.push({ name, key, ans, c, w, b, n: key.length, detail });
    out.correct += c; out.wrong += w; out.blank += b; out.total += key.length;
  }
  out.score = Math.round((out.correct / out.total) * 1000) / 10;
  return out;
}

function finishExam(auto) {
  clearInterval(timerInterval);
  if (!current.keys) { alert("Bu sınavın cevap anahtarı yayınlanmadığı için puanlama yapılamıyor."); return; }
  state.finished = true;
  const g = grade();
  state.lastScore = g.score;
  saveState();
  renderResult(g, auto);
  show(els.result);
}

function renderResult(g, auto) {
  els.resultTitle.textContent = examName(current) + " — Sonuç";
  const used = DURATION - Math.max(0, state.remaining);
  let html = `
    <div class="score-hero">
      ${auto ? `<p style="color:var(--red);font-weight:600">Süre doldu — sınav otomatik bitirildi.</p>` : ""}
      <div class="big">${g.score}</div>
      <div class="sub">100 üzerinden puan (doğru oranı) · Kullanılan süre: ${fmtTime(used)}</div>
    </div>
    <table class="result-table">
      <tr><th>Ders</th><th>Soru</th><th>Doğru</th><th>Yanlış</th><th>Boş</th><th>Başarı</th></tr>`;
  for (const s of g.sections) {
    html += `<tr><td>${s.name}</td><td>${s.n}</td><td style="color:var(--green);font-weight:700">${s.c}</td>
      <td style="color:var(--red);font-weight:700">${s.w}</td><td>${s.b}</td>
      <td>%${Math.round((s.c / s.n) * 100)}</td></tr>`;
  }
  html += `<tr><td><strong>Toplam</strong></td><td><strong>${g.total}</strong></td>
    <td><strong style="color:var(--green)">${g.correct}</strong></td>
    <td><strong style="color:var(--red)">${g.wrong}</strong></td>
    <td><strong>${g.blank}</strong></td><td><strong>%${Math.round((g.correct / g.total) * 100)}</strong></td></tr></table>`;
  for (const s of g.sections) {
    html += `<div class="qchips"><h3>${s.name}</h3><div class="chips">`;
    for (let i = 0; i < s.n; i++) {
      const cls = s.detail[i];
      const lbl = cls === "e" ? "—" : s.ans[i];
      html += `<span class="chip ${cls}" title="Soru ${i + 1}: cevabınız ${s.ans[i] ?? "boş"}, doğru ${s.key[i]}">${i + 1}<small>${lbl}→${s.key[i]}</small></span>`;
    }
    html += `</div></div>`;
  }
  html += `<p style="color:var(--muted);font-size:.8rem;margin-top:20px">Not: Resmî KGS puanı farklı bir istatistiksel yöntemle hesaplanır; buradaki puan yalnızca doğru cevap oranını gösterir.
    ${current.answerSheet ? ` Orijinal cevap anahtarı: <a href="${current.answerSheet}" target="_blank" rel="noopener">görüntüle</a>.` : ""}</p>`;
  els.resultMain.innerHTML = html;
}

/* İncele: kitapçığa dön, doğru/yanlış işaretli */
$("#btn-review").addEventListener("click", () => {
  reviewMode = true;
  els.start.hidden = true; els.finish.hidden = true; els.timer.hidden = true;
  buildSheet();
  // işaretle
  for (const [name, key] of Object.entries(current.keys)) {
    document.querySelectorAll(`.qrow[data-sec="${CSS.escape(name)}"]`).forEach((row) => {
      const q = Number(row.dataset.q);
      row.classList.add("review");
      const a = state.answers[name][q];
      if (a) row.classList.add(a === key[q] ? "correct" : "wrong");
      row.querySelectorAll(".opt").forEach((b) => {
        if (b.textContent === key[q]) b.classList.add("keymark");
      });
    });
  }
  show(els.exam);
});

$("#btn-retry").addEventListener("click", () => {
  localStorage.removeItem(storeKey(current.id));
  const score = state?.lastScore;
  openExam(current).then(() => { if (score != null) { state.lastScore = score; saveState(); } });
});

/* ---------------- Navigasyon ---------------- */
function goHome() {
  clearInterval(timerInterval);
  saveState();
  renderHome();
  show(els.home);
}
$("#btn-back").addEventListener("click", goHome);
$("#btn-back2").addEventListener("click", goHome);
$("#btn-sheet-toggle").addEventListener("click", () => els.sheet.classList.toggle("open"));

window.addEventListener("beforeunload", saveState);

/* ---------------- Başlat ---------------- */
fetch("data/exams.json")
  .then((r) => r.json())
  .then((d) => { DATA = d; renderHome(); })
  .catch((err) => {
    els.list.innerHTML = `<p style="color:#c00">Veri yüklenemedi: ${err.message}</p>`;
  });

fetch("data/books.json")
  .then((r) => r.json())
  .then((d) => renderBooks(d))
  .catch(() => { const h = $("#books"); if (h) h.hidden = true; });

fetch("data/analysis.json")
  .then((r) => r.json())
  .then((d) => renderAnalysis(d))
  .catch(() => { const h = $("#analysis"); if (h) h.hidden = true; });
