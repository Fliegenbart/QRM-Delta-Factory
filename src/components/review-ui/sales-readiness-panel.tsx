import {
  AlertCircle,
  CheckCircle2,
  ClipboardCheck,
  FileCheck2,
  Library,
  LockKeyhole,
  Route,
  ShieldCheck,
} from "lucide-react";

const offerPoints = [
  {
    title: "Was der Kunde kauft",
    body: "Eine KI-gestützte Prüfmappe für QA, RA und SME: Dokumente werden strukturiert, Belege geprüft, Widersprüche sichtbar gemacht und offene Entscheidungen vorbereitet.",
  },
  {
    title: "Was ausdrücklich nicht verkauft wird",
    body: "Keine autonome Freigabe, keine Behörden- oder Notified-Body-Simulation, keine regulatorische Garantie und kein Ersatz für qualifizierte QA-/RA-Verantwortung.",
  },
  {
    title: "Warum das glaubwürdig ist",
    body: "Unterlagen rein. Prüfmappe raus. Mensch entscheidet. Kein Befund ohne belastbaren Beleg. Keine Entlastung ohne geprüfte Evidenz.",
  },
];

const trustLadder = [
  ["1", "Ringversuch", "Gemessen mit präparierten synthetischen Fällen und Kontrollstellen.", "Erreicht"],
  ["2", "Kunden-Blindtest-Kit", "Kunde kennt die Musterlösung, das System nicht.", "Bereit"],
  ["3", "Historische Fälle", "Abgeschlossene echte Fälle werden blind gegen bekannte Ergebnisse geprüft.", "Nächster Schritt"],
  ["4", "Begleiteter Pilot", "Parallelbetrieb ohne autonome Entscheidung und mit QA-Abnahme.", "Geplant"],
  ["5", "Kontrollierter Regelbetrieb", "Erst nach SOP, Training, Audit Trail, Monitoring und Freigabe im Kundensystem.", "Gate"],
] as const;

const goNoGoGates = [
  ["Intended Use", "Tool bereitet Review Packs vor, keine QA-Freigabe.", "bereit"],
  ["Human Review", "High/Critical, fehlende Evidenz und Unsicherheit erzwingen menschliche Entscheidung.", "bereit"],
  ["Datenroute", "Echte Kundendaten nur nach Datenschutzreview, Tenant, Zugriffsschutz und Freigabe.", "gate"],
  ["Regelpakete", "Kundenspezifische SOPs und Knowledge Packs müssen versioniert eingebunden werden.", "gate"],
  ["Validierung", "Ringversuch ist vorhanden; Blindtest und kundenseitige UAT sind vor Produktivbetrieb nötig.", "gate"],
] as const;

const pilotPack = [
  "Kunden-Blindtest-Kit mit Anleitung, Bewertungsmatrix und Abschlussbericht",
  "Datenroute: anonymisierte oder synthetische Unterlagen zuerst, echte Kundendaten nur nach Freigabe",
  "Go/No-Go-Gates für Pilot, Paid Pilot und kontrollierten Regelbetrieb",
  "Review-Pack-Output mit Befunden, Belegen, Nachweislücken und Human Decision Points",
  "Abschlussbericht mit Treffern, Fehlalarmen, übersehenen Findings und nächsten CAPA-/Verbesserungsschritten",
];

