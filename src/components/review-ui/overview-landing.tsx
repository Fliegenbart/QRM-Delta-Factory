"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight,
  CheckCircle2,
  FileSearch,
  FlaskConical,
  Quote,
  Scale,
  UserCheck,
} from "lucide-react";
import {
  OVERVIEW_FALLBACK_STATS,
  selectOverviewRingversuchStats,
  type OverviewRingversuchStats,
} from "@/src/lib/ringversuch-overview-stats";

/* ----- Live-Kennzahlen aus dem Ringversuch ----- */

function useRingversuchStats(): OverviewRingversuchStats {
  const [stats, setStats] = useState<OverviewRingversuchStats>(OVERVIEW_FALLBACK_STATS);
  useEffect(() => {
    let cancelled = false;
    fetch("/api/ringversuch")
      .then((response) => (response.ok ? response.json() : null))
      .then((payload) => {
        if (cancelled) return;
        setStats(selectOverviewRingversuchStats(payload));
      })
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, []);
  return stats;
}

function formatCitationRate(rate: number | null): string {
  if (rate == null) return "-";
  return `${(Math.round(rate * 1000) / 10).toLocaleString("de-DE")} %`;
}

function formatFalseAlarms(count: number): string {
  return count === 0 ? "null" : count.toLocaleString("de-DE");
}

/* ----- Animation ----- */

const reveal = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
};

function Reveal({ delay, children }: { delay: number; children: React.ReactNode }) {
  return (
    <motion.div
      variants={reveal}
      initial="initial"
      animate="animate"
      transition={{ duration: 0.45, delay, ease: [0.21, 0.65, 0.36, 1] }}
    >
      {children}
    </motion.div>
  );
}

/* ----- Hauptkomponente ----- */

