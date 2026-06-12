/* Konu Testleri — müfredata (data/curriculum.json) dayalı mini testler.
   Sorular data/questions/<ders>.json dosyalarından gelir; istatistikler
   localStorage'da soru ID'sine bağlı tutulur (kgs-quiz-stats-v1).
   app.js'teki global $ ve show() kullanılır (script sırası: app.js → quiz.js). */
"use strict";

(() => {
  const QUIZ_LEN = 10;
  const STATS_KEY = "kgs-quiz-stats-v1";

  let CURRICULUM = null;
  const questionCache = new Map(); // subjectId -> questions[]
  let activeSubject = null;
  let quiz = null; // {subject, topic, questions, idx, correct, wrongList, answered}

  const qEls = {
    home: document.querySelector("#quiz-home"),
    topicsView: document.querySelector("#view-topics"),
    topicsTitle: document.querySelector("#topics-title"),
    topicsMain: document.querySelector("#topics-main"),
    quizView: document.querySelector("#view-quiz"),
    quizTitle: document.querySelector("#quiz-title"),
    quizProgress: document.querySelector("#quiz-progress"),
    quizMain: document.querySelector("#quiz-main"),
  };

  /* ---------------- istatistik ---------------- */
  function loadStats() {
    try { return JSON.parse(localStorage.getItem(STATS_KEY)) || {}; } catch { return {}; }
  }
  function recordAnswer(qid, ok) {
    const stats = loadStats();
    const s = stats[qid] || { c: 0, w: 0 };
    if (ok) s.c += 1; else s.w += 1;
    stats[qid] = s;
    localStorage.setItem(STATS_KEY, JSON.stringify(stats));
  }
  // konu ustalığı: en az bir kez doğru cevaplanan benzersiz soru oranı
  function topicMastery(questions, stats) {
    if (!questions.length) return null;
    const done = questions.filter((q) => stats[q.id]?.c > 0).length;
    return Math.round((done / questions.length) * 100);
  }

  /* ---------------- veri ---------------- */
  async function getQuestions(subjectId) {
    if (questionCache.has(subjectId)) return questionCache.get(subjectId);
    let qs = [];
    try {
      const r = await fetch(`data/questions/${subjectId}.json`);
      if (r.ok) qs = (await r.json()).questions || [];
    } catch { /* dosya yoksa boş havuz */ }
    questionCache.set(subjectId, qs);
    return qs;
  }

  /* ---------------- ana sayfa bölümü ---------------- */
  function renderQuizHome() {
    const cards = CURRICULUM.subjects.map((s) => {
      const nTopics = s.units.reduce((n, u) => n + u.topics.length, 0);
      return `
        <button class="subject-card" data-subject="${s.id}">
          <span class="subject-icon">${s.icon}</span>
          <span class="subject-name">${s.name}</span>
          <span class="subject-meta">${nTopics} konu</span>
        </button>`;
    }).join("");
    qEls.home.innerHTML = `
      <div class="quiz-home-inner">
        <h2 class="books-heading">🎯 Konu Testleri — 5. Sınıf</h2>
        <p class="books-sub">Resmî müfredat konularına göre kısa testler çözün, her soruda anında geri bildirim ve açıklama alın, konu konu ilerlemenizi takip edin.</p>
        <div class="subject-grid">${cards}</div>
      </div>`;
    qEls.home.hidden = false;
    qEls.home.querySelectorAll("[data-subject]").forEach((b) =>
      b.addEventListener("click", () => openSubject(b.dataset.subject)));
  }

  /* ---------------- konu listesi ---------------- */
  async function openSubject(subjectId) {
    const subj = CURRICULUM.subjects.find((s) => s.id === subjectId);
    if (!subj) return;
    activeSubject = subj;
    qEls.topicsTitle.textContent = `${subj.icon} ${subj.name} — Konu Testleri`;
    qEls.topicsMain.innerHTML = `<p style="color:#555;padding:20px">Sorular yükleniyor…</p>`;
    show(qEls.topicsView);
    const all = await getQuestions(subjectId);
    renderTopics(subj, all);
  }

  function renderTopics(subj, all) {
    const stats = loadStats();
    const byTopic = {};
    for (const q of all) (byTopic[q.topic] ||= []).push(q);
    let html = "";
    for (const unit of subj.units) {
      html += `<div class="unit-group"><h2>${unit.name}</h2>`;
      for (const t of unit.topics) {
        const qs = byTopic[t.id] || [];
        const mastery = topicMastery(qs, stats);
        const bar = mastery === null ? "" : `
          <div class="mastery"><div class="mastery-bar"><div class="mastery-fill${mastery === 100 ? " full" : ""}" style="width:${mastery}%"></div></div>
          <span class="mastery-label">%${mastery}</span></div>`;
        html += `
          <div class="topic-row">
            <div class="topic-info">
              <div class="topic-name">${t.name}</div>
              <div class="topic-meta">${qs.length ? qs.length + " soru" : "yakında"}</div>
              ${bar}
            </div>
            ${qs.length ? `<button class="btn primary small" data-topic="${t.id}">Test Çöz</button>` : ""}
          </div>`;
      }
      html += `</div>`;
    }
    qEls.topicsMain.innerHTML = html;
    qEls.topicsMain.querySelectorAll("[data-topic]").forEach((b) =>
      b.addEventListener("click", () => startQuiz(subj, b.dataset.topic, byTopic[b.dataset.topic])));
  }

  /* ---------------- test akışı ---------------- */
  function pickQuestions(pool) {
    const stats = loadStats();
    const shuffle = (a) => {
      for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
      }
      return a;
    };
    // SEÇİM: önce hiç doğru cevaplanmamışlar (yeni + yanlış bilinenler) öncelikli,
    // havuz büyükse her testte farklı 10 soru gelir.
    const fresh = shuffle(pool.filter((q) => !(stats[q.id]?.c > 0)));
    const rest = shuffle(pool.filter((q) => stats[q.id]?.c > 0));
    const picked = fresh.concat(rest).slice(0, QUIZ_LEN);
    // SIRA: seçilen sorular her testte rastgele sırada sunulur.
    return shuffle(picked);
  }

  function startQuiz(subj, topicId, pool) {
    const topic = subj.units.flatMap((u) => u.topics).find((t) => t.id === topicId);
    quiz = {
      subject: subj, topic,
      questions: pickQuestions(pool),
      idx: 0, correct: 0, wrongList: [], answered: false,
    };
    qEls.quizTitle.textContent = topic.name;
    show(qEls.quizView);
    renderQuestion();
  }

  function renderQuestion() {
    const q = quiz.questions[quiz.idx];
    quiz.answered = false;
    qEls.quizProgress.textContent = `${quiz.idx + 1} / ${quiz.questions.length}`;
    const passage = q.passage ? `<div class="passage">${q.passage}</div>` : "";
    const opts = ["A", "B", "C", "D"].map((L, i) => `
      <button class="quiz-opt" data-letter="${L}">
        <span class="opt-letter">${L}</span><span class="opt-text">${q.options[i]}</span>
      </button>`).join("");
    qEls.quizMain.innerHTML = `
      <div class="quiz-card">
        ${passage}
        <div class="quiz-q">${q.q}</div>
        <div class="quiz-opts">${opts}</div>
        <div class="quiz-feedback" id="quiz-feedback" hidden></div>
        <div class="quiz-nav"><button class="btn primary" id="btn-next" hidden></button></div>
      </div>`;
    qEls.quizMain.querySelectorAll(".quiz-opt").forEach((b) =>
      b.addEventListener("click", () => answer(b, q)));
    document.querySelector("#btn-next").addEventListener("click", next);
  }

  function answer(btn, q) {
    if (quiz.answered) return;
    quiz.answered = true;
    const picked = btn.dataset.letter;
    const ok = picked === q.answer;
    recordAnswer(q.id, ok);
    if (ok) quiz.correct += 1;
    else quiz.wrongList.push({ q, picked });
    qEls.quizMain.querySelectorAll(".quiz-opt").forEach((b) => {
      b.disabled = true;
      if (b.dataset.letter === q.answer) b.classList.add("correct");
      else if (b === btn) b.classList.add("wrong");
    });
    const fb = document.querySelector("#quiz-feedback");
    fb.hidden = false;
    fb.className = "quiz-feedback " + (ok ? "ok" : "no");
    fb.innerHTML = `<strong>${ok ? "✓ Doğru!" : `✗ Yanlış — doğru cevap ${q.answer}`}</strong><p>${q.explanation}</p>`;
    const nextBtn = document.querySelector("#btn-next");
    nextBtn.hidden = false;
    nextBtn.textContent = quiz.idx + 1 < quiz.questions.length ? "Sonraki Soru →" : "Sonucu Gör";
    nextBtn.focus();
  }

  function next() {
    if (quiz.idx + 1 < quiz.questions.length) {
      quiz.idx += 1;
      renderQuestion();
      qEls.quizMain.scrollTop = 0;
      window.scrollTo(0, 0);
    } else {
      renderSummary();
    }
  }

  function renderSummary() {
    const n = quiz.questions.length;
    const pct = Math.round((quiz.correct / n) * 100);
    qEls.quizProgress.textContent = "";
    let wrongs = "";
    if (quiz.wrongList.length) {
      wrongs = `<h3>Yanlış cevaplananlar</h3>` + quiz.wrongList.map(({ q, picked }) => `
        <div class="wrong-item">
          ${q.passage ? `<div class="passage small">${q.passage}</div>` : ""}
          <div class="wrong-q">${q.q}</div>
          <div class="wrong-detail">Senin cevabın: <span class="no">${picked}</span> · Doğrusu: <span class="ok">${q.answer}) ${q.options["ABCD".indexOf(q.answer)]}</span></div>
          <div class="wrong-expl">${q.explanation}</div>
        </div>`).join("");
    }
    qEls.quizMain.innerHTML = `
      <div class="quiz-card summary">
        <div class="score-hero">
          <div class="big">${quiz.correct} / ${n}</div>
          <div class="sub">%${pct} başarı — ${quiz.topic.name}</div>
        </div>
        ${wrongs}
        <div class="quiz-nav">
          <button class="btn primary" id="btn-again">Tekrar Çöz</button>
          <button class="btn ghost" id="btn-topics">Konulara Dön</button>
        </div>
      </div>`;
    document.querySelector("#btn-again").addEventListener("click", async () => {
      const pool = (await getQuestions(quiz.subject.id)).filter((x) => x.topic === quiz.topic.id);
      startQuiz(quiz.subject, quiz.topic.id, pool);
    });
    document.querySelector("#btn-topics").addEventListener("click", backToTopics);
  }

  async function backToTopics() {
    if (activeSubject) openSubject(activeSubject.id); // ustalık çubukları tazelensin
  }

  /* ---------------- navigasyon ---------------- */
  document.querySelector("#btn-topics-back").addEventListener("click", () => {
    show(document.querySelector("#view-home"));
  });
  document.querySelector("#btn-quiz-exit").addEventListener("click", () => {
    if (quiz && quiz.idx + 1 < quiz.questions.length &&
        !confirm("Test yarıda kalacak. Çıkmak istediğine emin misin?")) return;
    backToTopics();
  });

  /* ---------------- başlat ---------------- */
  fetch("data/curriculum.json")
    .then((r) => r.json())
    .then((d) => { CURRICULUM = d; renderQuizHome(); })
    .catch(() => { qEls.home.hidden = true; });
})();
