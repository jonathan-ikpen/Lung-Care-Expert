const chatWindow = document.getElementById("chatWindow");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const quickReplies = document.getElementById("quickReplies");

let state = {symptoms:[], asked:[]};
let lastFollowup = null;

function addMsg(text, who="bot", small=null, isHtml=false){
  const div = document.createElement("div");
  div.className = `msg ${who}`;
  if(isHtml){
    div.innerHTML = text;
  } else {
    div.textContent = text;
  }
  if(small){
    const sm = document.createElement("div");
    sm.className = "meta muted";
    sm.style.marginTop = "8px";
    sm.textContent = small;
    div.appendChild(sm);
  }
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function setQuickReplies(items, qid=null){
  quickReplies.innerHTML = "";
  if(!items || !items.length) return;
  items.forEach(it=>{
    const btn = document.createElement("button");
    btn.className = "quick-reply";
    btn.textContent = it;
    btn.addEventListener("click", ()=>{
      addMsg(it, "user");  // show label, not raw value
      sendChat(it, qid);
    });
    quickReplies.appendChild(btn);
  });
}

async function sendChat(text, qid=null){
  const res = await fetch("/api/chat", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({message:text, state, qid})
  });
  const data = await res.json();
  state = data.state || state;
  if(data.detectedSymptoms?.length){
    addMsg("Noted: " + data.detectedSymptoms.join(", "), "bot");
  }
  if(data.followup){
    addMsg(data.followup.text, "bot");
    const sugg = data.followup.suggestions || [];
    lastFollowup = data.followup;
    setQuickReplies(sugg, data.followup.id);
  } else {
    // Style possible conditions (if present)
    if(data.reply && data.reply.startsWith("Possible conditions:")){
      // Split conditions and advice if present
      let [cond, ...rest] = data.reply.split(". ");
      let advice = rest.join(". ");
      cond = cond.replace(/_/g, " ");
      let html = `<div style='margin-bottom:10px;'><strong>${cond}.</strong></div>`;
      if(advice) html += `<div class='muted' style='margin-bottom:10px;'>${advice}</div>`;
      addMsg(html, "bot", null, true);
    } else {
      addMsg(data.reply, "bot");
    }
    // Style explanations
    if(data.rules_triggered?.length){
      const expl = data.rules_triggered.map(r=>
        `<div style='margin-bottom:8px;'><strong>${r.condition}:</strong> <span>${r.explanation}</span><br><span class='muted' style='font-size:13px;'>Matched: <code>${r.rule.map(f=>f.replace(/_/g,' ')).join(", ")}</code></span></div>`
      ).join("");
      addMsg(`<div style='margin-top:8px;'>${expl}</div>`, "bot", "Rules triggered", true);
    }
    lastFollowup = null;
  }
}

chatForm.addEventListener("submit", (e)=>{
  e.preventDefault();
  const text = chatInput.value.trim();
  if(!text) return;
  addMsg(text, "user");
  chatInput.value = "";
  setQuickReplies([]);
  sendChat(text, lastFollowup ? lastFollowup.id : null);
});