export function OverviewLanding() {
  const stats = useRingversuchStats();
  const latest = stats.latest;
  const best = stats.best;
  const latestFalseAlarms = latest.decoysTotal - latest.decoysPassed;
  const bestFalseAlarms = best.decoysTotal - best.decoysPassed;
  const latestCitationRate = formatCitationRate(latest.citationRate);
  const bestRunSummary = stats.hasBetterBestRun
    ? `Bester bestätigter Lauf: ${best.sensitivityFound} von ${best.sensitivityTotal} Fehlern gefunden, ${formatFalseAlarms(bestFalseAlarms)} Fehlalarme.`
    : "Der jüngste vollständige Lauf ist zugleich der beste bestätigte Lauf.";

  return (
    <div className="mx-auto max-w-4xl space-y-16 pb-8">
      {/* Hero */}
      <Reveal delay={0}>
        <div className="pt-4">
          <div className="grid items-center gap-10 lg:grid-cols-[minmax(0,1fr)_340px]">
            <div>
              <div className="text-[11px] font-medium uppercase tracking-[0.2em] text-[var(--text-tertiary)]">
                Pharma QRM Delta Engine
              </div>
              <h2 className="mt-3 text-[32px] font-semibold leading-[1.15] tracking-[-0.01em] text-[var(--text-primary)] sm:text-[40px]">
                KI bereitet vor.
                <br />
                <span className="text-[var(--brand-strong)]">Die QA entscheidet.</span>
              </h2>
              <p className="mt-5 text-[15px] leading-7 text-[var(--text-secondary)]">
                Das System liest Change-, Abweichungs- und CAPA-Unterlagen, findet
                Widersprüche, Fehlklassifizierungen und fehlende Pflichtnachweise — und
                legt der Qualitätssicherung eine vollständig belegte Prüfmappe vor. Es
                spart die Such- und Sortierarbeit, nicht das Urteil: Jede Entscheidung
                bleibt beim Menschen.
              </p>
            </div>
            <FindingArtifact />
          </div>
          <Link
            href="/ringversuch"
            className="group mt-8 inline-flex flex-wrap items-baseline gap-x-2 gap-y-1 border-t border-[var(--border-default)] pt-4 text-[13px] text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
          >
            <span className="font-medium text-[var(--text-primary)]">
              Jüngster vollständiger Ringversuch:
            </span>
            <span>
              {latest.sensitivityFound} von {latest.sensitivityTotal} versteckten Fehlern
              gefunden
            </span>
            <span aria-hidden>·</span>
            <span>{latestFalseAlarms} Fehlalarme</span>
            <span aria-hidden>·</span>
            <span>{latestCitationRate} belegte Befunde</span>
            {stats.hasBetterBestRun ? (
              <>
                <span aria-hidden>·</span>
                <span>
                  bester bestätigter Lauf: {best.sensitivityFound} von {best.sensitivityTotal} gefunden
                </span>
              </>
            ) : null}
            <span className="inline-flex items-center gap-1 font-medium text-[var(--brand-strong)] group-hover:underline">
              Zum Nachweis
              <ArrowRight className="h-3.5 w-3.5" aria-hidden />
            </span>
          </Link>
        </div>
      </Reveal>

      {/* So arbeitet das System */}
      <Reveal delay={0.1}>
        <section>
          <LandingHeading
            title="So arbeitet das System"
            description="Drei Schritte — vom Dokumentenstapel zur entscheidungsreifen Prüfmappe."
          />
          <div className="grid gap-3 sm:grid-cols-3">
            <StepCard
              number="01"
              title="Lesen & belegen"
              body="Jedes Dokument wird in zitierfähige Einzelaussagen zerlegt. Jede Aussage behält ihre Fundstelle: Dokument, Seite, wörtliches Zitat."
            />
            <StepCard
              number="02"
              title="Prüfen & aufdecken"
              body="Sieben unabhängige KI-Prüfer analysieren die Unterlagen gegen Ihr Regelwerk. Zwei KI-Kritiker auf Modellen anderer Hersteller suchen nach Übersehenem; eine regelbasierte Gegenprüfung stellt jeden Befund infrage."
            />
            <StepCard
              number="03"
              title="Vorlegen, nicht entscheiden"
              body="Das Ergebnis ist eine Prüfmappe mit Befunden, Zitaten und offenen Fragen. Unklare oder kritische Fälle gehen immer an die QA — ohne Ausnahme."
            />
          </div>
        </section>
      </Reveal>

      {/* Warum vertrauen */}
      <Reveal delay={0.2}>
        <section>
          <LandingHeading
            title="Warum man dem System vertrauen kann"
            description="Drei Prinzipien gegen das berechtigte Misstrauen gegenüber KI im Compliance-Umfeld."
          />
          <div className="space-y-3">
            <PrincipleRow
              icon={Quote}
              title="Kein Befund ohne Zitat"
              body="Jeder Befund muss eine wörtliche Textstelle aus den Originalunterlagen benennen. Das Zitat wird maschinell Zeichen für Zeichen gegen das Quelldokument geprüft: Halluzinierte oder verfälschte Belege werden verworfen, bevor sie in die Prüfmappe gelangen. Ob die Schlussfolgerung aus einem echten Beleg trägt, bewertet die QA — dafür steht jedes Zitat einen Klick entfernt im Originalkontext."
            />
            <PrincipleRow
              icon={UserCheck}
              title="Im Zweifel: Mensch"
              body="Fällt ein KI-Baustein aus oder ist die Beleglage dünn, gibt das System den Fall niemals automatisch frei. Es sagt offen: Hier muss ein Mensch prüfen. Dieses Verhalten ist fest eingebaut, nicht konfigurierbar."
            />
            <PrincipleRow
              icon={FlaskConical}
              title="Gemessen, nicht behauptet"
              body="In Anlehnung an Ringversuche aus der Laborpraxis wird das System regelmäßig mit präparierten Fällen getestet, deren versteckte Fehler vorab dokumentiert und versiegelt sind. So ist belegbar, was es findet, was es übersieht — und dass es bei fehlerfreien Unterlagen ruhig bleibt."
            />
          </div>

          {/* Live-Kennzahlen */}
          <div className="mt-4 rounded-md border border-[var(--border-default)] bg-[var(--brand-soft)] p-5">
            <div className="grid gap-6 sm:grid-cols-3">
              <LiveStat
                value={`${latest.sensitivityFound} von ${latest.sensitivityTotal}`}
                label="im jüngsten vollständigen Ringversuch"
              />
              <LiveStat
                value={`${latestFalseAlarms}`}
                label={`Fehlalarme bei ${latest.decoysTotal} harmlosen Kontrollstellen`}
              />
              <LiveStat
                value={
                  latest.citationRate != null
                    ? `${(Math.round(latest.citationRate * 1000) / 10).toLocaleString("de-DE")} %`
                    : "-"
                }
                label="der Befunde mit wortwörtlich geprüftem Zitat"
              />
            </div>
            <Link
              href="/ringversuch"
              className="mt-5 inline-flex items-center gap-1.5 text-[13px] font-medium text-[var(--brand-strong)] hover:underline"
            >
              Zum vollständigen Qualifizierungsnachweis
              <ArrowRight className="h-3.5 w-3.5" aria-hidden />
            </Link>
            <div className="mt-1 text-[11px] text-[var(--text-tertiary)]">
              Werte aus dem jüngsten vollständigen Ringversuchslauf (Stand: {latest.standDate}).
              {` ${bestRunSummary} `}
              Die Zahlen stammen direkt aus den Messdaten; der vollständige Lauf inklusive
              aller Fälle ist im Qualifizierungsnachweis einsehbar.
            </div>
          </div>
        </section>
      </Reveal>

      {/* Vertrauensleiter */}
      <Reveal delay={0.3}>
        <section>
          <LandingHeading
            title="Die nächsten Schritte: eine Vertrauensleiter"
            description="Vertrauen entsteht stufenweise — jede Stufe hat ein überprüfbares Kriterium, bevor die nächste beginnt."
          />
          <ol className="relative space-y-0">
            <LadderStep
              index={1}
              state="done"
              title="Ringversuch mit präparierten Fällen"
              body={`Zehn realistische GMP-Fälle mit bewusst versteckten Fehlern. Stand ${latest.standDate}: im jüngsten vollständigen Lauf ${latest.sensitivityFound} von ${latest.sensitivityTotal} Fehlern gefunden; ${bestRunSummary}`}
              status="Erreicht"
            />
            <LadderStep
              index={2}
              state="ready"
              title="Blindtest mit Ihren eigenen Fällen"
              invitation="Das ist der Schritt, den wir Ihnen heute vorschlagen."
              body="Ihre Experten erstellen Testfälle nach unserer Anleitung und behalten die Musterlösungen. Wir sehen die Fälle zum ersten Mal beim Testlauf. Sie bewerten das Ergebnis gegen Ihre eigene Lösung — zu Ihren Kriterien, in Ihrem Tempo. Aufwand auf Ihrer Seite: erfahrungsgemäß ein bis zwei Expertentage."
              status="Bereit zum Start"
            />
            <LadderStep
              index={3}
              state="planned"
              title="Bewährungsprobe an echten, abgeschlossenen Fällen"
              body="Einige Jahre alte, vollständig dokumentierte Vorgänge mit bekanntem Ausgang. Das System bewertet sie blind; verglichen wird gegen die seinerzeit dokumentierten Abschlussbewertungen und das, was Ihre Berater aus der Fallarbeit ergänzen können."
              status="Geplant"
            />
            <LadderStep
              index={4}
              state="planned"
              title="Begleiteter Pilot im Tagesgeschäft"
              body="Einsatz parallel zur normalen Arbeit, mit vorab gemeinsam vereinbarten Erfolgskriterien — wie bei einer klinischen Studie mit definierten Endpunkten."
              status="Geplant"
              last
            />
          </ol>
        </section>
      </Reveal>

      {/* KI-Transparenz */}
      <Reveal delay={0.35}>
        <section>
          <LandingHeading
            title="Welche KI hier arbeitet — und wo Ihre Daten bleiben"
            description="Transparenz über Modelle, Datenwege und den Umgang mit der Natur von KI-Systemen."
          />
          <div className="space-y-3">
            <TransparencyBlock
              title="Modelle — protokolliert bis auf den einzelnen Befund"
              body="Die Hauptprüfung — Aussagen-Extraktion und alle sieben Fach-Reviewer — übernimmt Mistral Large des europäischen Anbieters Mistral AI (Paris). Als KI-Kritiker kontrollieren Claude (Anthropic) und GPT (OpenAI) die Ergebnisse; alternativ läuft das System vollständig auf europäischen Modellen — beide Konfigurationen sind im Ringversuch gemessen. Zu jedem Befund wird festgehalten, welches Modell ihn in welcher Version mit welchem Prüfauftrag erstellt hat, abgesichert über eine lückenlos verkettete Audit-Spur."
            />
            <TransparencyBlock
              title="Die Zitatprüfung ist bewusst keine KI"
              body="Ob ein Zitat wirklich im Original steht, prüft deterministischer Programmcode — Zeichen für Zeichen gegen das Quelldokument, kryptografisch protokolliert. Gleicher Input, garantiert gleiches Ergebnis: An dieser Stelle gibt es nichts zu halluzinieren."
            />
            <TransparencyBlock
              title="Datenverarbeitung"
              body="Die Modell-Anbieter verwenden übermittelte Inhalte gemäß ihren API-Bedingungen nicht zum Training. Für alle Tests werden ausschließlich synthetische oder anonymisierte Unterlagen verwendet — die Blindtest-Anleitung deckt das ab. Für einen Pilotbetrieb mit echten Unterlagen wird die Datenroute vorab gemeinsam festgelegt; die vollständig europäische Konfiguration ist bereits heute gemessen und einsatzbereit."
            />
            <TransparencyBlock
              title="Verlässlichkeit trotz Streuung"
              body="KI-Ausgaben sind nicht vollständig deterministisch. Das System begegnet dem dreifach: Alle Modelle laufen mit minimaler Zufallsstreuung; neun unabhängige Prüfer mit unterschiedlichen Blickwinkeln ersetzen die einzelne Meinung; und die Zusammenführung ist bewusst konservativ — ein einmal gefundener Befund wird nie per Mehrheitsentscheid weggestimmt. Die verbleibende Streuung wird nicht versteckt: Wiederholte Ringversuchsläufe machen sie sichtbar und sind im Qualifizierungsnachweis einsehbar."
            />
          </div>
        </section>
      </Reveal>

      {/* Grenzen */}
      <Reveal delay={0.4}>
        <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-secondary)] p-5">
          <div className="flex items-center gap-2 text-[12px] font-medium uppercase tracking-[0.14em] text-[var(--text-tertiary)]">
            <Scale className="h-3.5 w-3.5" aria-hidden />
            Was das System ausdrücklich nicht tut
          </div>
          <p className="mt-2 max-w-3xl text-[13px] leading-6 text-[var(--text-secondary)]">
            Es trifft keine regulatorischen Entscheidungen, ersetzt keine qualifizierte
            Risikobewertung und keine QA-Verantwortung. Es ist ein Prototyp: Ein produktiver
            Einsatz erfordert formale Validierung, SOPs und die Freigabe im Qualitätssystem
            des Anwenders. Genau dafür ist die Vertrauensleiter da.
          </p>
        </div>
      </Reveal>
    </div>
  );
}

