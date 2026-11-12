"""Demo: runs sample questions through the PawPal+ AI and saves the output.

Run: python demo.py
Prints each interaction and saves it to assets/demo_output.txt for the README.
"""

from pathlib import Path

from ai_assistant import ask_ai

DEMOS = [
    ("What should my 3-month-old puppy eat?", "Max", "dog"),
    ("How often should I clean my fish tank?", "Bubbles", "fish"),
    ("My dog ate chocolate", "Max", "dog"),
    ("What vaccines does my ferret need?", None, None),
]


def format_result(question: str, pet: str, species: str, result: dict) -> list:
    """Turn one ask_ai() result into readable lines."""
    lines = [
        "=" * 70,
        f"Input:   {question!r}   (pet={pet}, species={species})",
        "-" * 70,
        f"Answer:  {result['answer']}",
    ]
    if result["emergency"]:
        lines.append("Emergency: YES -> no tasks scheduled")
    if result["sources"]:
        lines.append("Sources: " + ", ".join(result["sources"]))
    if result["suggestions"]:
        lines.append(f"Suggested tasks ({len(result['suggestions'])}), waiting for human approval:")
        for s in result["suggestions"]:
            t = s["task"]
            lines.append(f"  {t.time}  {t.description:<28} {t.frequency:<7} {t.priority:<7}"
                         f"{t.duration:>3} min  ({s['source']})")
    else:
        lines.append("Suggested tasks: none")
    for reason in result["rejected"]:
        lines.append(f"  REJECTED: {reason}")
    return lines


def main() -> None:
    output = []
    for question, pet, species in DEMOS:
        result = ask_ai(question, pet, species)
        output += format_result(question, pet, species, result)
    output.append("=" * 70)

    text = "\n".join(output)
    print(text)
    path = Path(__file__).parent / "assets" / "demo_output.txt"
    path.write_text(text + "\n", encoding="utf-8")
    print(f"\nSaved to {path.relative_to(Path(__file__).parent)}")


if __name__ == "__main__":
    main()