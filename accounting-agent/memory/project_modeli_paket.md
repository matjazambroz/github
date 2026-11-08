---
name: Modeli in naročniški paket
description: Točni modeli agentov in uporabnikov paket Claude
type: project
---
Točni modeli (7.-8. 11. 2026): Strateg in QA `claude-opus-5-5`, Graditelj `claude-sonnet-5-5`. `effort` ostane privzet
(Opus 5.5 ima privzeto `medium`, Sonnet 5.5 `high`).
Uporabnik ima paket **Claude Pro**.
**Why:** predvidljiv strošek in obnašanje; splošni oznaki `opus`/`sonnet` se lahko preslikata v drug model.
**How to apply:** če Opus 5.5 v paketu Pro ni na voljo ali se hitro porabi omejitev, v `.claude/agents/racuni-strateg.md` in
`.claude/agents/racuni-qa.md` zamenjaj `model:` na `claude-sonnet-5-5` (QA naj ostane najmočnejši model, ki ga paket dovoli).
Ne predpostavljaj, kaj Pro vključuje: preveri z `/model` in na strani paketa.
