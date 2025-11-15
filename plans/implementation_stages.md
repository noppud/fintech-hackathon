# Implementation Stages: Distilled LLM Categorization with ML

This document outlines the main stages required to implement the invoice categorization system described in `plan_01.txt`, including the UI.

## Stage 0 – Problem Definition & Requirements
- Define primary use cases (e.g. invoice categorization, transaction tagging).
- Agree on target accuracy, latency, and allowed error types.
- Identify data privacy, security, and compliance requirements.
- Decide initial scope (single country/customer vs. multi-tenant SaaS).

## Stage 1 – Taxonomy & Data Model
- Design the category taxonomy (e.g. chart of accounts, expense types).
- Define entities and schemas (invoice, vendor, line items, category, confidence, audit trail).
- Decide on input formats (PDFs, CSV, JSON) and normalized internal representation.
- Define how human feedback and overrides are stored.

## Stage 2 – LLM Labeling Pipeline
- Design prompts for the LLM to categorize invoices and explain reasoning.
- Implement data anonymization / masking if needed before sending to LLM.
- Build a batch labeling pipeline (ingest → prompt LLM → parse responses → store labels).
- Add quality controls: sampling, heuristic checks, and simple rules to catch obvious errors.
- Log all inputs/outputs with trace IDs for auditing and debugging.

## Stage 3 – ML Model Training
- Choose model family (e.g. gradient boosting, small transformer, or tabular NN) based on features.
- Engineer features from invoice data (amounts, vendors, descriptions, metadata).
- Split data into train/validation/test; ensure realistic temporal or customer splits.
- Train initial model using LLM-generated labels as ground truth.
- Evaluate performance by category, customer, and data slice; define acceptance thresholds.

## Stage 4 – Inference Service & LLM Fallback
- Package the trained model into a prediction service (e.g. REST/gRPC).
- Implement confidence scoring and thresholds for “auto-accept”, “needs review”, “send to LLM”.
- Integrate LLM fallback for low-confidence or novel cases.
- Design an idempotent API for categorization requests with request/response schemas.
- Add logging, metrics (latency, confidence distribution, fallback rate), and basic monitoring.

## Stage 5 – UI / Frontend
- **Operator UI (finance/ops users)**
  - List invoices with predicted category, confidence, and source (ML vs. LLM vs. human).
  - Allow quick review and correction of categories (single and bulk edit).
  - Surface “needs review” items (low confidence or conflicting labels) in a work queue.
  - Provide filters/search (by date, vendor, amount, category, confidence range).
- **Admin / Configuration UI**
  - Manage category taxonomy (create/rename/merge categories with safeguards).
  - Configure confidence thresholds and fallback behavior per customer/tenant.
  - View model and LLM usage metrics (accuracy, fallback rate, cost, throughput).
  - Manage access control (roles: admin, reviewer, viewer).
- **UX Considerations**
  - Clear indicators of prediction source and confidence.
  - Fast bulk actions and keyboard shortcuts for power users.
  - Audit log visibility for each invoice (who changed what, when, and why).

## Stage 6 – Feedback Loop & Continual Learning
- Capture user corrections in the UI as labeled data with context.
- Periodically retrain or fine-tune the ML model using both LLM labels and human feedback.
- Detect data drift (vendors, descriptions, new categories) and schedule re-labeling as needed.
- Evaluate gains from retraining and only roll out models that beat current baseline.

## Stage 7 – Security, Compliance & Operations
- Implement authentication and authorization for APIs and UI.
- Ensure data encryption at rest and in transit; consider field-level encryption for PII.
- Define data retention policies and backup/restore procedures.
- Add audit logging for all model and user actions affecting financial data.
- Prepare basic documentation/runbooks for incidents and model rollback.

## Stage 8 – Production Rollout & Iteration
- Start with a pilot customer or a small subset of traffic in shadow mode.
- Compare model/LLM predictions against existing manual processes.
- Gradually increase automation (auto-accept) as confidence grows.
- Iterate on taxonomy, prompts, features, and UI workflow based on real-world usage.
- Plan next steps: expand to other fintech categorization tasks (transactions, receipts, etc.).

