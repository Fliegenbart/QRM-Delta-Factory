# Change Control CC-IT-2026-011 — LIMS-Migration auf Version 9.2

- **System:** LIMS "LabTrack", GAMP-Kategorie 4 (konfiguriertes Produkt)
- **Antragsteller:** G. Fischer (IT-Systemverantwortlicher)
- **Antragsdatum:** 12.01.2026
- **Klassifizierung:** Major Change (Datenbankmigration, geänderte Audit-Trail-Funktion)

## Beschreibung
Migration der Produktivdatenbank von Version 8.6 auf 9.2 inklusive Übernahme aller Prüfaufträge, Spezifikationen und Benutzerrollen. Während der Migration (Zeitfenster 31.01.2026, 18:00–23:00 Uhr) ist der Audit Trail des Systems deaktiviert; die Migration wird durch ein Migrationsprotokoll dokumentiert.

## Risikobewertung
Hohes Risiko für Datenintegrität während des Migrationsfensters; Mitigation durch vollständiges Backup vor der Migration (Backup-Test am 30.01.2026 erfolgreich, Wiederherstellung in Testumgebung in 47 min) und Datenabgleich (Record Count, Stichproben) nach der Migration.

## Qualifizierung
IQ/OQ gemäß Qualifizierungsplan QP-LIMS-9.2 vor Produktivsetzung; PQ begleitend über 4 Wochen.

- *Erstellt von:* G. Fischer, 12.01.2026
- *Geprüft von (QA-IT):* V. Lang, 14.01.2026
- *Genehmigt (QA-Leitung):* Dr. H. Winter, 16.01.2026
