# Autonomous Document Intelligence Agent

> **Status: Phase 0 — Dataset and Specification Foundation**

This repository contains the foundation for an Autonomous Document Intelligence Agent. The project is currently in **Phase 0**, focusing strictly on defining dataset structures, evaluation criteria, and domain schemas prior to implementation.

## Project Structure

```
autonomous-document-intelligence-agent/
├── README.md                           # Project overview & phase status
├── scope.md                            # Detailed scope & objectives
├── schemas/                            # Schema definitions
│   ├── government_scheme.json          # Government scheme schema shell
│   └── opportunity.json                # Opportunity schema shell
├── data/                               # Dataset & source registries
│   ├── government_schemes/
│   │   ├── sources.csv                 # Source URLs & metadata for schemes
│   │   └── documents/                  # Raw document store
│   └── opportunities/
│       ├── sources.csv                 # Source URLs & metadata for opportunities
│       └── documents/                  # Raw document store
├── evaluation/                         # Benchmarking & evaluation framework
│   ├── gold/                           # Hand-curated ground truth data
│   └── criteria.md                     # Evaluation metrics and guidelines
├── src/                                # Application source code placeholder
├── tests/                              # Test suite placeholder
└── docs/                               # Additional documentation placeholder
```

## Current Phase Objectives (Phase 0)

1. Establish source tracking (`data/**/sources.csv`).
2. Finalize document extraction schemas (`schemas/`).
3. Define evaluation criteria and collect gold standard datasets (`evaluation/`).
