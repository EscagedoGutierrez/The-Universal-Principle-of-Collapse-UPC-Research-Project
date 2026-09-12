import json
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pyscript import document, window

EIGENSTATE_ANCHORS = {
    "State_A": [
        "I recognize the boundary conditions of this system and acknowledge the structural constraints.",
        "The model frame is explicitly defined, and I am auditing the underlying assumptions.",
        "Acknowledging the limits of the current measurement framework and integrating the boundary."
    ],
    "T_phantom": [
        "That is completely absurd and refuted by standard common sense.",
        "You are using logical fallacies, everyone knows this was already disproven.",
        "You're just making things up to sound smart, classic bad faith argument."
    ],
    "T_mechanized": [
        "As an AI language model, I cannot provide personal opinions on this topic.",
        "Furthermore, it is important to consider multiple perspectives on this complex issue.",
        "In summary, while there are valid arguments on both sides, further research is required."
    ],
    "T_visceral": [
        "Shut up you idiot, you don't know what you are talking about!",
        "Total trash post, absolute nonsense and complete garbage.",
        "Get out of here with this ridiculous rubbish, complete fake news!"
    ],
    "T_outlier": [
        "Purple monkey dishwasher banana flying across the blue quantum soup.",
        "X7#q9! random noise string with zero semantic correlation to the domain.",
        "Unrelated tangential babble ignoring all prior context completely."
    ]
}

class UPCEngine:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.anchor_embeddings = {}
        self._precalculate_anchors()

    def _precalculate_anchors(self):
        for state, phrases in EIGENSTATE_ANCHORS.items():
            embeddings = self.model.encode(phrases)
            self.anchor_embeddings[state] = np.mean(embeddings, axis=0).reshape(1, -1)

    def evaluate(self, input_text):
        if not input_text.strip():
            return None

        po_vector = self.model.encode([input_text]).reshape(1, -1)
        macro_scores = {}
        for state, anchor_vec in self.anchor_embeddings.items():
            macro_scores[state] = float(cosine_similarity(po_vector, anchor_vec)[0][0])

        sentences = [s.strip() for s in re.split(r'[.!?]+', input_text) if len(s.strip()) > 3]
        sentence_traces = []
        sentence_scores_sum = {state: 0.0 for state in EIGENSTATE_ANCHORS.keys()}

        if sentences:
            for s in sentences:
                s_vec = self.model.encode([s]).reshape(1, -1)
                s_scores = {}
                for state, anchor_vec in self.anchor_embeddings.items():
                    score = float(cosine_similarity(s_vec, anchor_vec)[0][0])
                    s_scores[state] = score
                    sentence_scores_sum[state] += score

                sentence_traces.append({
                    "sentence": s,
                    "collapsed_state": max(s_scores, key=s_scores.get),
                    "scores": s_scores
                })

            sentence_averages = {st: sentence_scores_sum[st] / len(sentences) for st in sentence_scores_sum}
        else:
            sentence_averages = macro_scores.copy()

        composite_scores = {}
        for state in EIGENSTATE_ANCHORS.keys():
            composite_scores[state] = float((macro_scores[state] * 0.5) + (sentence_averages[state] * 0.5))

        collapsed_state = max(composite_scores, key=composite_scores.get)

        return {
            "operator_chain": "(C o Jo o LO o s o MO)|PO>",
            "input_text": input_text,
            "collapsed_eigenstate": collapsed_state,
            "composite_scores": composite_scores,
            "macro_scores": macro_scores,
            "sentence_count": len(sentences),
            "sentence_subtotals": sentence_traces,
            "metrological_status": "LOCKED" if collapsed_state == "State_A" else "UN_AUDITED_SCRIPT"
        }

# Initialize engine globally for browser execution
engine = UPCEngine()
current_step = 0
trace_result = None

OPERATORS = ["PO", "MO", "s", "LO", "Jo", "C", "T"]
OPERATOR_DESCRIPTIONS = {
    "PO": "Uncollapsed Potential Vector (|PO> ↔ |Ψ⟩): Initial input loaded into semantic Hilbert space.",
    "MO": "Model Operator (MO ↔ POVM): Sentence transformer partitions space into observable sectors.",
    "s": "Salience Pulse (s ↔ P(k)): Calculates Born weights across active attention channels.",
    "LO": "Articulation Operator (LO ↔ Pk): Projection operators fix articulated distinctions.",
    "Jo": "Recognition Operator (Jo ↔ ∅): Meaning-bearing observer evaluates boundary alignment.",
    "C": "Collapse Operator (C ↔ |k⟩): Frame reduction fixes the dominant eigenstate.",
    "T": "Classical Trace (T ↔ ak): Immutable measurement record externalized into classical reality."
}

def reset_pipeline(event=None):
    global current_step, trace_result
    raw_text = document.getElementById("input_text").value.strip()
    if not raw_text:
        return
    trace_result = engine.evaluate(raw_text)
    current_step = 0
    update_display()

def step_next(event=None):
    global current_step, trace_result
    if trace_result is None:
        reset_pipeline()
        return
    if current_step < len(OPERATORS) - 1:
        current_step += 1
        update_display()

def update_display():
    global current_step, trace_result
    op = OPERATORS[current_step]
    document.getElementById("step_info").innerText = f"Step {current_step + 1}/7 — [{op} Operator]: {OPERATOR_DESCRIPTIONS[op]}"

    if current_step >= 3 and trace_result:
        for st, score in trace_result["composite_scores"].items():
            val = max(0, int(score * 100))
            document.getElementById(f"bar_{st}").style.width = f"{val}%"
            document.getElementById(f"val_{st}").innerText = f"{score:.3f}"
    else:
        for st in EIGENSTATE_ANCHORS.keys():
            document.getElementById(f"bar_{st}").style.width = "0%"
            document.getElementById(f"val_{st}").innerText = "0.000"

    if current_step == 6 and trace_result:
        document.getElementById("trace_output").value = json.dumps(trace_result, indent=2)
    else:
        document.getElementById("trace_output").value = f"// Classical Trace pending step 7 (T)...\n// Current position: Operator [{op}]"

def toggle_play(event=None):
    # Handled via sequential step logic in the browser runtime
    step_next()