/* ----- Bausteine ----- */

function FindingArtifact() {
  return (
    <div aria-hidden className="hidden select-none lg:block">
      <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] p-4 shadow-[0_1px_2px_rgba(23,32,38,0.06)]">
        <div className="flex items-center justify-between gap-2">
          <span className="rounded border border-amber-200 bg-amber-50 px-1.5 py-0.5 text-[10.5px] font-medium uppercase tracking-[0.08em] text-amber-700 dark:border-amber-800 dark:bg-amber-900/30 dark:text-amber-300">
            Befund · Hoch
          </span>
          <span className="text-[10.5px] uppercase tracking-[0.1em] text-[var(--text-tertiary)]">
            Prüfmappe
          </span>
        </div>
        <p className="mt-3 text-[13px] font-medium leading-5 text-[var(--text-primary)]">
          Abweichung als „Minor" eingestuft — ohne Labordaten zur Temperaturunterschreitung.
        </p>
        <div className="mt-3 border-l-2 border-[var(--brand-strong)] bg-[var(--surface-secondary)] px-3 py-2">
          <p className="mono text-[11.5px] leading-5 text-[var(--text-secondary)]">
            „Die Abweichung wird als Minor eingestuft, da die Salbe visuell homogen
            blieb …"
          </p>
        </div>
        <div className="mt-2.5 flex items-center justify-between gap-2 text-[11px]">
          <span className="inline-flex items-center gap-1 text-success-600 dark:text-success-400">
            <CheckCircle2 className="h-3 w-3" aria-hidden />
            Zitat wortwörtlich geprüft
          </span>
          <span className="text-[var(--text-tertiary)]">Deviation Report · S. 1</span>
        </div>
        <div className="mt-3 border-t border-[var(--border-default)] pt-2.5 text-[11px] text-[var(--text-tertiary)]">
          Nächster Schritt: QA-Entscheidung — Hochstufung prüfen, Labordaten nachfordern
        </div>
      </div>
    </div>
  );
}

