"""PawPal+ AI assistant: retrieves pet care notes and asks Gemini for task suggestions."""

import re
from pathlib import Path
from typing import List, Optional

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"


import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

import json

from pawpal_system import Task

VALID_FREQUENCIES = {"once", "daily", "weekly"}
VALID_PRIORITIES = {"low", "medium", "high"}

MAX_QUESTION_LENGTH = 500

# If any of these appear in the question, treat it as an emergency (see knowledge/emergencies.md)
EMERGENCY_WORDS = [
    "chocolate", "xylitol", "grape", "raisin", "lily", "lilies", "poison", "toxic",
    "bleeding", "blood", "seizure", "collapsed", "unconscious", "not breathing",
    "can't breathe", "choking", "bloat", "heatstroke", "hit by a car", "broken leg",
    "can't pee", "straining to pee",
]

EMERGENCY_MESSAGE = (
    "This sounds like it could be an emergency. Please contact your veterinarian or an "
    "emergency animal hospital right away. For possible poisoning, you can also call "
    "ASPCA Animal Poison Control at (888) 426-4435. PawPal+ cannot help with emergencies, "
    "so no tasks were scheduled."
)


load_dotenv()  # reads GEMINI_API_KEY from .env
MODEL = "gemini-3.6-flash"



# Words that point to an animal file (e.g. "puppy" -> dog_care.md)
ANIMAL_WORDS = {
    "dog": ["dog", "dogs", "puppy", "puppies"],
    "cat": ["cat", "cats", "kitten", "kittens"],
    "rabbit": ["rabbit", "rabbits", "bunny", "bunnies"],
    "guinea_pig": ["guinea", "pig", "pigs"],
    "hamster": ["hamster", "hamsters"],
    "fish": ["fish", "betta", "goldfish", "aquarium", "tank"],
    "bird": ["bird", "birds", "budgie", "budgies", "parakeet", "parakeets", "cockatiel", "cockatiels"],
    "reptile": ["reptile", "reptiles", "gecko", "geckos", "dragon", "dragons", "lizard", "lizards"],
    "turtle": ["turtle", "turtles", "slider", "sliders"],
}

# Common words that don't help the search
STOP_WORDS = {"the", "a", "an", "and", "or", "to", "of", "for", "my", "is", "what",
              "how", "should", "do", "i", "in", "on", "it", "can", "does", "with"}


def tokenize(text: str) -> List[str]:
    """Lowercase the text and split it into words, dropping common filler words."""
    words = re.findall(r"[a-z]+", text.lower())
    return [w for w in words if w not in STOP_WORDS]


def detect_animal(question: str, species: Optional[str] = None) -> Optional[str]:
    """Return the animal the question is about, e.g. 'dog' for 'my puppy'."""
    words = set(tokenize(question))
    if species:
        words.update(tokenize(species))
    for animal, keywords in ANIMAL_WORDS.items():
        if words & set(keywords):
            return animal
    return None


def load_chunks() -> List[dict]:
    """Read every notes file and split it into one chunk per '## ' section."""
    chunks = []
    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        sections = path.read_text(encoding="utf-8").split("\n## ")[1:]  # skip the file title
        for section in sections:
            heading, _, body = section.partition("\n")
            chunks.append({"file": path.name, "heading": heading.strip(), "text": body.strip()})
    return chunks



def score_chunk(chunk: dict, question_words: set, animal: Optional[str]) -> int:
    """Calculate how relevant a note section is to the question."""
    chunk_words = set(tokenize(chunk["heading"] + " " + chunk["text"]))

    score = len(question_words & chunk_words)

    if animal and chunk["file"].startswith(animal):
        score += 5

    return score


def retrieve(question: str, species: Optional[str] = None, top_k: int = 3) -> List[dict]:
    """Return the top_k note sections that best match the question."""
    question_words = set(tokenize(question))
    animal = detect_animal(question, species)

    scored = []

    for chunk in load_chunks():
        score = score_chunk(chunk, question_words, animal)

        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda pair: pair[0], reverse=True)

    return [chunk for score, chunk in scored[:top_k]]

