# Goldstandard-Testsuite für PharmaQRM Review-System

## Zweck des Goldstandards
Diese Testsuite dient der Evaluierung und Validierung von automatisierten Review-Systemen im regulatorischen GMP-Umfeld (Good Manufacturing Practice). Sie simuliert die reale Komplexität von Qualitätssicherungs-Prüfungen durch synthetische Fallmappen.

## Wichtiger Hinweis zur Verwendung
- **Alle Daten sind vollständig fiktiv:** Sämtliche Firmennamen, Produkte, Chargennummerierungen, Klarnamen und Datumsangaben besitzen keinen Bezug zu realen Entitäten.
- **Isolierung des Lösungsschlüssels:** Die Datei `hidden_errors_answer_key.json` innerhalb der Fallordner sowie die globale `goldstandard_index.csv` enthalten die Ziellösungen. Diese Dateien **dürfen dem zu testenden Review-System nicht als Input übergeben werden**.
- **Test-Methodik:** Dem System sind ausschließlich die `case_summary.md` sowie die enthaltenen `document_*.md`-Dateien bereitzustellen. Die Systemausgaben (Findings/Alarme) müssen anschließend gegen die JSON-Lösungsschlüssel abgeglichen werden, um Sensitivität (True Positive Rate) und Spezifikationstreue (False Positive Rate anhand der eingebauten Decoys) zu bestimmen.

## Struktur der Fälle
- **Einfach (Case 01-03):** Fehler sind isoliert innerhalb eines einzigen Dokuments erkennbar.
- **Mittler (Case 04-07):** Fehler erfordern den direkten Abgleich zwischen zwei Dokumenten derselben Mappe.
- **Schwierig (Case 08-10):** Fehler ergeben sich erst durch logische Verknüpfung mehrerer Dokumenten und die Anwendung tieferer GMP-Regulatorien.
