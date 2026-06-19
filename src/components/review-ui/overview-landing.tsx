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
    <div className="mx-auto max-w-4xl space-y-14 pb-8">
      {/* Hero */}
      <Reveal delay={0}>
        <section className="pt-4">
          <div className="grid items-center gap-10 lg:grid-cols-[minmax(0,1fr)_340px]">
            <div>
              <div className="text-[11px] font-medium uppercase tracking-[0.2em] text-[var(--text-tertiary)]">
                Pharma QRM · Delta Engine
              </div>
              <h2 className="mt-3 text-[34px] font-semibold leading-[1.08] tracking-[-0.01em] text-[var(--text-primary)] sm:text-[48px]">
                Endlich eine KI, die nichts behauptet, was sie nicht belegen kann.
              </h2>
              <p className="mt-5 text-[15px] leading-7 text-[var(--text-secondary)]">
                Andere Tools raten weiter und überlassen Ihnen das Aufräumen. Dieses legt
                zu jedem Befund die Quelle — oder hält an und gibt den Fall an Sie. So wird
                aus KI-Output endlich Vorarbeit, die Sie verwenden können.
              </p>
              <div className="mt-6 flex flex-wrap gap-2">
                <a
                  href="#blindtest"
                  className="inline-flex h-10 items-center gap-2 rounded-md bg-[var(--brand)] px-4 text-[13px] font-medium text-white hover:bg-[var(--brand-strong)]"
                >
                  Blindtest starten
                  <ArrowRight className="h-3.5 w-3.5" aria-hidden />
                </a>
                <a
                  href="#how-it-works"
                  className="inline-flex h-10 items-center rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-4 text-[13px] font-medium text-[var(--text-primary)] hover:bg-[var(--surface-secondary)]"
                >
                  Wie es funktioniert
                </a>
              </div>
            </div>
            <FindingArtifact />
          </div>
        </section>
      </Reveal>

      {/* Beweisbalken */}
      <Reveal delay={0.05}>
        <Link
          href="/ringversuch"
          className="group block rounded-md border border-[var(--border-default)] bg-[var(--brand-soft)] p-4 hover:border-[var(--brand)]"
        >
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="text-[11px] font-medium uppercase tracking-[0.16em] text-[var(--brand-strong)]">
                Gemessen, nicht behauptet.
              </div>
              <div className="mt-1 text-[12px] text-[var(--text-secondary)] group-hover:text-[var(--text-primary)]">
                Ringversuch mit präparierten GMP-Fällen und sauberen Kontrollstellen
              </div>
            </div>
            <div className="grid gap-3 text-[12px] sm:grid-cols-3 md:min-w-[420px]">
              <LiveStat value="24 / 25" label="versteckte Fehler gefunden" />
              <LiveStat value="0" label="Fehlalarme" />
              <LiveStat value="93 %" label="belegte Befunde" />
            </div>
          </div>
        </Link>
      </Reveal>

      {/* Was das Tool ist */}
      <Reveal delay={0.1}>
        <section>
          <LandingHeading
            title="Was das Tool ist."
            description="Eine Software, die einen Stapel GMP-Unterlagen liest — Change Control, Abweichung, CAPA, Audit-Findings — und daraus macht, was sonst Stunden Handarbeit kostet: eine geordnete, belegte Prüfmappe."
          />
          <div className="space-y-4 text-[14px] leading-7 text-[var(--text-secondary)]">
            <p>
              Jede Aussage mit Fundstelle, jeder Widerspruch markiert, jeder fehlende
              Pflichtnachweis benannt.
            </p>
            <p>
              Die Risikobewertung nimmt es Ihnen nicht ab. Es bereitet sie vor — Befunde,
              Belege, Lücken, gewichtete Risiken, soweit die Unterlagen sie hergeben. Das
              Urteil bleibt Ihres. Die Fleißarbeit davor nicht.
            </p>
            <p>
              Kein Chatbot, kein Orakel, keine Freigabe-Automatik. Ein Werkzeug, das den
              Fall sortiert und Ihnen vorlegt.
            </p>
          </div>
        </section>
      </Reveal>

      {/* Warum KI hier anders ist */}
      <Reveal delay={0.15}>
        <section>
          <LandingHeading
            title="Warum KI-Risikoanalysen bisher gescheitert sind — und was hier anders ist."
            description="Das Problem war nie die Geschwindigkeit. Es war das Vertrauen."
          />
          <div className="mb-4 space-y-4 text-[14px] leading-7 text-[var(--text-secondary)]">
            <p>
              Was die KI ausgab, musste man von Hand nachprüfen — und sobald man alles
              nachprüft, ist die Ersparnis weg. Eine selbstbewusst formulierte, aber
              falsche Aussage ist schlimmer als gar keine.
            </p>
            <p>
              Dieses Tool ist um genau dieses Problem herum gebaut. Drei Prinzipien — und
              keines davon ist abschaltbar.
            </p>
          </div>
          <div className="space-y-3">
            <PrincipleRow
              icon={Quote}
              title="Belegt, oder es kommt gar nicht durch."
              body="Jedes Zitat prüft fester Code Zeichen für Zeichen gegen das Original — keine KI, kein Ermessen. Was sich nicht belegen lässt, erreicht Ihre Mappe nie. Sie ertappen die Maschine nicht mehr beim Erfinden. Sie bewerten nur noch, was nachweislich dasteht."
            />
            <PrincipleRow
              icon={FlaskConical}
              title="Still, wo nichts ist."
              body="Der eigentliche Zeitfresser sind Fehlalarme — Befunde, die keine sind, einzeln wegzuklicken. Genau darauf wird das System gemessen: null Fehlalarme bei elf sauberen Kontrollstellen. Wo nichts ist, bleibt es still."
            />
            <PrincipleRow
              icon={UserCheck}
              title="Sagt, wenn es nicht weiß."
              body="Bei dünner Beleglage rät es nicht. Es hält an und reicht den Fall weiter — dorthin, wo andere Tools selbstbewussten Unsinn liefern. Das ist keine Schwäche, die wir kaschieren. Das ist der Punkt."
            />
          </div>
          <p className="mt-4 rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-4 py-3 text-[13px] leading-6 text-[var(--text-secondary)]">
            Unterm Strich verschiebt sich Ihr Aufwand: weg vom Kontrollieren der Maschine, hin
            zum Entscheiden des Falls. Nicht weniger Sorgfalt — dieselbe Sorgfalt, an der
            richtigen Stelle.
          </p>
        </section>
      </Reveal>

      {/* Was es kann */}
      <Reveal delay={0.2}>
        <section>
          <LandingHeading
            title="Was es kann."
            description="Change Control · Abweichungen · CAPA · Audit-Findings · Periodic Reviews. Mehrere Dokumente pro Fall. Die Originaldateien bleiben jederzeit die Quelle — nichts wird umgeschrieben, alles bleibt rückverfolgbar."
          />
          <div className="grid gap-3 lg:grid-cols-3">
            <InfoBlock
              title="Was reingeht"
              body="Change Control, Abweichungen, CAPA, Audit-Findings und Periodic Reviews — mehrere Dokumente pro Fall."
            />
            <InfoBlock title="Was es findet">
              <ul className="space-y-1.5">
                <li>Eine Abweichung als „Minor“ eingestuft — ohne die Labordaten, die das tragen würden.</li>
                <li>Eine CAPA mit dokumentierten Maßnahmen, aber offener Wirksamkeitsprüfung.</li>
                <li>Ein Annex-Zitat, das auf Seite 14 anders steht, als der Bericht behauptet.</li>
                <li>Zwei Dokumente, die sich widersprechen, ohne dass es jemandem aufgefallen ist.</li>
              </ul>
            </InfoBlock>
            <InfoBlock
              title="Was rauskommt"
              body="Eine Prüfmappe pro Fall: Befund, belegendes Zitat, offene Lücke, nächster QA-Schritt. Bei sauberen Unterlagen: nichts. Keine erfundene Arbeit."
            />
          </div>
          <p className="mt-3 rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-4 py-3 text-[13px] leading-6 text-[var(--text-secondary)]">
            Was es nicht tut: bewerten, freigeben, Verantwortung übernehmen. Die letzte
            Entscheidung trifft ein Mensch — immer, fest verdrahtet.
          </p>
        </section>
      </Reveal>

      {/* Wie es funktioniert */}
      <Reveal delay={0.25}>
        <section id="how-it-works">
          <LandingHeading
            title="Wie es funktioniert — in drei Schritten."
            description="Vom Dokumentenstapel zur Prüfmappe, ohne dass die Verantwortung an die Maschine wandert."
          />
          <div className="grid gap-3 sm:grid-cols-3">
            <StepCard
              number="01"
              title="Lesen und belegen"
              body="Jedes Dokument wird in einzelne, zitierfähige Aussagen zerlegt. Jede behält ihre Fundstelle: Dokument, Seite, wörtliches Zitat. Sie sind nie mehr als einen Klick von der Quelle entfernt."
            />
            <StepCard
              number="02"
              title="Prüfen und aufdecken"
              body="Sieben unabhängige Prüfinstanzen gehen die Unterlagen gegen Ihr Regelwerk durch — Datenintegrität, Abweichung, CAPA, Chargenbezug, Validierung, regulatorische Konsistenz, Widersprüche. Was eine übersieht, fällt der nächsten auf. Ob ein Zitat wirklich im Original steht, entscheidet hier kein Modell, sondern fester Code."
            />
            <StepCard
              number="03"
              title="Vorlegen, nicht entscheiden"
              body="Heraus kommt die Prüfmappe. Klares ist als klar markiert, Kritisches und Unklares landet auf Ihrem Tisch. Das System schließt nichts im Stillen ab."
            />
          </div>
        </section>
      </Reveal>

      {/* Gemessen */}
      <Reveal delay={0.3}>
        <section>
          <LandingHeading
            title="Gemessen, nicht behauptet."
            description="Wie ein Ringversuch im Labor: präparierte Fälle, deren Fehler vorab dokumentiert und versiegelt sind."
          />
          <div className="rounded-md border border-[var(--border-default)] bg-[var(--brand-soft)] p-5">
            <p className="mb-5 max-w-3xl text-[13px] leading-6 text-[var(--text-secondary)]">
              Das System sieht sie zum ersten Mal im Lauf. Erst danach wird der Umschlag
              geöffnet. So steht schwarz auf weiß, was es findet, was es übersieht — und
              dass es bei fehlerfreien Unterlagen ruhig bleibt.
            </p>
            <div className="grid gap-6 sm:grid-cols-3">
              <LiveStat value="24 von 25" label="versteckten Fehlern gefunden" />
              <LiveStat value="0" label="Fehlalarme bei 11 harmlosen Kontrollstellen" />
              <LiveStat value="93 %" label="der Befunde mit wörtlich geprüftem Zitat" />
            </div>
            <Link
              href="/ringversuch"
              className="mt-5 inline-flex items-center gap-1.5 text-[13px] font-medium text-[var(--brand-strong)] hover:underline"
            >
              Zum vollständigen Nachweis
              <ArrowRight className="h-3.5 w-3.5" aria-hidden />
            </Link>
            <div className="mt-2 max-w-2xl text-[11px] leading-5 text-[var(--text-tertiary)]">
              Stand 11.06.2026, jüngster abgeschlossener Lauf — nicht der beste
              ausgewählte. Vollständig einsehbar im Qualifizierungsnachweis.
            </div>
          </div>
        </section>
      </Reveal>

      {/* Vertrauensstufen */}
      <Reveal delay={0.35}>
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
              body="Zehn GMP-Fälle, bewusst versteckte Fehler. 24 von 25 gefunden, null Fehlalarme."
              status="Erreicht"
            />
            <LadderStep
              index={2}
              state="ready"
              title="Blindtest mit Ihren Fällen"
              invitation="Der Schritt, den wir heute vorschlagen."
              body="Sie bauen die Testfälle, behalten die Lösungen. Das System sieht sie zum ersten Mal im Lauf. Sie bewerten gegen Ihre eigene Lösung — Ihre Kriterien, Ihr Tempo. Aufwand: ein bis zwei Expertentage."
              status="Vorgeschlagen"
            />
            <LadderStep
              index={3}
              state="planned"
              title="Echte abgeschlossene Fälle"
              body="Ältere Vorgänge mit bekanntem Ausgang, blind bewertet, gegen die damalige Abschlussbewertung gehalten."
              status="Geplant"
            />
            <LadderStep
              index={4}
              state="planned"
              title="Begleiteter Pilot"
              body="Parallel zum Tagesgeschäft, mit vorab vereinbarten Erfolgskriterien."
              status="Geplant"
              last
            />
          </ol>
        </section>
      </Reveal>

      {/* Schluss-CTA */}
      <Reveal delay={0.4}>
        <section
          id="blindtest"
          className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] p-5"
        >
          <h3 className="text-[20px] font-semibold tracking-[-0.01em] text-[var(--text-primary)]">
            Der nächste Schritt gehört Ihnen.
          </h3>
          <p className="mt-2 max-w-3xl text-[14px] leading-7 text-[var(--text-secondary)]">
            Sie bauen die Fälle. Sie kennen die Lösung. Wir sehen sie zum ersten Mal im Lauf
            — und Sie sehen, ob das hält, was diese Seite behauptet. Ein bis zwei
            Expertentage. Mehr kostet es Sie nicht, um es zu wissen.
          </p>
          <a
            href="#blindtest"
            className="mt-4 inline-flex h-10 w-fit items-center gap-2 rounded-md bg-[var(--brand)] px-4 text-[13px] font-medium text-white hover:bg-[var(--brand-strong)]"
          >
            Blindtest anfragen
            <ArrowRight className="h-3.5 w-3.5" aria-hidden />
          </a>
        </section>
      </Reveal>

      {/* Fußnote */}
      <Reveal delay={0.45}>
        <section className="border-t border-[var(--border-default)] pt-5">
          <p className="max-w-3xl text-[12px] leading-6 text-[var(--text-tertiary)]">
            Dies ist ein Prototyp. Produktiver Einsatz erfordert formale Validierung, SOPs
            und Freigabe im Qualitätssystem des Anwenders. Genau dafür ist die
            Vertrauensleiter da.
          </p>
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

function InfoBlock({
  title,
  body,
  children,
}: {
  title: string;
  body?: React.ReactNode;
  children?: React.ReactNode;
}) {
  return (
    <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] p-4">
      <div className="text-[13px] font-medium text-[var(--text-primary)]">{title}</div>
      <div className="mt-1.5 text-[12.5px] leading-6 text-[var(--text-secondary)]">
        {children ?? body}
      </div>
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
