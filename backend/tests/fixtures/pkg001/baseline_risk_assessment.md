# Baseline Risk Assessment: Impurity-Q-Spezifikationsänderung

**Dokument-ID:** RA-SYN-001  
**Version:** 1.0  
**Datum:** 2026-03-16  
**Dokumenttyp:** Baseline Risk Assessment  
**Prozessbereich:** QC / Spezifikations- und Methodenrisiko  
**Seiten-/Abschnittsplatzhalter:** S. 1-4 / Abschnitte 1-6  
**Status:** Vorläufig genehmigt durch Process Owner

## 1. Bewertungsumfang
Dieses Assessment bewertet die Absenkung des Grenzwerts für Impurity Q bei **AUR-17 Stage-4** von NMT 0,20 % auf NMT 0,10 %. Betrachtet werden Probenahme, chromatographische Methode, Berechnungssheet, LIMS-Spezifikationsfeld und Freigabeentscheidung. Nicht betrachtet werden historische Rückstellmusterprüfungen, da diese „nicht Teil der Routinefreigabe“ sind.

## 2. Risikoeinschätzung
Die Risikoanalyse bewertet die analytische Fähigkeit als niedrig bis mittel. Als Hauptargument wird angeführt, dass die Methode **M-A17-IMP** bereits für Impurity Q eingesetzt wird und im Vergleichslabor reproduzierbare Ergebnisse nahe 0,12 % geliefert hat. Für BRX-3 wird die gleiche Probeneinwaage und Verdünnung verwendet. Die UPLC-Plattform wird als „funktional äquivalent“ bewertet, weil die Retentionszeitfenster und die Integrationsparameter aus dem zentralen Methodenpaket übernommen werden.

| Risiko-ID | Risiko | Bewertung vor Maßnahme | Maßnahme | Restrisiko |
|---|---|---:|---|---:|
| R1 | Quantifizierung nahe neuem Grenzwert | M | System Suitability mit niedrigem Standard | L |
| R2 | Falsche Spezifikation im LIMS | M | LIMS-Feld Change Ticket LIM-7781 | L |
| R3 | Anwender nutzt alte SOP | M | Hinweis in Schichtübergabe | L |
| R4 | Geräteunterschied BRX-North vs. BRX-3 | M | Vergleichslabordaten akzeptiert; keine separate Bridge | L |

## 3. Evidenzbasis
Die Bewertung verweist auf **MV-VAL-221**, **BRX-North Comparator Summary CMP-221-N**, und die System Suitability vom 2026-03-14 am Standort BRX-3. Der Reviewer-Kommentar lautet: „No issue found; validation package demonstrates method fitness for low-level impurity reporting.“ Der Kommentar enthält keine separate Begründung, warum die Validierung mit dem neuen Grenzwert identisch bewertet wird.

## 4. Prozess- und Trainingseffekt
Da der Ablauf für Analysten unverändert bleibt, wird kein verpflichtendes Training festgelegt. Als Kommunikationsmaßnahme reicht laut Tabelle 2 ein Schichtboard-Hinweis für fünf Arbeitstage. Die Wirksamkeit der Kommunikation soll nicht gemessen werden, weil „der Grenzwert im LIMS automatisch angezeigt wird“.

## 5. Annahmen und Grenzen
Dieses Assessment geht davon aus, dass alle Freigabebatches nach LIMS-Umstellung geprüft werden. Es geht außerdem davon aus, dass Comparator-Lab-Daten auf BRX-3 übertragen werden dürfen. Attachment 2 „Equipment Equivalence Checklist“ wird als Referenz genannt, ist aber im Assessment-Paket als „to be filed with validation evidence“ markiert.
