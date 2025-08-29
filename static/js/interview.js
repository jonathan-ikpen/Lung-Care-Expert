const stepper = document.getElementById("stepper");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const finishBtn = document.getElementById("finishBtn");
const resultPanel = document.getElementById("resultPanel");
const progressPct = document.getElementById("progressPct");

let current = 0;
const answers = {};

function renderStep(idx){
  const q = QUESTIONS[idx];
  let pct = 0;
  if (QUESTIONS.length > 1) {
    pct = Math.round((idx / (QUESTIONS.length - 1)) * 100);
  }
  progressPct.textContent = pct + "%";
  stepper.innerHTML = `
    <div class="progress"><div class="bar" style="width:${pct}%"></div></div>
    <div class="step">
      <h4>${q.text}</h4>
      ${renderInput(q)}
    </div>
    <div class="muted">Step ${idx+1} of ${QUESTIONS.length}</div>
  `;

  prevBtn.style.display = idx === 0 ? "none" : "inline-block";
  nextBtn.style.display = idx >= QUESTIONS.length-1 ? "none" : "inline-block";
  finishBtn.style.display = idx >= QUESTIONS.length-1 ? "inline-block" : "none";
}

function renderInput(q){
  if(q.type === "boolean"){
    const val = q.id in answers ? !!answers[q.id] : null;
    return `
      <div class="input-row">
        <label class="radio"><input type="radio" name="${q.id}" value="true" ${val===true?"checked":""}>Yes</label>
        <label class="radio"><input type="radio" name="${q.id}" value="false" ${val===false?"checked":""}>No</label>
        <label class="radio"><input type="radio" name="${q.id}" value="unknown">Not sure</label>
      </div>`;
  }
  if(q.type === "choice"){
    const options = q.options.map(o=>{
      const checked = answers[q.id]===o.value ? "checked":"";
      return `<label class="radio">
        <input type="radio" name="${q.id}" value="${o.value}" ${checked}>
        ${o.label}
      </label>`
    }).join("");
    return `<div class="input-row">${options}</div>`;
  }
  if(q.type === "number"){
    const val = q.id in answers ? answers[q.id] : "";
    return `<div><input class="range chat-input" type="number" min="${q.min||0}" max="${q.max||100}" name="${q.id}" value="${val}"></div>`;
  }
  if(q.type === "scale"){
    const val = q.id in answers ? answers[q.id] : 5;
    return `<div>
      <input type="range" class="range" min="${q.min||0}" max="${q.max||10}" name="${q.id}" value="${val}" oninput="this.nextElementSibling.value=this.value">
      <output>${val}</output>
    </div>`;
  }
  return "";
}

function collect(){
  const q = QUESTIONS[current];
  const els = Array.from(document.querySelectorAll(`input[name="${q.id}"]`));
  if(!els.length) return;
  if(els[0].type==="radio"){
    const chosen = els.find(e=>e.checked);
    if(chosen){
      if(q.type==="boolean"){
        answers[q.id] = chosen.value === "true";
      }else{
        answers[q.id] = chosen.value;
      }
    }
  }else{
    const el = document.querySelector(`[name="${q.id}"]`);
    if(el) answers[q.id] = el.value;
  }
}

prevBtn.addEventListener("click", ()=>{
  collect();
  if(current>0){ current--; renderStep(current); }
});

nextBtn.addEventListener("click", ()=>{
  collect();
  if(current < QUESTIONS.length-1){ current++; renderStep(current); }
});

finishBtn.addEventListener("click", async ()=>{
  collect();
  const res = await fetch("/diagnose", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({answers})
  });
  const data = await res.json();
  showResult(data);
});

function showResult(data){
  const {ranked, advice, facts, rules_triggered} = data;
  resultPanel.classList.remove("hidden");
  if(!ranked || !ranked.length){
    resultPanel.innerHTML = `<h3>No clear result</h3><p class="muted">${advice}</p><div class="muted">Facts: ${facts.join(", ")}</div>`;
    return;
  }
  const items = ranked.map(r=>`<li><div><strong>${r.condition}</strong><div class="meta">${Math.round(r.confidence*100)}% probable</div></div></li>`).join("");
  const rules = (rules_triggered||[]).map(rr=>`<div class="muted">${rr.condition}: ${rr.explanation} (matched: ${rr.rule.join(", ")})</div>`).join("");
  resultPanel.innerHTML = `
    <h3>Possible conditions</h3>
    <ul class="ranked">${items}</ul>
    <p class="muted">${advice}</p>
    <div style="margin-top:12px">${rules}</div>
    <div class="muted" style="margin-top:8px">Facts: ${facts.join(", ")}</div>
  `;
}


// Initial render: ensure QUESTIONS is defined and DOM is ready
if (typeof QUESTIONS !== 'undefined') {
  renderStep(current);
} else {
  window.addEventListener('DOMContentLoaded', function() {
    if (typeof QUESTIONS !== 'undefined') {
      renderStep(current);
    }
  });
}
