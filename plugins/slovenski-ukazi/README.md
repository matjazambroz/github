# slovenski-ukazi

Plugin za Claude Code s 98 slovenskimi ukazi in `/ukazi` za pregled. Seznam z opisi in primeri je v [UKAZI.md](UKAZI.md).

## Namestitev

```
/plugin marketplace add matjazambroz/github
/plugin install slovenski-ukazi@matjaz-plugins
```

Nato znova zaženite Claude Code. Ukazi so na voljo kot `/slovenski-ukazi:proof`, kjer ni konflikta, pa tudi kot `/proof`.

## Posodobitev

```
/plugin marketplace update matjaz-plugins
```

## Opomba

Če imate iste ukaze tudi v `~/.claude/commands/`, jih po namestitvi plugina izbrišite, da se ne podvajajo.
