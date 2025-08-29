from collections import defaultdict
from knowledge_base import KNOWLEDGE_BASE, EMERGENCY_FLAGS, QUESTIONS

class InferenceEngine:
    def __init__(self, kb):
        self.kb = kb

    def evaluate_from_symptoms(self, symptom_list):
        facts = set(symptom_list)
        rule_matches = []
        scores = defaultdict(float)

        for condition, rules in self.kb.items():
            for rule in rules:
                reqs, w, explanation = rule
                if reqs.issubset(facts):
                    scores[condition] += w
                    rule_matches.append({"condition":condition, "rule":sorted(list(reqs)), "weight":w, "explanation":explanation})

        total = sum(scores.values())
        ranked = []
        if total > 0:
            for condition, sc in sorted(scores.items(), key=lambda x: x[1], reverse=True):
                ranked.append({"condition": condition, "confidence": min(1, sc / total)})
        advice = self._advice(facts, ranked)
        return {"ranked": ranked, "advice": advice, "facts": sorted(list(facts)), "rules_triggered": rule_matches}

    def evaluate_from_answers(self, answers):
        facts = set()
        for q in QUESTIONS:
            qid = q["id"]
            if q["type"] == "boolean":
                val = answers.get(qid, False)
                if isinstance(val, str):
                    val = val.lower() in ["true","yes","y","1"]
                if val:
                    facts.add(qid)
            elif q["type"] == "choice":
                val = answers.get(qid, "")
                if val and val != "none":
                    facts.add(val)
            elif q["type"] == "number":
                val = answers.get(qid, None)
                if val:
                    try:
                        v = float(val)
                        if qid == "fever_severity" and v >= 40:
                            facts.add("very_high_fever")
                    except:
                        pass
            elif q["type"] == "scale":
                val = answers.get(qid, None)
                if val:
                    try:
                        v = float(val)
                        if qid == "cough_severity" and v >= 7:
                            facts.add("cough_severity")
                    except:
                        pass
        return self.evaluate_from_symptoms(list(facts))

    def next_best_questions(self, facts, asked):
        order = [
            "blue_lips_or_face","confusion","oxygen_low","very_high_fever",
            "shortness_of_breath","fever","cough_type","cough_severity","hemoptysis",
            "duration_over_14d","night_sweats","weight_loss","exposure_tb","smoker","age_over_65"
        ]
        qmap = {q["id"]:q for q in QUESTIONS}
        candidates = []
        for qid in order:
            if qid in asked: continue
            if qid in facts: continue
            if qid in qmap:
                candidates.append(qmap[qid])
        return candidates

    def _advice(self, facts, ranked):
        if any(flag in facts for flag in EMERGENCY_FLAGS):
            return ("⚠️ Red-flag symptoms detected. Seek urgent medical care immediately.")

        if not ranked:
            return ("More information is needed. Answer follow-up questions about duration, cough type, severity, and any red flags.")

        top = ranked[0]["condition"]
        if top == "Community-acquired pneumonia":
            return ("Possible pneumonia — consider clinical evaluation, chest X-ray and antibiotics if bacterial; seek care urgently if breathing difficulty or low oxygen.")
        if top == "Tuberculosis (TB) suspicion":
            return ("Possible TB — see a clinician for testing (sputum microscopy/GeneXpert) and public health referral as needed.")
        if top == "COVID-19 / Viral LRI":
            return ("Possible viral LRI — follow local testing/isolation guidance and monitor oxygenation; seek care for worsening breathlessness.")
        return "Consult a healthcare professional for personalized care."
