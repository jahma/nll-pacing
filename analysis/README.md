# NLL-Analyse: Wie schnell gehen die LäuferInnen los?

`fade.py` vergleicht für alle FinisherInnen 2021–2025 (seit der Streckenänderung) die offizielle
10-km-Zwischenzeit mit dem Anteil der Endzeit, den man bei gleichmäßiger Anstrengung nach 10 km
gelaufen hätte (Steigungsregel wie auf der Seite: +3,3 % / −1,8 % je Prozent, ab −8 % gedeckelt).
Ergebnis je Zielzeitgruppe: Sekunden vor (+) oder hinter (−) dem gleichmäßigen Plan bei km 10.

- `course.json` — Streckenprofil (20-m-Raster)
- `fade_summary.json` — nur zusammengefasste Werte (Median, Quartile, Anteile, n); keine Einzelzeiten, keine Namen
- Die Eingabedaten (Zeiten ohne Namen, aus den öffentlichen Ergebnislisten) liegen nicht in diesem Repo.
