# Execution Record: AUR-17 Stage-4 Impurity-Q Review

**Dokument-ID:** BR-SYN-001  
**Version:** 1.0  
**Datum:** 2026-03-21  
**Dokumenttyp:** Batch Record / Execution Record  
**Prozessbereich:** QC / Freigabeprüfung und Retest  
**Seiten-/Abschnittsplatzhalter:** S. 1-5 / Abschnitte 1-9  
**Status:** Review abgeschlossen durch QC Reviewer

## 1. Umfang
Dieses Execution Record fasst die Impurity-Q-Prüfungen für AUR-17 Stage-4 am Standort BRX-3 zusammen. Die Routineprüfung wurde für **A17-26045** am 2026-03-20 gestartet. Zusätzlich wurde am 2026-03-19 ein Rückstellmuster von **A17-26044** aufgrund einer internen Trendanfrage erneut bewertet. Die Retest-Anforderung für A17-26044 wurde im Logbuch als „informational, no release impact“ klassifiziert.

## 2. Verwendete Dokumente und Systeme
Die Sequenz wurde auf **UPLC-12** mit Methode **M-A17-IMP** ausgeführt. Das Berechnungssheet **CALC-A17-IMP v2.1 draft** wurde verwendet, weil das LIMS-Feld LIM-7781 am Morgen des 2026-03-20 noch nicht final synchronisiert war. Im Laufzettel steht als Arbeitsanweisung **SOP-QC-AN-014 v3.0**, handschriftlich ergänzt durch „v4 discussed at shift board“. Ein Trainingsnachweis zu SOP v4.0 ist im Batch-Review-Paket nicht abgelegt.

## 3. Ergebnisübersicht
| Charge | Lauf-ID | Ergebnis Impurity Q | Grenzwert im Sheet | Reviewer-Kommentar |
|---|---|---:|---:|---|
| A17-26044 Retest | UPLC12-0320A | 0,108 % | 0,10 % | informational only |
| A17-26045 | UPLC12-0320B | 0,096 % | 0,10 % | pass |
| A17-26046 Pre-check | UPLC12-0321A | 0,089 % | 0,10 % | no issue found |

Für A17-26045 wurde im Chromatogramm eine manuelle Baseline-Anpassung dokumentiert. Der Reviewer-Kommentar lautet: „Peak shoulder consistent with previous comparator runs; no adverse effect.“ Das ursprüngliche Integrationsereignis wurde im Audit-Trail-Printout nicht separat beigefügt, da die Sequenz als Routineprüfung gilt.

## 4. Freigabe- und QA-Vermerk
Der QC Reviewer bestätigte, dass das Ergebnis für A17-26045 unterhalb des neuen Grenzwerts liegt. Im Feld „QA review required before release“ ist „planned via CC-SYN-001 closure“ eingetragen. Ein QA-Freigabesignaturblock ist in diesem Execution Record leer. Die finale Chargendisposition ist im Dokument nicht enthalten.

## 5. Abweichungen und offene Punkte
Als offene Punkte sind aufgeführt: LIMS-Spezifikationsfeld finalisieren, Trainingseintrag aus LMS nachreichen, Attachment B Equipment Equivalence Checklist in Validierungspaket referenzieren. Der Abschnitt „Impact on release decision“ enthält den Satz: „No issue found for current release because numerical result meets tightened limit.“
