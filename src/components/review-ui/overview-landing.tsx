"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight,
  CheckCircle2,
  FlaskConical,
  Quote,
  UserCheck,
  type LucideIcon,
} from "lucide-react";

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
                Die Prüfung machen Sie.
                <br />
                <span className="text-[var(--brand-strong)]">
                  Das Zusammentragen macht das Tool.
                </span>
              </h2>
              <p className="mt-5 text-[15px] leading-7 text-[var(--text-secondary)]">
                Aus einem Stapel Change-, Abweichungs- und CAPA-Unterlagen wird eine
                Prüfmappe: jede Aussage mit Fundstelle, jeder Widerspruch markiert, jeder
                fehlende Pflichtnachweis benannt. Sie lesen nicht mehr alles — Sie
                entscheiden über das, was zählt.
              </p>
            </div>
            <FindingArtifact />
          </div>
          <Link
            href="/ringversuch"
            className="group mt-8 inline-flex flex-wrap items-baseline gap-x-2 gap-y-1 border-t border-[var(--border-default)] pt-4 text-[13px] text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
          >
            <span className="font-medium text-[var(--text-primary)]">
              Im Ringversuch belegt:
            </span>
            <span>24 von 25 versteckten Fehlern gefunden</span>
            <span aria-hidden>·</span>
            <span>0 Fehlalarme</span>
            <span aria-hidden>·</span>
            <span>93 % der Befunde mit wörtlich geprüftem Zitat</span>
            <span className="inline-flex items-center gap-1 font-medium text-[var(--brand-strong)] group-hover:underline">
              Zum Nachweis
              <ArrowRight className="h-3.5 w-3.5" aria-hidden />
            </span>
          </Link>
        </div>
      </Reveal>

      {/* Das Problem */}
      <Reveal delay={0.1}>
        <section>
          <LandingHeading
            title="Der teuerste Teil eines Reviews ist der langweiligste."
            description="Bevor ein Fall überhaupt bewertet werden kann, geht Stunden drauf: Unterlagen sichten, Aussagen gegen das Regelwerk halten, prüfen ob jeder Pflichtnachweis da ist, Widersprüche zwischen Dokumenten finden. Diese Arbeit ist nötig, aber sie verlangt keine Expertise — sie verlangt Geduld. Und genau hier rutscht im Zweifel etwas durch: ein fehlender Labornachweis, eine Klassifizierung, die die Daten nicht hergeben, ein Zitat, das im Original anders steht."
          />
        </section>
      </Reveal>

      {/* So arbeitet das System */}
      <Reveal delay={0.15}>
        <section>
          <LandingHeading
            title="Vom Dokumentenstapel zur entscheidungsreifen Mappe — in drei Schritten."
            description="Das Tool nimmt die Fleißarbeit aus dem Review und legt Ihnen die entscheidenden Stellen geordnet vor."
          />
          <div className="grid gap-3 sm:grid-cols-3">
            <StepCard
              number="01"
              title="Lesen und belegen"
              body="Jedes Dokument wird in einzelne, zitierfähige Aussagen zerlegt. Jede behält ihre Fundstelle: Dokument, Seite, wörtliches Zitat. Nichts wird zusammengefasst, ohne dass Sie zur Quelle zurückspringen können."
            />
            <StepCard
              number="02"
              title="Prüfen und aufdecken"
              body="Sieben unabhängige Prüfinstanzen gehen die Unterlagen gegen Ihr Regelwerk durch — Datenintegrität, Abweichung, CAPA, Chargenbezug, Validierung, regulatorische Konsistenz, Widersprüche."
            />
            <StepCard
              number="03"
              title="Vorlegen, nicht entscheiden"
              body="Sie bekommen eine Mappe mit Befunden, Zitaten und offenen Fragen. Klare Fälle sind als klar markiert, kritische und unklare wandern immer auf Ihren Tisch. Das System schließt nichts im Stillen ab."
            />
          </div>
        </section>
      </Reveal>

      {/* Warum vertrauen */}
      <Reveal delay={0.2}>
        <section>
          <LandingHeading
            title="Drei Gründe, warum das hier kein KI-Versprechen ist."
            description="Die Prüfmappe soll nicht beeindrucken, sondern prüfbar bleiben: mit Originalzitaten, klarer Eskalation und wiederholbaren Messungen."
          />
          <div className="space-y-3">
            <PrincipleRow
              icon={Quote}
              title="Kein Befund ohne Beleg"
              body="Jeder Befund muss eine wörtliche Stelle aus dem Originaldokument nennen. Diese Stelle wird Zeichen für Zeichen gegen die Quelle geprüft — nicht von einer KI, sondern von festem Programmcode. Was sich nicht wörtlich belegen lässt, kommt gar nicht erst in die Mappe. Ob der Beleg die Schlussfolgerung trägt, entscheiden Sie — das Zitat steht einen Klick entfernt im Original."
            />
            <PrincipleRow
              icon={UserCheck}
              title="Im Zweifel: Mensch"
              body="Ist die Beleglage dünn oder fällt eine Prüfinstanz aus, gibt das System den Fall nie automatisch frei. Es sagt offen, wo ein Mensch hinschauen muss. Das ist fest eingebaut, nicht abschaltbar."
            />
            <PrincipleRow
              icon={FlaskConical}
              title="Gemessen, nicht behauptet"
              body="Das System wird regelmäßig mit präparierten Fällen getestet, deren Fehler vorab dokumentiert und versiegelt sind — wie ein Ringversuch im Labor. So ist nachweisbar, was es findet, was es übersieht, und dass es bei sauberen Unterlagen ruhig bleibt."
            />
          </div>
        </section>
      </Reveal>

      {/* Die Zahlen */}
      <Reveal delay={0.25}>
        <section>
          <LandingHeading
            title="Das letzte Ergebnis im Detail."
            description="Stand 11.06.2026, aus den Messdaten des letzten abgeschlossenen Laufs."
          />
          <div className="rounded-md border border-[var(--border-default)] bg-[var(--brand-soft)] p-5">
            <div className="grid gap-6 sm:grid-cols-3">
              <LiveStat value="24 von 25" label="versteckten Fehlern gefunden" />
              <LiveStat value="0" label="Fehlalarme bei 11 bewusst harmlosen Kontrollstellen" />
              <LiveStat value="93 %" label="der Befunde mit wörtlich geprüftem Zitat" />
            </div>
            <Link
              href="/ringversuch"
              className="mt-5 inline-flex items-center gap-1.5 text-[13px] font-medium text-[var(--brand-strong)] hover:underline"
            >
              Zum vollständigen Nachweis
              <ArrowRight className="h-3.5 w-3.5" aria-hidden />
            </Link>
            <div className="mt-1 text-[11px] text-[var(--text-tertiary)]">
              Der vollständige Lauf ist im Qualifizierungsnachweis einsehbar.
            </div>
          </div>
        </section>
      </Reveal>

      {/* Vertrauensstufen */}
      <Reveal delay={0.3}>
        <section>
          <LandingHeading
            title="Vertrauen in Stufen — jede mit einem prüfbaren Kriterium."
            description="Der nächste sinnvolle Schritt ist kein Sprung in den Produktivbetrieb, sondern ein Blindtest mit Ihren Fällen."
          />
          <ol className="relative space-y-0">
            <LadderStep
              index={1}
              state="done"
              title="Ringversuch"
              body="Zehn realistische GMP-Fälle mit bewusst versteckten Fehlern. 24 von 25 gefunden, null Fehlalarme."
              status="Erreicht"
            />
            <LadderStep
              index={2}
              state="ready"
              title="Blindtest mit Ihren Fällen"
              invitation="Der Schritt, den wir heute vorschlagen."
              body="Sie bauen Testfälle nach unserer Anleitung und behalten die Lösungen. Das System sieht sie zum ersten Mal im Lauf. Sie bewerten gegen Ihre eigene Lösung — Ihre Kriterien, Ihr Tempo. Aufwand: ein bis zwei Expertentage."
              status="Vorgeschlagen"
            />
            <LadderStep
              index={3}
              state="planned"
              title="Echte abgeschlossene Fälle"
              body="Ältere, vollständig dokumentierte Vorgänge mit bekanntem Ausgang. Das System bewertet blind, verglichen wird gegen die damalige Abschlussbewertung."
              status="Geplant"
            />
            <LadderStep
              index={4}
              state="planned"
              title="Begleiteter Pilot"
              body="Einsatz parallel zum Tagesgeschäft, mit vorab vereinbarten Erfolgskriterien."
              status="Geplant"
              last
            />
          </ol>
        </section>
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
  icon: LucideIcon;
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
