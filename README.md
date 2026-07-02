# Imtithal | امتثال

Imtithal is an AI-assisted contract compliance analysis system designed to review outsourcing contracts in the financial sector and compare them against SAMA requirements.

## Goal

The goal of Imtithal is to support financial institutions in reviewing outsourcing contracts more efficiently by automating the initial compliance checking process. The system aims to reduce manual effort, speed up contract review, improve consistency, and help identify missing or incomplete compliance requirements.

## Project Overview

The system reads an Arabic PDF contract, extracts its text, and compares its clauses against a structured checklist based on SAMA outsourcing requirements.

Each requirement is classified as:

- **Compliant**: the requirement is covered.
- **Partial**: the requirement is partially covered or unclear.
- **Missing**: the requirement is missing or not sufficiently addressed.

The system then calculates the final compliance score and outputs the results in a structured format that can be connected to a user interface.

## Current Features

- Arabic PDF contract analysis.
- Text extraction from PDF files.
- Structured checklist based on SAMA requirements.
- Rule-based validation with semantic matching.
- Compliance score calculation.
- Classification of requirements into Compliant / Partial / Missing.
- Structured output for frontend integration.
- Initial RAG support for retrieving relevant SAMA evidence for future explainability.

## Output

The generated output includes:

- Contract file name.
- Compliance score.
- Total possible score.
- Compliance percentage.
- Number of compliant, partial, and missing requirements.
- Detailed result for each checklist item.
- Best matched clause from the contract.
- Recommendations for missing or incomplete requirements.
