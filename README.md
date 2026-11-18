
# BDD Exam Assistant 1.0

A Python-based exam preparation assistant for database courses.

## Overview

BDD Exam Assistant helps students organize PDF learning
materials, search lecture content, associate exam questions
with knowledge concepts, and practice with structured quizzes.

## Features

- Batch PDF text extraction with OCR
- French-language OCR using Tesseract
- Structured JSON knowledge base
- Cross-document keyword search
- Source and page-level traceability
- Exam question and concept matching
- Manual review of candidate associations
- Interactive knowledge graph
- Concept difficulty sorting
- Quiz generation from a curated question bank
- Quiz results and study reports
- Unified command-line interface

## Technology Stack

- Python
- PyMuPDF
- Tesseract OCR
- JSON
- NetworkX
- PyVis
- unittest

## Project Structure

- main.py: Main application entry point
- batch_ocr.py: PDF processing and OCR
- search_knowledge.py: Keyword search
- precise_search.py: Context-based retrieval
- link_questions.py: Question-concept matching
- review_links.py: Review processing
- knowledge_graph.py: Graph visualization
- difficulty_sort.py: Difficulty sorting
- quiz_generator.py: Quiz execution
- tests/: Automated tests

## Installation

1. Install Python and Tesseract OCR.
2. Install the French language package for Tesseract.
3. Create a Python virtual environment.
4. Install project dependencies:

    python -m pip install -r requirements.txt

5. Ensure Tesseract is available in PATH, or configure
   its installation path in batch_ocr.py.

## Usage

Run:

    python main.py

Select a function from the command-line menu.

Add your own PDF files to the data/ directory.

## Testing

Run:

    python -m unittest discover -s tests -v

## Data Validation

- Keyword matching generates candidate associations.
- Candidate associations require manual verification.
- Unmatched concepts remain in the knowledge base.
- Unverified quiz answers are not automatically scored.
- Open-ended questions require manual grading.

## Limitations

- OCR accuracy depends on source image quality.
- Some mixed-content PDF pages may require additional OCR.
- Keyword matching does not provide semantic understanding.
- Difficulty levels require manual validation.
- The current version does not use an AI API.

## Version

1.0 - Python CLI Prototype
