# LLM Extraction + Deterministic Validation Engine

This project demonstrates a practical and production-oriented pattern for using Large Language Models (LLMs) in data pipelines.


Probabilistic extraction using an LLM followed by Deterministic validation using rule-based logic.

The goal is to show how LLMs can be used safely, audibly, and reliably inside real systems.

---

## Core Idea

LLMs are powerful but non-deterministic.  
This project treats them as proposers, not decision-makers.

The pipeline works as follows:

1. Extract  
   An LLM converts unstructured text into a typed schema.

2. Validate  
   A deterministic rules layer checks ranges, confidence, and consistency.

3. Report  
   The system outputs structured JSON, validation issues, and a valid flag.

At no point is another LLM used to fix errors. All validation is explicit and auditable.

---

## Key Properties

- Schema-driven  
  All extracted fields are defined using Pydantic models.

- Auditable  
  Each extracted field includes supporting evidence copied verbatim from the input.

- Uncertainty-aware  
  Each field includes a confidence score that downstream logic can reason about.

- Deterministically validated  
  Validation rules are explicit, reproducible, and independent of the LLM.

- Extensible across domains  
  Only schemas and validation policies change between domains.

---

## Extraction Model

Each extracted field follows the same contract:

value:        The extracted value or null  
evidence:     Exact substring from the input text  
confidence:   Float between 0.0 and 1.0

This makes every output inspectable, explainable, and safe to validate deterministically.

---

## Validation Model

Validation produces a list of issues.

Each issue contains:
- field
- severity (error or warning)
- human-readable message

Something is considered valid if and only if no errors are present.
Warnings indicate uncertainty or edge cases.

---

## Setup

1. Create and activate a virtual environment (recommended).

2. Install dependencies:

pip install -r requirements.txt

3. Create a .env file based on .env.example and set your OpenAI API key:

OPENAI_API_KEY=your_key_here

---

## Running the Pipeline

The pipeline is currently built to handle rental listing data.

Input listings are stored in a plain text file, separated by blank lines.

Run the pipeline:

python -m src.pipeline --in examples/listings.txt --out out/out.json

This will:
- extract structured fields using the LLM
- validate them deterministically
- write results to out/out.json
- print a summary to the console

---

## Output Format

Each listing produces:
- original text
- extracted structured fields
- validation issues
- a valid flag

This output is suitable for downstream systems, review queues, or analytics.

---

## Why This Project

Many LLM demos stop at “it works on this example”.

This project focuses on:
- failure modes
- uncertainty
- validation
- auditability
- real-world constraints

It is designed as a reusable extraction and validation engine, not a one-off script.

---

## Possible Extensions

- Additional schemas for jobs, products, events, etc.
- Learned validation policies from historical data
- Simple web UI for inspection
- Batch processing of scraped data sources

The core engine is intentionally kept minimal so these can be layered on later.
