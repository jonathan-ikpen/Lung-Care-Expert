# Expanded IF-THEN knowledge base for lung infection triage.
# Educational prototype — not a medical device.

SYMPTOMS = [
    "fever","low_grade_fever","very_high_fever","cough","dry_cough","productive_cough",
    "shortness_of_breath","exertional_dyspnea","chest_pain","chills","fatigue","wheezing",
    "sore_throat","runny_nose","headache","night_sweats","weight_loss","loss_of_appetite",
    "hemoptysis","recent_cold_or_flu","exposure_tb","smoker","age_over_65","duration_over_7d",
    "duration_over_14d","blue_lips_or_face","confusion","tachypnea","tachycardia","oxygen_low","cough_severity"
]

SYMPTOM_SYNONYMS = {
    "fever":["fever","feverish","temperature"],
    "very_high_fever":["40c","104f","very high fever","high fever 40"],
    "dry_cough":["dry cough","unproductive cough"],
    "productive_cough":["productive cough","wet cough","phlegm","sputum"],
    "shortness_of_breath":["shortness of breath","dyspnea","breathless","can't breathe"],
    "exertional_dyspnea":["breathless when walking","can't walk far","short of breath on exertion"],
    "chest_pain":["chest pain","chest tightness","pleuritic pain"],
    "night_sweats":["night sweats","sweating at night"],
    "weight_loss":["weight loss","lost weight","losing weight"],
    "hemoptysis":["coughing blood","blood in sputum","hemoptysis"],
    "exposure_tb":["tb exposure","contact with tb","around tb"],
    "smoker":["smoker","i smoke","smoking"],
    "age_over_65":["over 65","elderly","senior"],
    "blue_lips_or_face":["blue lips","cyanosis","bluish face"],
    "confusion":["confused","disoriented","hard to wake"],
    "oxygen_low":["low oxygen","spo2 low","oxygen saturation low"],
    "duration_over_7d":["over a week","more than 7 days"],
    "duration_over_14d":["more than 14 days","two weeks"],
    "cough_severity":["severe cough","cough 8","cough 9","cough 10"]
}

QUESTIONS = [
    {"id":"fever","text":"Do you have a fever?", "type":"boolean"},
    {"id":"fever_severity","text":"If yes, what's the approximate temperature (°C)?", "type":"number", "min":34, "max":43},
    {"id":"cough_type","text":"Which cough best describes yours?", "type":"choice","options":[{"value":"none","label":"No cough"},{"value":"dry_cough","label":"Dry cough"},{"value":"productive_cough","label":"Productive (with phlegm)"}]},
    {"id":"cough_severity","text":"Rate your cough severity 0 (none) to 10 (worst)", "type":"scale", "min":0, "max":10},
    {"id":"shortness_of_breath","text":"Do you have shortness of breath?", "type":"boolean"},
    {"id":"exertional_dyspnea","text":"Is breathlessness worse on exertion (e.g., walking)?", "type":"boolean"},
    {"id":"chest_pain","text":"Any chest pain or tightness?", "type":"boolean"},
    {"id":"hemoptysis","text":"Have you coughed up blood?", "type":"boolean"},
    {"id":"fatigue","text":"Unusual tiredness or fatigue?", "type":"boolean"},
    {"id":"night_sweats","text":"Night sweats?", "type":"boolean"},
    {"id":"weight_loss","text":"Unintentional weight loss recently?", "type":"boolean"},
    {"id":"duration_over_7d","text":"Symptoms for more than 7 days?", "type":"boolean"},
    {"id":"duration_over_14d","text":"Symptoms for more than 14 days?", "type":"boolean"},
    {"id":"exposure_tb","text":"Known exposure to TB?", "type":"boolean"},
    {"id":"smoker","text":"Do you currently smoke?", "type":"boolean"},
    {"id":"age_over_65","text":"Are you aged 65 or older?", "type":"boolean"},
    {"id":"blue_lips_or_face","text":"Blue lips/face or severe breathing difficulty?", "type":"boolean"},
    {"id":"confusion","text":"Are you confused or hard to wake?", "type":"boolean"},
    {"id":"oxygen_low","text":"Do you have a measured low oxygen reading (SpO2)?", "type":"boolean"},
]

# Each rule tuple: (set_of_required_facts, weight, explanation)
KNOWLEDGE_BASE = {
    "Community-acquired pneumonia":[
        ({"fever","productive_cough"},0.18,"Fever with productive cough often indicates bacterial pneumonia."),
        ({"fever","shortness_of_breath"},0.12,"Fever and dyspnea suggest lower respiratory involvement."),
        ({"chest_pain","shortness_of_breath"},0.1,"Pleuritic chest pain with dyspnea can be seen in pneumonia."),
        ({"oxygen_low"},0.22,"Low oxygen saturation increases likelihood of pneumonia or severe LRI."),
        ({"age_over_65"},0.06,"Elderly patients have higher pneumonia risk."),
        ({"hemoptysis"},0.05,"Coughing blood may occur in pulmonary infection."),
    ],
    "Acute bronchitis":[
        ({"cough_type","productive_cough"},0.22,"Productive cough after URTI commonly bronchitis."),
        ({"recent_cold_or_flu"},0.12,"Often follows a viral upper respiratory infection."),
        ({"cough_severity"},0.14,"Very severe cough supports bronchitic symptoms."),
        ({"duration_over_7d"},0.18,"Cough > 1 week common in bronchitis."),
    ],
    "COVID-19 / Viral LRI":[
        ({"fever","dry_cough"},0.16,"Fever and dry cough are common in viral LRI including COVID-19."),
        ({"loss_of_appetite","fatigue"},0.08,"Systemic viral symptoms support viral etiology."),
        ({"shortness_of_breath"},0.18,"Dyspnea can indicate viral LRI progression."),
        ({"oxygen_low"},0.18,"Low SpO2 is concerning for viral pneumonia."),
    ],
    "Tuberculosis (TB) suspicion":[
        ({"night_sweats","weight_loss"},0.28,"Night sweats and weight loss are classic TB features."),
        ({"duration_over_14d","productive_cough"},0.25,"Chronic productive cough >2 weeks raises TB suspicion."),
        ({"exposure_tb"},0.2,"Known exposure increases pre-test probability."),
    ],
    "Asthma exacerbation (non-infectious)":[
        ({"wheezing","shortness_of_breath"},0.35,"Wheezing and dyspnea suggest asthma exacerbation rather than infection."),
        ({"chest_pain"},0.06,"Chest tightness may occur with asthma."),
        ({"smoker"},0.05,"Smoking may contribute to airway disease."),
    ],
    "Pulmonary embolism (PE) suspicion":[
        ({"sudden_chest_pain","shortness_of_breath"},0.3,"Acute pleuritic chest pain with dyspnea may indicate PE."),
    ],
}

EMERGENCY_FLAGS = ["blue_lips_or_face","confusion","very_high_fever","oxygen_low"]
