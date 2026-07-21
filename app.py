"""Synthetic Case Quizzes — education only."""

from __future__ import annotations

import json
from pathlib import Path

import gradio as gr

from input_guard import DISCLAIMER

CASES = json.loads((Path(__file__).parent / "data" / "cases.json").read_text())
DISCIPLINES = ["all", *sorted({c["discipline"] for c in CASES})]


def filtered(discipline: str):
    if discipline == "all":
        return CASES
    return [c for c in CASES if c["discipline"] == discipline]


def case_labels(discipline: str):
    return [f"{c['id']}: {c['title']}" for c in filtered(discipline)]


def show_case(discipline: str, label: str):
    cases = filtered(discipline)
    by_label = {f"{c['id']}: {c['title']}": c for c in cases}
    c = by_label.get(label) or (cases[0] if cases else None)
    if not c:
        return "No cases.", gr.update(choices=[], value=None), ""
    stem = (
        f"### {c['title']}\n"
        f"**Discipline:** `{c['discipline']}` · **Specialty tag:** {c['specialty']}\n\n"
        f"> SYNTHETIC / EDUCATION — not a real patient\n\n"
        f"{c['stem']}\n\n"
        f"**Question:** {c['question']}"
    )
    radios = gr.update(choices=c["choices"], value=None)
    return stem, radios, c["id"]


def grade(case_id: str, choice: str) -> str:
    c = next((x for x in CASES if x["id"] == case_id), None)
    if not c:
        return "Select a case first."
    if not choice:
        return "Pick an answer."
    correct = c["choices"][c["answer_index"]]
    if choice == correct:
        return f"✅ Correct.\n\n{c['explanation']}\n\n**{DISCLAIMER}**"
    return (
        f"❌ Not quite. Correct answer: **{correct}**\n\n"
        f"{c['explanation']}\n\n**{DISCLAIMER}**"
    )


with gr.Blocks(title="Synthetic Case Quizzes") as demo:
    gr.Markdown(
        f"# Synthetic Case Quizzes\n\n**{DISCLAIMER}**\n\n"
        f"Banner: **synthetic / education** — never treat as clinical guidance.\n\n"
        f"[Cross Clinical OSS](https://github.com/Cross-Clinical/suite-index) · "
        f"[Jargon Explainer](https://github.com/Cross-Clinical/clinical-jargon-explainer) · "
        f"[ProMedNet](https://crossclinical.com)"
    )
    disc = gr.Dropdown(DISCIPLINES, value="all", label="Discipline")
    label = gr.Dropdown(case_labels("all"), label="Case")
    case_id = gr.State("")
    stem = gr.Markdown()
    choice = gr.Radio(label="Your answer")
    result = gr.Markdown()

    def on_disc(d):
        labels = case_labels(d)
        return gr.update(choices=labels, value=labels[0] if labels else None)

    disc.change(on_disc, disc, label).then(show_case, [disc, label], [stem, choice, case_id])
    label.change(show_case, [disc, label], [stem, choice, case_id])
    gr.Button("Check answer").click(grade, [case_id, choice], result)
    demo.load(show_case, [disc, label], [stem, choice, case_id])

if __name__ == "__main__":
    demo.launch()