def build_prompt(question: str, chunks: List[dict], pet_name: Optional[str] = None) -> str:
    """Combine the instructions, retrieved notes, and question into one prompt."""
    notes = "\n\n".join(f"[{c['file']} - {c['heading']}]\n{c['text']}" for c in chunks)
    pet_line = f"The pet's name is {pet_name}." if pet_name else ""

    return f"""You are PawPal+, a pet care scheduling assistant.
Answer ONLY using the pet care notes below. If the notes do not cover the question,
say so in "answer" and return an empty "tasks" list. Do not invent facts.

Return JSON with exactly this shape:
{{
  "answer": "2-4 sentence explanation for the owner",
  "tasks": [
    {{"description": "short task name", "time": "HH:MM (24-hour)",
      "frequency": "once" or "daily" or "weekly", "duration": minutes as a number,
      "priority": "low" or "medium" or "high", "source": "file name the task came from"}}
  ]
}}
Suggest at most 6 tasks. {pet_line}

PET CARE NOTES:
{notes}

QUESTION: {question}
"""


def ask_gemini(prompt: str) -> str:
    """Send the prompt to Gemini and return its raw JSON text."""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",  # forces JSON output
            temperature=0.2,                        # low = more consistent answers
        ),
    )
    return response.text


def to_tasks(raw_tasks: List[dict]) -> tuple:
    """Turn Gemini's task suggestions into Task objects. Return (suggestions, rejected)."""
    suggestions = []  # valid: [{"task": Task, "source": "dog_care.md"}, ...]
    rejected = []     # invalid: ["Walk: frequency 'twice a day' is not once/daily/weekly", ...]

    for item in raw_tasks:
        name = item.get("description", "(no name)")

        if item.get("frequency") not in VALID_FREQUENCIES:
            rejected.append(f"{name}: frequency '{item.get('frequency')}' is not once/daily/weekly")
            continue
        if item.get("priority") not in VALID_PRIORITIES:
            rejected.append(f"{name}: priority '{item.get('priority')}' is not low/medium/high")
            continue

        try:
            task = Task(
                description=str(name).strip(),
                time=item.get("time"),              # validate_time() runs here
                frequency=item["frequency"],
                duration=int(item.get("duration", 15)),
                priority=item["priority"],
            )
        except (ValueError, TypeError) as error:
            rejected.append(f"{name}: {error}")
            continue

        suggestions.append({"task": task, "source": item.get("source", "unknown")})

    return suggestions, rejected


def is_emergency(question: str) -> bool:
    """Return True if the question mentions an emergency warning sign."""
    text = question.lower()
    return any(word in text for word in EMERGENCY_WORDS)


def make_result(answer: str, suggestions=None, rejected=None, sources=None,
                emergency: bool = False) -> dict:
    """Build the result dictionary that ask_ai() always returns."""
    return {
        "answer": answer,
        "suggestions": suggestions or [],
        "rejected": rejected or [],
        "sources": sources or [],
        "emergency": emergency,
    }


def ask_ai(question: str, pet_name: Optional[str] = None, species: Optional[str] = None) -> dict:
    """Full pipeline: check the question -> retrieve notes -> ask Gemini -> convert to Tasks."""
    question = question.strip()

    # D1: input checks
    if not question:
        return make_result("Please type a question about your pet's care.")
    if len(question) > MAX_QUESTION_LENGTH:
        return make_result(f"Please keep your question under {MAX_QUESTION_LENGTH} characters.")

    # D2: emergency check, BEFORE retrieval
    if is_emergency(question):
        return make_result(EMERGENCY_MESSAGE, sources=["emergencies.md"], emergency=True)

    chunks = retrieve(question, species)
    if not chunks:
        return make_result("I don't have pet care notes about that.")

    raw = ask_gemini(build_prompt(question, chunks, pet_name))
    data = json.loads(raw)
    suggestions, rejected = to_tasks(data.get("tasks", []))

    return make_result(
        data.get("answer", ""),
        suggestions,
        rejected,
        [f"{c['file']} - {c['heading']}" for c in chunks],
    )