function LandingHeading({ title, description }: { title: string; description: string }) {
  return (
    <div className="mb-4">
      <h3 className="text-[20px] font-semibold tracking-[-0.01em] text-[var(--text-primary)]">
        {title}
      </h3>
      <p className="mt-1 max-w-2xl text-[13px] leading-6 text-[var(--text-secondary)]">
        {description}
      </p>
    </div>
  );
}

function StepCard({ number, title, body }: { number: string; title: string; body: string }) {
  return (
    <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] p-4">
      <div className="mono text-[22px] font-semibold text-[var(--brand-strong)]">{number}</div>
      <div className="mt-2 text-[14px] font-medium text-[var(--text-primary)]">{title}</div>
      <p className="mt-1.5 text-[12.5px] leading-6 text-[var(--text-secondary)]">{body}</p>
    </div>
  );
}

function PrincipleRow({
  icon: Icon,
  title,
  body,
}: {
  icon: typeof FileSearch;
  title: string;
  body: string;
}) {
  return (
    <div className="flex gap-4 rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] p-4">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-[var(--brand-soft)]">
        <Icon className="h-4.5 w-4.5 text-[var(--brand-strong)]" aria-hidden />
      </div>
      <div>
        <div className="text-[14px] font-medium text-[var(--text-primary)]">{title}</div>
        <p className="mt-1 max-w-2xl text-[12.5px] leading-6 text-[var(--text-secondary)]">
          {body}
        </p>
      </div>
    </div>
  );
}

