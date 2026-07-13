# Fabric Escape Room

Build escape room games on **Microsoft Fabric** using **GitHub Copilot**. Give Copilot a theme, and it creates a fully playable 5-module puzzle game across Fabric services — Lakehouse, Eventhouse, Semantic Model, Notebook, Data Agent, and OrgApp.

---

## How It Works

```
Theme → Copilot builds → Team configures → Test & reset → Players escape!
```

1. **Choose a theme** — haunted mansion, pirate ship, biolab outbreak, or anything you invent
2. **Paste the prompt** into GitHub Copilot — it creates the Lakehouse, Eventhouse, Semantic Model, seed notebook, and diagnostic notebook
3. **Team builds in parallel** — each person follows their setup guide file to create reports, dashboard, Data Agent, and OrgApp
4. **Test the game** — solve all 4 puzzles using the answer key, verify the victory message in Module 5, then reset all filters for players
5. **Share the OrgApp link** — players open it and start solving puzzles

---

## The 5 Modules

Players must find 4 authorization codes hidden across the first 4 modules, then combine them in Module 5 to escape.

| Module | Puzzle Type | Fabric Item | What Players Do |
|--------|------------|-------------|-----------------|
| **1. Data Anomaly** | Find the outlier | Power BI Report | Browse a dataset with a slicer — one entity has abnormal readings. Drillthrough reveals the code. |
| **2. Pattern Gap** | Find the missing data point | RTI Dashboard | A bar chart shows 50+ time windows. One has zero activity — that's the gap. A table maps it to the code. |
| **3. AI Conversation** | Extract info from an AI | Data Agent | Chat with a themed character who gives cryptic hints. The code is in a table the AI can query. |
| **4. Read & Discover** | Find the code in output | Notebook | Read through many diagnostic sections. The code is buried in one among warnings and noise. |
| **5. Final Escape** | Combine all 4 codes | Power BI Report | Four dropdown slicers + a status card. All 4 correct → victory. Wrong → denied. |

---

## Game Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        OrgApp (Game Portal)                 │
│                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ Module 1 │ │ Module 2 │ │ Module 3 │ │ Module 4 │      │
│  │  Report  │ │   RTI    │ │  Data    │ │ Notebook │      │
│  │          │ │Dashboard │ │  Agent   │ │(read-only)│      │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────────┘      │
│       │             │            │                          │
│       ▼             ▼            ▼                          │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐                   │
│  │Semantic │  │Eventhouse│  │Lakehouse│                    │
│  │ Model   │  │   (KQL)  │  │ Delta   │                    │
│  └────┬────┘  └──────────┘  └────┬────┘                    │
│       │              ▲           │                          │
│       │              │     Seed Notebook                    │
│       └──────────┐   │  ┌────────┘                          │
│                  ▼   │  ▼                                   │
│            ┌──────────────┐                                 │
│            │  Module 5    │                                 │
│            │  Final Escape│                                 │
│            │  (Report)    │                                 │
│            └──────────────┘                                 │
└─────────────────────────────────────────────────────────────┘
```

| Fabric Item | Purpose |
|-------------|---------|
| **Lakehouse** | Delta tables — puzzle data, clue fragments, authorization codes |
| **Seed Notebook** | Populates Lakehouse tables (runs inside Fabric via `RunNotebook`) |
| **Eventhouse** | Time-series data — activity logs, sensor readings |
| **Semantic Model** | DirectLake model with DAX measures for reports |
| **Diagnostic Notebook** | Pre-formatted output with one hidden code (Module 4) |
| **Data Agent** | AI character players chat with (Module 3) |
| **OrgApp** | Game portal — players access everything here |

---

## Prerequisites

- **Microsoft Fabric workspace** with capacity (F64+ recommended)
- **Contributor** or **Member** role on the workspace
- **Power BI Pro** license and **Power BI Desktop** ([download](https://powerbi.microsoft.com/desktop))
- **GitHub Copilot** license
- **Azure CLI** installed ([install guide](https://learn.microsoft.com/cli/azure/install-azure-cli))
- **Tenant settings** that allow Lakehouse, Notebook/Spark jobs, Eventhouse/KQL, semantic model authoring, Data Agent, OrgApp, and sharing/publishing

---

## Getting Started

See [CREATION-INSTRUCTIONS.md](CREATION-INSTRUCTIONS.md) for the full step-by-step guide.

Before setup day, run the event preflight checklist in [EVENT-PREREQS.md](EVENT-PREREQS.md).

**Quick start:**

1. Clone this repo and [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric) as sibling folders
2. Open both in a VS Code multi-root workspace
3. Open Copilot Chat in **Agent** mode
4. Paste the prompt from [CREATION-INSTRUCTIONS.md](CREATION-INSTRUCTIONS.md) with your theme
5. Verify the build, follow the setup guides, test, and play!

---

## Example Themes

| Theme | Setting | AI Character |
|-------|---------|-------------|
| 🏴‍☠️ Pirate Ship | A cursed vessel heading for the reef | Captain Bones (ghost) |
| 🔬 Biolab Outbreak | High-security lab in lockdown | NEXUS (facility AI) |
| 🏚️ Haunted Mansion | A Victorian manor sealed by a spell | Lady Ravencrest (spirit) |
| 🏦 Bank Vault Heist | Trapped inside during a heist gone wrong | ATLAS (vault AI) |
| 🌋 Volcano Base | A villain's lair with rising lava | Dr. Scorpio's mainframe |
| 🚀 Space Station | Station hit by an asteroid, power failing | ODIN (damaged station AI) |

See [EXAMPLE-THEMES.md](EXAMPLE-THEMES.md) for full details with story hooks and module ideas.

---

## Files

| File | Purpose |
|------|---------|
| [CREATION-INSTRUCTIONS.md](CREATION-INSTRUCTIONS.md) | Full guide — environment setup, prompt template, verification, testing, troubleshooting |
| [.github/agents/](.github/agents/escape-room-builder.agent.md) | Agent + skills for Copilot — game design, Fabric provisioning, validation, documentation |
| [EXAMPLE-THEMES.md](EXAMPLE-THEMES.md) | Theme ideas with story hooks and module suggestions |
