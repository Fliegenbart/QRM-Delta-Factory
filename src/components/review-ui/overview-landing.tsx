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

/* ----- Live-Kennzahlen aus dem Ringversuch ----- */

type LiveStats = {
  sensitivityFound: number;
  sensitivityTotal: number;
  decoysPassed: number;
  decoysTotal: number;
  citationRate: number | null;
};

function useRingversuchStats(): LiveStats | null {
  const [stats, setStats] = useState<LiveStats | null>(null);
  useEffect(() => {
    let cancelled = false;
    fetch("/api/ringversuch")
      .then((response) => (response.ok ? response.json() : null))
      .then((payload) => {
        if (cancelled || !payload?.runs) return;
        const latest = payload.runs.find(
          (run: { run?: { mode?: string } }) => run.run?.mode === "live"
        );
        const agg = latest?.aggregate;
        if (!agg?.sensitivity) return;
        setStats({
          sensitivityFound: agg.sensitivity.found,
          sensitivityTotal: agg.sensitivity.total,
          decoysPassed: agg.specificity_decoys?.passed ?? 0,
          decoysTotal: agg.specificity_decoys?.total ?? 0,
          citationRate: agg.citation_precision?.rate ?? null,
        });
      })
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, []);
  return stats;
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

  return (
    <div className="mx-auto max-w-4xl space-y-16 pb-8">
      {/* Hero */}
      <Reveal delay={0}>
        <div className="pt-4">
          <div className="text-[11px] font-medium uppercase tracking-[0.2em] text-[var(--text-tertiary)]">
            Pharma QRM Delta Engine
          </div>
          <h2 className="mt-3 max-w-2xl text-[32px] font-semibold leading-[1.15] tracking-[-0.01em] text-[var(--text-primary)] sm:text-[40px]">
            KI bereitet vor.
            <br />
            <span className="text-[var(--brand-strong)]">Die QA entscheidet.</span>
          </h2>
          <p className="mt-5 max-w-2xl text-[15px] leading-7 text-[var(--text-secondary)]">
            Das System liest Change-, Abweichungs- und CAPA-Unterlagen, findet Risiken,
            Widersprüche und fehlende Pflichtnachweise — und legt der Qualitätssicherung
            eine fertige, vollständig belegte Prüfmappe vor. Es spart die Such- und
            Sortierarbeit, nicht das Urteil: Jede Entscheidung bleibt beim Menschen.
          </p>
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
              body="Mehrere unabhängige KI-Prüfer und zwei KI-Kritiker prüfen gegen Ihr Regelwerk: Widersprüche zwischen Dokumenten, Fehlklassifizierungen, fehlende Pflichtnachweise."
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
              body="Jeder Befund muss eine wörtliche Textstelle aus den Originalunterlagen benennen. Das Zitat wird maschinell gegen das Dokument geprüft — und wer will, prüft in Sekunden selbst nach. Erfundenes fliegt raus, bevor es jemand zu sehen bekommt."
            />
            <PrincipleRow
              icon={UserCheck}
              title="Im Zweifel: Mensch"
              body="Fällt ein KI-Baustein aus oder ist die Beleglage dünn, gibt das System den Fall niemals automatisch frei. Es sagt offen: Hier muss ein Mensch prüfen. Dieses Verhalten ist fest eingebaut, nicht konfigurierbar."
            />
            <PrincipleRow
              icon={FlaskConical}
              title="Gemessen, nicht behauptet"
              body="Wie ein Labor im Ringversuch wird das System regelmäßig mit präparierten Fällen getestet, deren versteckte Fehler vorab feststehen. So ist belegbar, was es findet, was es übersieht — und dass es bei Harmlosem ruhig bleibt."
            />
          </div>

          {/* Live-Kennzahlen */}
          <div className="mt-4 rounded-md border border-[var(--border-default)] bg-[var(--brand-soft)] p-5">
            <div className="grid gap-6 sm:grid-cols-3">
              <LiveStat
                value={stats ? `${stats.sensitivityFound} von ${stats.sensitivityTotal}` : "–"}
                label="versteckten Fehlern gefunden"
              />
              <LiveStat
                value={stats ? `${stats.decoysTotal - stats.decoysPassed}` : "–"}
                label={
                  stats
                    ? `Fehlalarme bei ${stats.decoysTotal} harmlosen Kontrollstellen`
                    : "Fehlalarme"
                }
              />
              <LiveStat
                value={
                  stats?.citationRate != null
                    ? `${(Math.round(stats.citationRate * 1000) / 10).toLocaleString("de-DE")} %`
                    : "–"
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
              Werte aus dem jüngsten Ringversuchslauf — live aus den Messdaten, nicht aus einer
              Präsentation.
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
              body="Zehn realistische GMP-Fälle mit bewusst versteckten Fehlern. Stand heute: 24 von 25 Fehlern gefunden, null Fehlalarme."
              status="Erreicht"
            />
            <LadderStep
              index={2}
              state="ready"
              title="Blindtest mit Ihren eigenen Fällen"
              body="Ihre Experten erstellen Testfälle und behalten die Lösungen. Wir sehen die Fälle zum ersten Mal beim Test — eine Anleitung zum Erstellen liegt bereit."
              status="Bereit zum Start"
            />
            <LadderStep
              index={3}
              state="planned"
              title="Bewährungsprobe an echten, abgeschlossenen Fällen"
              body="Einige Jahre alte Vorgänge, deren Feinheiten Ihre Berater aus eigener Arbeit kennen. Das System tritt gegen das Gedächtnis der Experten an."
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
  body,
  status,
  last,
}: {
  index: number;
  state: "done" | "ready" | "planned";
  title: string;
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
        <p className="mt-1 max-w-2xl text-[12.5px] leading-6 text-[var(--text-secondary)]">
          {body}
        </p>
      </div>
    </li>
  );
}
