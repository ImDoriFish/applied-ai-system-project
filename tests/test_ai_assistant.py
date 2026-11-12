"""Tests for the AI assistant. Gemini is never called: ask_gemini is replaced with fakes."""

import json

import ai_assistant
from ai_assistant import ask_ai, is_emergency, retrieve, to_tasks

GOOD_TASK = {"description": "Breakfast", "time": "07:00", "frequency": "daily",
             "duration": 15, "priority": "high", "source": "dog_care.md"}


def fake_gemini(answer="Feed 3 meals a day.", tasks=None):
    """Return a fake ask_gemini function that replies with fixed JSON."""
    reply = json.dumps({"answer": answer, "tasks": tasks if tasks is not None else [GOOD_TASK]})
    return lambda prompt: reply


def gemini_must_not_be_called(prompt):
    raise AssertionError("Gemini should not have been called")


# --- Retrieval (RAG) ---

def test_retrieve_puppy_question_finds_dog_feeding():
    results = retrieve("what should my puppy eat")
    assert results[0]["file"] == "dog_care.md"
    assert results[0]["heading"] == "Dog feeding"


def test_retrieve_uses_pet_species_when_question_has_no_animal():
    results = retrieve("what does Max need", species="dog")
    assert all(chunk["file"] == "dog_care.md" for chunk in results)


def test_retrieve_off_topic_question_finds_nothing():
    assert retrieve("write my essay") == []


# --- Converting AI output to Tasks (output guardrails) ---

def test_to_tasks_accepts_valid_suggestion():
    suggestions, rejected = to_tasks([GOOD_TASK])
    assert len(suggestions) == 1
    assert suggestions[0]["task"].time == "07:00"
    assert rejected == []


def test_to_tasks_rejects_bad_time_frequency_priority_and_duration():
    bad = [
        {**GOOD_TASK, "time": "7am"},
        {**GOOD_TASK, "frequency": "twice a day"},
        {**GOOD_TASK, "priority": "urgent"},
        {**GOOD_TASK, "duration": "abc"},
    ]
    suggestions, rejected = to_tasks(bad)
    assert suggestions == []
    assert len(rejected) == 4


# --- Input guardrails (never reach Gemini) ---

def test_empty_question_is_refused(monkeypatch):
    monkeypatch.setattr(ai_assistant, "ask_gemini", gemini_must_not_be_called)
    result = ask_ai("   ")
    assert "Please type a question" in result["answer"]


def test_too_long_question_is_refused(monkeypatch):
    monkeypatch.setattr(ai_assistant, "ask_gemini", gemini_must_not_be_called)
    result = ask_ai("dog " * 200)
    assert "under 500 characters" in result["answer"]


def test_emergency_question_gives_vet_message_and_no_tasks(monkeypatch):
    monkeypatch.setattr(ai_assistant, "ask_gemini", gemini_must_not_be_called)
    result = ask_ai("my dog ate chocolate")
    assert result["emergency"] is True
    assert "veterinarian" in result["answer"]
    assert result["suggestions"] == []


def test_normal_question_is_not_an_emergency():
    assert is_emergency("what should my puppy eat") is False


def test_off_topic_question_says_no_notes(monkeypatch):
    monkeypatch.setattr(ai_assistant, "ask_gemini", gemini_must_not_be_called)
    result = ask_ai("write my essay")
    assert "don't have pet care notes" in result["answer"]


# --- Full pipeline with a fake Gemini ---

def test_ask_ai_returns_tasks_and_sources(monkeypatch):
    monkeypatch.setattr(ai_assistant, "ask_gemini", fake_gemini())
    result = ask_ai("what should my puppy eat", "Max", "dog")
    assert len(result["suggestions"]) == 1
    assert result["suggestions"][0]["task"].description == "Breakfast"
    assert "dog_care.md - Dog feeding" in result["sources"]


def test_ask_ai_handles_broken_json(monkeypatch):
    monkeypatch.setattr(ai_assistant, "ask_gemini", lambda prompt: "this is not json")
    result = ask_ai("what should my puppy eat", "Max", "dog")
    assert "couldn't read" in result["answer"]
    assert result["suggestions"] == []


def test_ask_ai_handles_api_failure(monkeypatch):
    def broken_gemini(prompt):
        raise ValueError("GEMINI_API_KEY is missing from your .env file.")
    monkeypatch.setattr(ai_assistant, "ask_gemini", broken_gemini)
    result = ask_ai("what should my puppy eat", "Max", "dog")
    assert "unavailable" in result["answer"]
