# Diagram rešitve: prejeti računi

Interaktivna različica: https://claude.ai/artifact/QRCjuZoujWbRcEoE9EmK14 (zasebna povezava).

## Potek računa

```mermaid
flowchart LR
  IZV["Izvajalec<br/>s.p. / d.o.o., redko tuj"] -- "naloži PDF" --> XTRF["XTRF portal<br/>samo PDF, brez XML"]
  XTRF -- "obvestilo po e-pošti" --> GM["Gmail<br/>matjaz.ambroz@amidas.si"]
  TRG["Sprožilec<br/>rutina 8:00 ali /prejeti-racuni"] --> STR

  subgraph AG["AGENT SAM (samo priprava)"]
    STR["Strateg · Opus<br/>analiza, dvojnik, IBAN, XTRF, DDV<br/>predlog konta, JSON + zastavice"]
    GRA["Graditelj · Sonnet<br/>Sheets, oznake, eSlog XML<br/>osnutek: 1 račun = 1 mail"]
    QA["QA vrata · Opus<br/>točkovnik 100, prag 95"]
    STO[("Evidenca Sheets<br/>Drive Računi/LLLL-MM<br/>oznake Gmail")]
  end

  XTRF -- "mcp-xtrf, samo GET" --> STR
  GM -- "bere" --> STR
  STO -- "bere dvojnike" --> STR
  STR -- "JSON" --> GRA
  XSD["eslog.xsd + vzorec.xml<br/>od servisa, še manjka"] -. "validate.sh" .-> GRA
  GRA -- "vpiše" --> STO
  GRA -- "delo" --> QA
  QA -- "manj kot 95: nazaj, največ 2x" --> GRA
  STR -- "označi" --> FLAG["Zastavice<br/>tuj izvajalec, IBAN, dvojnik,<br/>nepreverjen XML"]

  QA -- "95 ali več: osnutki pripravljeni" --> MAT

  subgraph HUM["SAMO ČLOVEK"]
    MAT["Matjaž<br/>pregleda osnutke, sam pošlje"]
    SRV["Servis · e-računi<br/>To: 50375431@e-racuni.com<br/>CC: invoices@amidas.si<br/>PDF + XML, knjiži sam"]
  end
  MAT -- "pošlje, 1 račun = 1 sporočilo" --> SRV

  classDef agent fill:#e1edf8,stroke:#2b69a0,color:#15212b;
  classDef human fill:#fff0cf,stroke:#a96d10,color:#15212b;
  classDef missing stroke:#a96d10,stroke-dasharray:5 4;
  class STR,GRA,QA agent;
  class MAT human;
  class XSD missing;
```

**Agent ne sme:** pošiljati e-pošte, brisati, plačevati, pisati v XTRF.

## Mesečni ritem

```mermaid
timeline
  title Mesec
  vsak delovni dan ob 8:00 : dnevna rutina : 2 do 5 računov
  12. v mesecu : opomnik : kaj še ni poslano servisu
  16. v mesecu : kontrola : dva dni rezerve
  18. v mesecu : rok servisa : ob vikendu prejšnji delovnik
```

## Odprto
1. eSlog XSD in vzorčni XML od servisa (do takrat osnutki `[XML NEPREVERJEN]`).
2. Ali agent iz Gmaila/XTRF dobi vsebino PDF-ja za priponko (sicer `[PRILOGE ROČNO]`).
3. Potrditev kontov s strani servisa.
