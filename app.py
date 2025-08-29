from flask import Flask, render_template, request, jsonify
from inference_engine import InferenceEngine
from knowledge_base import KNOWLEDGE_BASE, QUESTIONS, SYMPTOM_SYNONYMS
import re

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
engine = InferenceEngine(KNOWLEDGE_BASE)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/interview")
def interview():
    return render_template("interview.html", questions=QUESTIONS)

@app.route("/diagnose", methods=["POST"])
def diagnose():
    data = request.get_json() or {}
    answers = data.get("answers", {})
    result = engine.evaluate_from_answers(answers)
    return jsonify(result)

@app.route("/chat")
def chat():
    return render_template("chatbot.html")

@app.route("/api/chat", methods=["POST"])
def api_chat():
    payload = request.get_json() or {}
    user_message = payload.get("message", "").strip()
    session_state = payload.get("state", {})
    detected = set()
    text = user_message.lower()

    # extract symptoms using synonyms
    for symptom, patterns in SYMPTOM_SYNONYMS.items():
        for p in patterns:
            if re.search(rf"\\b{re.escape(p)}\\b", text):
                detected.add(symptom)
                break

    stated_symptoms = set(session_state.get("symptoms", []))
    stated_symptoms |= detected

    ask_for_result = any(k in text for k in ["diagnose","result","what is it","what could it be","summary","possible","likely"])

    followups = engine.next_best_questions(stated_symptoms, asked=set(session_state.get("asked", [])))
    response_text = ""
    if ask_for_result or not followups:
        scores = engine.evaluate_from_symptoms(list(stated_symptoms))
        top = scores.get("ranked", [])[:4]
        if not top:
            response_text = "I need more information. Tell me more symptoms or answer a few quick questions."
        else:
            response_text = "Possible conditions: " + ", ".join(f"{c['condition']} ({int(round(c['confidence']*100))}%)" for c in top) + "."
            response_text += " " + scores.get("advice","")
        return jsonify({
            "reply": response_text,
            "state": {"symptoms": sorted(list(stated_symptoms)), "asked": list(session_state.get("asked", []))},
            "detectedSymptoms": sorted(list(detected)),
            "rules_triggered": scores.get("rules_triggered", [])
        })
    else:
        q = followups[0]
        suggestions = []
        if q["type"] == "boolean":
            suggestions = ["Yes","No","Not sure"]
        elif q["type"] == "choice":
            suggestions = [o["label"] for o in q.get("options",[])]
        elif q["type"] == "scale":
            suggestions = ["0","3","5","7","10"]
        # mark asked and update state
        asked = set(session_state.get("asked", []))
        asked.add(q["id"])
        session_state["asked"] = list(asked)
        session_state["symptoms"] = list(stated_symptoms)
        return jsonify({"reply":"","followup":{"id":q["id"],"text":q["text"],"type":q["type"],"suggestions":suggestions},"state":session_state,"detectedSymptoms":sorted(list(detected))})

if __name__ == "__main__":
    app.run(debug=True)