function TransparencyBlock({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] p-4">
      <div className="text-[13.5px] font-medium text-[var(--text-primary)]">{title}</div>
      <p className="mt-1 max-w-3xl text-[12.5px] leading-6 text-[var(--text-secondary)]">
        {body}
      </p>
    </div>
  );
}

function LiveStat({ value, label }: { value: string; label: string }) {
  return (
    <div>
      <div className="text-[26px] font-semibold leading-none text-[var(--brand-strong)]">
        {value}
      </div>
      <div className="mt-1.5 text-[12px] leading-5 text-[var(--text-secondary)]">{label}</div>
    </div>
  );
}

function LadderStep({
  index,
  state,
  title,
  invitation,
  body,
  status,
  last,
}: {
  index: number;
  state: "done" | "ready" | "planned";
  title: string;
  invitation?: string;
  body: string;
  status: string;
  last?: boolean;
}) {
  const badgeClasses =
    state === "done"
      ? "bg-[var(--brand-soft)] text-[var(--brand-strong)] border-transparent"
      : state === "ready"
        ? "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/30 dark:text-amber-300 dark:border-amber-800"
        : "bg-[var(--surface-secondary)] text-[var(--text-tertiary)] border-[var(--border-default)]";
  return (
    <li className="relative flex gap-4 pb-7 last:pb-0">
      {!last ? (
        <span
          className="absolute left-[15px] top-9 bottom-0 w-px bg-[var(--border-default)]"
          aria-hidden
        />
      ) : null}
      <div
        className={`relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border text-[13px] font-semibold ${
          state === "done"
            ? "border-[var(--brand-strong)] bg-[var(--brand-soft)] text-[var(--brand-strong)]"
            : "border-[var(--border-default)] bg-[var(--surface-primary)] text-[var(--text-secondary)]"
        }`}
      >
        {state === "done" ? <CheckCircle2 className="h-4 w-4" aria-hidden /> : index}
      </div>
      <div className="pt-1">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[14px] font-medium text-[var(--text-primary)]">{title}</span>
          <span
            className={`rounded border px-1.5 py-0.5 text-[10.5px] font-medium uppercase tracking-[0.08em] ${badgeClasses}`}
          >
            {status}
          </span>
        </div>
        {invitation ? (
          <div className="mt-0.5 text-[13px] font-medium italic text-[var(--brand-strong)]">
            {invitation}
          </div>
        ) : null}
        <p className="mt-1 max-w-2xl text-[12.5px] leading-6 text-[var(--text-secondary)]">
          {body}
        </p>
      </div>
    </li>
  );
}
