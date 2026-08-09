# Produktthese: Von der Befundliste zur Anforderungsabdeckung

## Der Befund, der alles verschiebt

Die Requirement-Engine erreicht auf einem Blindkorpus 79 % Sensitivität bei
98 % Decoy-Spezifität und 15,5 Zeilen pro Fall. Der Finding-Pfad erreicht auf
vergleichbarem Material ähnliche Erkennung bei doppelter Listenlänge und
0,85 Redundanz.

Und trotzdem: **null Referenzen** auf `requirement_review` in `app/api/`,
`app/main.py` und `app/services/pipeline.py`. Die bessere Engine ist
ausschließlich über den Eval-Harness erreichbar. Kein Kunde kann sie sehen,
kein Upload löst sie aus, kein Export enthält sie.

Der Abstand zwischen „gut gebaut" und „Weltklasseprodukt" ist an dieser
Stelle kein Modellproblem und kein Prompt-Problem. Er ist ein Produktproblem.

## Was ein Prüfer tatsächlich beantworten muss

Szilard bekommt heute eine Liste von Beobachtungen und muss sie selbst auf
seine Prüflogik zurückfalten. Seine eigentliche Frage lautet nicht „was ist
euch aufgefallen", sondern:

> Ist jede Pflicht, die für diesen Vorgang gilt, erfüllt — und wo steht der
> Beweis?

Das ist eine **Abdeckungsfrage**, keine Fundfrage. Ein Prüfbericht, der sie
beantwortet, hat eine andere Form als ein Feed:

| Befundliste (heute) | Anforderungsabdeckung (Ziel) |
|---|---|
| n Beobachtungen, Reihenfolge nach Schwere | 28 Anforderungen, jede genau einmal |
| „was fehlt" bleibt unsichtbar | erfüllt / verletzt / unklar / nicht anwendbar |
| Vollständigkeit unbeweisbar | Vollständigkeit ist die Struktur selbst |
| Dubletten müssen bekämpft werden | strukturell unmöglich |
| Kundenregeln sind ein Feature | Kundenregeln sind das Produkt |

Der letzte Punkt ist der geschäftliche: Grünewalds eigene SOP-Anforderungen
einzuspielen heißt in dieser Form nicht „Konfiguration", sondern das Tool an
den Kunden anzupassen. Die synthetische Grünewald-Rule-Library existiert
bereits als Entwurf.

## Die drei Eigenschaften, die den Bericht auditfähig machen

1. **Jede Zeile ist eine Pflicht mit Quelle.** SOP-Name, Abschnitt, Version —
   nicht eine Modellformulierung, sondern die Anforderung, wie sie im
   Regelwerk steht.
2. **Jede Aussage trägt ihren Beweis oder ihre Lücke.** Wörtliches Zitat mit
   Dokument und Seite, server-seitig gegen den Quelltext geprüft. Wo kein
   prüfbares Zitat übrig blieb, steht das da — als `unclear`, nicht als
   stillschweigendes „erfüllt".
3. **Jede Bewertung zeigt, wie sicher sie ist.** Entailment-Urteil,
   Zweitprüfung bei kritischen Erfüllt-Bewertungen, Sample-Dissens,
   deterministische Validator-Flags. Ein Prüfer sieht, worauf er sich stützen
   kann und wo er selbst hinschauen muss.

Diese drei Eigenschaften existieren bereits im `RequirementCoverageReport` —
sie sind nur nirgends sichtbar.

## Was daraus folgt (Reihenfolge)

1. **Engine erreichbar machen**: Requirement-Pfad als wählbare Pipeline,
   Report persistieren, über API abrufbar.
2. **Prüfmappe als Abdeckungsbericht**: eine Zeile je Anforderung, gruppiert
   nach Status, mit Evidenz und Sicherheitsmerkmalen.
3. **Export**: PDF und CSV in derselben Struktur — das Artefakt, das in die
   Akte geht.
4. **Erst danach** weitere Erkennungsarbeit (Reihenfolge-Validator,
   Library-Zeilen aus der Miss-Taxonomie).

Punkt 4 zuletzt, nicht zuerst: 79 % eines Berichts, den ein Prüfer als seinen
eigenen Prozess erkennt, sind mehr wert als 85 % eines Feeds, den er
übersetzen muss.