export function SalesReadinessPanel() {
  return (
    <div className="space-y-8">
      <section className="border-b border-[var(--border-default)] pb-8">
        <div className="max-w-4xl">
          <div className="text-[11px] font-medium uppercase tracking-[0.18em] text-[var(--brand)]">
            Kundenpilot & Verkauf
          </div>
          <h2 className="mt-3 text-[30px] font-semibold leading-tight text-[var(--text-primary)] md:text-[42px]">
            Verkaufbar als belegte Prüfvorbereitung, nicht als KI-Freigabe.
          </h2>
          <p className="mt-4 max-w-3xl text-[15px] leading-7 text-[var(--text-secondary)]">
            Die QRM Delta Factory verkauft keine Scheinsicherheit. Sie verkauft schnellere,
            belegtere und auditfähigere Entscheidungsvorbereitung: Quellen, Regeln,
            Widersprüche, Nachweislücken und klare Human-Review-Punkte.
          </p>
        </div>
      </section>

      <section className="grid gap-3 lg:grid-cols-3">
        {offerPoints.map((point) => (
          <div
            key={point.title}
            className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] p-4"
          >
            <FileCheck2 className="h-4 w-4 text-[var(--brand)]" aria-hidden />
            <h3 className="mt-3 text-[14px] font-medium text-[var(--text-primary)]">
              {point.title}
            </h3>
            <p className="mt-1.5 text-[12px] leading-6 text-[var(--text-secondary)]">
              {point.body}
            </p>
          </div>
        ))}
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <div>
          <SectionHeader
            icon={Route}
            title="Trust Ladder"
            description="So wird aus einer Demo ein kontrollierter Pilot und später ein belastbarer Regelbetrieb."
          />
          <ol className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)]">
            {trustLadder.map(([index, title, body, status]) => (
              <li
                key={title}
                className="grid gap-3 border-b border-[var(--border-default)] p-4 last:border-b-0 sm:grid-cols-[40px_1fr_auto]"
              >
                <div className="mono grid h-8 w-8 place-items-center rounded bg-[var(--brand-soft)] text-[12px] font-medium text-[var(--brand-strong)]">
                  {index}
                </div>
                <div>
                  <div className="text-[13px] font-medium text-[var(--text-primary)]">{title}</div>
                  <div className="mt-1 text-[12px] leading-5 text-[var(--text-secondary)]">
                    {body}
                  </div>
                </div>
                <span className="h-fit rounded border border-[var(--border-default)] bg-[var(--surface-secondary)] px-2 py-1 text-[11px] font-medium text-[var(--text-secondary)]">
                  {status}
                </span>
              </li>
            ))}
          </ol>
        </div>

        <div>
          <SectionHeader
            icon={ShieldCheck}
            title="Go/No-Go-Gates"
            description="Diese Gates verhindern, dass ein Verkaufsgespräch wie eine regulatorische Freigabe klingt."
          />
          <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)]">
            {goNoGoGates.map(([title, body, state]) => (
              <div
                key={title}
                className="flex gap-3 border-b border-[var(--border-default)] p-4 last:border-b-0"
              >
                {state === "bereit" ? (
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-success-600" />
                ) : (
                  <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
                )}
                <div>
                  <div className="text-[13px] font-medium text-[var(--text-primary)]">{title}</div>
                  <div className="mt-1 text-[12px] leading-5 text-[var(--text-secondary)]">
                    {body}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] p-5">
          <SectionHeader
            icon={LockKeyhole}
            title="Datenroute"
            description="Für echte Kundendokumente braucht das Tool eine klare Betriebsgrenze."
          />
          <div className="space-y-3 text-[12px] leading-6 text-[var(--text-secondary)]">
            <p>
              Demo und erster Pilot laufen mit synthetischen, anonymisierten oder kundenseitig
              freigegebenen Unterlagen. Echte vertrauliche Dokumente kommen erst nach
              Datenschutzreview, Zugriffsschutz, Tenant-Trennung, Löschkonzept und
              Anbieterfreigabe in den Prozess.
            </p>
            <p>
              Externe KI-Provider werden nicht stillschweigend aktiviert. Datenroute,
              Modellanbieter, Speicherorte und Löschregeln werden vor dem Pilot schriftlich
              bestätigt.
            </p>
          </div>
        </div>

        <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] p-5">
          <SectionHeader
            icon={ClipboardCheck}
            title="Pilotpaket"
            description="Was du einem Kunden als bezahlbaren, kontrollierten Einstieg anbieten kannst."
          />
          <ul className="grid gap-2">
            {pilotPack.map((item) => (
              <li
                key={item}
                className="flex gap-2 rounded border border-[var(--border-muted)] bg-[var(--surface-secondary)] p-3 text-[12px] leading-5 text-[var(--text-secondary)]"
              >
                <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-[var(--brand)]" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] p-5">
        <SectionHeader
          icon={Library}
          title="Nächste Produktisierung"
          description="Damit aus dem Pilot ein wiederholbarer Verkauf wird."
        />
        <div className="grid gap-3 md:grid-cols-3">
          <ProductizationStep
            title="1. Regelpakete"
            body="SOP-to-Rule-Pack Compiler und Knowledge-Pack-Register für kundenspezifische Anforderungen."
          />
          <ProductizationStep
            title="2. Validierung"
            body="Intended Use, URS, Risk File, Testprotokoll, Ringversuch, Blindtest und UAT-Bericht."
          />
          <ProductizationStep
            title="3. Betrieb"
            body="Tenant, Zugriff, Audit Trail, Monitoring-KPIs, CAPA für KI-Fehler und Periodic Review."
          />
        </div>
      </section>
    </div>
  );
}

function SectionHeader({
  icon: Icon,
  title,
  description,
}: {
  icon: typeof ShieldCheck;
  title: string;
  description: string;
}) {
  return (
    <div className="mb-3">
      <div className="flex items-center gap-2 text-[11px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
        <Icon className="h-3.5 w-3.5" aria-hidden />
        {title}
      </div>
      <p className="mt-1 max-w-2xl text-[12px] leading-5 text-[var(--text-secondary)]">
        {description}
      </p>
    </div>
  );
}

function ProductizationStep({ title, body }: { title: string; body: string }) {
  return (
    <div className="border-l border-[var(--border-default)] pl-3">
      <h3 className="text-[13px] font-medium text-[var(--text-primary)]">{title}</h3>
      <p className="mt-1 text-[12px] leading-5 text-[var(--text-secondary)]">{body}</p>
    </div>
  );
}
