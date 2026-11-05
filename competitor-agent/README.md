# competitor-agent

Minimalni agentic sistem: Scout -> Planner -> Executor (web_search) -> Critic -> Memory -> Human check -> .pptx

    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=...

    # Faza 1: konkurenca v Sloveniji (Scout jih najde sam)
    python agent.py --company "AMIDAS d.o.o." --scope si --out analiza_si.pptx

    # Faza 2: razširitev na EU (ločen memory, da se podatki ne mešajo)
    python agent.py --company "AMIDAS d.o.o." --scope eu --n 8 --db eu.db --out analiza_eu.pptx

    # Ali ročno podani konkurenti
    python agent.py --company "AMIDAS d.o.o." --competitors "Podjetje A" "Podjetje B"
