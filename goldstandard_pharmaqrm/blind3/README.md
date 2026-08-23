# Blindkorpus 3 (August 2026)

Acht neue Fälle, 16 versteckte Fehler, 16 harmlose Kontrollstellen. Gebaut am
23.08.2026, **nachdem** die Regelschicht (Reihenfolge, Vier-Augen, CAPA ohne
Wirksamkeitsprüfung, Grenzwertvergleich) und der schmale Assessor fertig
waren — aber ohne dass ein Lauf gegen diese Fälle stattgefunden hätte. Das ist
die erste unabhängige Messung des neuen Aufbaus. Nach dem ersten Lauf ist
dieser Korpus Regressionsmaterial; die nächste unabhängige Zahl braucht
Blindkorpus 4.

Bereiche: sterile Abfüllung, API, QC-Labor (Change-Control-Paket), Verpackung,
Stabilität/OOS, Reinigungsvalidierung, computergestütztes System, Wareneingang.

    cd backend && ./.venv/bin/python -m app.evals.run_goldstandard --mode live \
      --engine requirement --stack hetzner --assessor-mode narrow \
      --cases-dir ../goldstandard_pharmaqrm/blind3 --pipeline-timeout-seconds 2400
