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
                Ein Werkzeug für QA, RA und SME, das GMP-Unterlagen liest und eine belegte
                Prüfmappe daraus macht — Befunde, Quellen, fehlende Nachweise und der
                nächste Entscheidungsschritt. Sie lesen nicht mehr alles. Sie entscheiden
                über das, was zählt.
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

      {/* Was das Tool ist */}
      <Reveal delay={0.1}>
        <section>
          <LandingHeading
            title="Was das Tool ist."
            description="Es ist eine Software, die einen Stapel GMP-Unterlagen — Change Control, Abweichung, CAPA, Audit-Findings — durchliest und strukturiert, was ein Mensch sonst von Hand sichten müsste."
          />
          <div className="space-y-4 text-[14px] leading-7 text-[var(--text-secondary)]">
            <p>
              Am Ende steht keine Bewertung und keine Freigabe, sondern eine
              entscheidungsreife Prüfmappe: jede Aussage mit Fundstelle, jeder Widerspruch
              markiert, jeder fehlende Pflichtnachweis benannt.
            </p>
            <p>
              Anders gesagt: Sie bekommen die Risikobewertung nicht abgenommen, aber
              vollständig vorbereitet — Befunde, Belege, Nachweislücken und gewichtete
              Risiken, soweit die Unterlagen sie hergeben. Die fachliche Risikoanalyse
              bleibt Ihre; die Vorarbeit dazu liefert das Tool.
            </p>
            <p>
              Es ist kein Chatbot und kein Orakel. Es trifft keine regulatorische
              Entscheidung. Es nimmt die Such-, Sortier- und Abgleicharbeit ab — die Stunden
              vor der eigentlichen Bewertung — und legt dem Experten einen geordneten Fall
              vor.
            </p>
          </div>
        </section>
      </Reveal>

      {/* Warum KI hier anders ist */}
      <Reveal delay={0.15}>
        <section>
          <LandingHeading
            title="Warum KI-Risikoanalysen bisher gescheitert sind — und was hier anders ist."
            description="Das Problem mit KI bei Risikoanalysen war nie die Geschwindigkeit. Es war das Misstrauen."
          />
          <div className="mb-4 space-y-4 text-[14px] leading-7 text-[var(--text-secondary)]">
            <p>
              Was die KI ausgab, ließ sich nicht ohne Weiteres verwenden — also musste man
              alles von Hand nachprüfen. Und sobald man alles nachprüft, ist die
              Zeitersparnis weg. Schlimmer noch: Eine selbstbewusst formulierte, aber
              falsche KI-Aussage ist gefährlicher als gar keine.
            </p>
            <p>
              Dieses Tool ist um genau dieses Problem herum gebaut. Drei Dinge verschieben
              den Kontrollaufwand dorthin, wo er hingehört.
            </p>
          </div>
          <div className="space-y-3">
            <PrincipleRow
              icon={Quote}
              title="Sie prüfen nicht mehr, ob die KI sich etwas ausgedacht hat."
              body="Jeder Befund muss eine wörtliche Stelle aus dem Originaldokument nennen. Diese Stelle wird Zeichen für Zeichen gegen die Quelle abgeglichen — nicht von einer KI, sondern von festem Programmcode. Erfundene oder verfälschte Belege werden aussortiert, bevor die Prüfmappe überhaupt entsteht. Ihre Arbeit ist nicht mehr, die Maschine beim Lügen zu ertappen. Ihre Arbeit ist nur noch, einen echten, belegten Befund fachlich zu bewerten."
            />
            <PrincipleRow
              icon={FlaskConical}
              title="Es meldet keine Phantome."
              body="Der eigentliche Zeitfresser bei anderen Tools sind Fehlalarme — Befunde, die keine sind und die man einzeln wegklicken muss. Genau darauf wird dieses System gemessen: null Fehlalarme bei elf bewusst harmlosen Kontrollstellen. Wo nichts ist, bleibt es still."
            />
            <PrincipleRow
              icon={UserCheck}
              title="Es kennt seine Grenzen und sagt sie."
              body="Wo die Beleglage dünn ist oder eine Prüfung nicht greift, übertüncht das System das nicht mit einer selbstbewussten Antwort. Es sagt offen: Hier muss ein Mensch hinsehen. Das ist das Gegenteil des verwertbar-aussehenden, aber unbrauchbaren Outputs, den Sie kennen."
            />
          </div>
          <p className="mt-4 rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-4 py-3 text-[13px] leading-6 text-[var(--text-secondary)]">
            Unterm Strich verschiebt sich Ihr Aufwand: weg vom Nachprüfen der Maschine, hin
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
            description="Change Control · Abweichungen · CAPA · Audit-Findings · Periodic Reviews. Mehrere Dokumente pro Fall. Die Originaldateien bleiben jederzeit die Quelle."
          />
          <div className="grid gap-3 lg:grid-cols-3">
            <InfoBlock
              title="Was reingeht"
              body="Change Control, Abweichungen, CAPA, Audit-Findings und Periodic Reviews — auch mehrere Dokumente pro Fall."
            />
            <InfoBlock
              title="Was es findet"
              body="Klassifizierungen ohne Beleg, fehlende Pflichtnachweise, Widersprüche zwischen Dokumenten sowie Zitate und Regelbezüge, die im Original anders stehen."
            />
            <InfoBlock
              title="Was rauskommt"
              body="Eine Prüfmappe pro Fall — mit Befunden, belegendem Zitat, offenen Lücken und dem konkreten nächsten QA-Schritt."
            />
          </div>
          <p className="mt-3 rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] px-4 py-3 text-[13px] leading-6 text-[var(--text-secondary)]">
            Was es nicht tut: bewerten, freigeben oder QA-Verantwortung ersetzen. Die
            letzte Entscheidung trifft immer ein Mensch — fest eingebaut, nicht
            abschaltbar.
          </p>
        </section>
      </Reveal>

      {/* Wie es funktioniert */}
      <Reveal delay={0.25}>
        <section>
          <LandingHeading
            title="Wie es funktioniert — in drei Schritten."
            description="Vom Dokumentenstapel zur entscheidungsreifen Mappe, ohne dass die Verantwortung an die Maschine wandert."
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
              body="Sieben unabhängige Prüfinstanzen gehen die Unterlagen gegen Ihr Regelwerk durch — Datenintegrität, Abweichung, CAPA, Chargenbezug, Validierung, regulatorische Konsistenz, Widersprüche. Ob ein Zitat wirklich im Original steht, prüft fester Programmcode, keine KI — Zeichen für Zeichen."
            />
            <StepCard
              number="03"
              title="Vorlegen, nicht entscheiden"
              body="Das Ergebnis ist die Prüfmappe. Klare Fälle sind als klar markiert, kritische und unklare wandern immer auf Ihren Tisch. Das System schließt nichts im Stillen ab."
            />
          </div>
        </section>
      </Reveal>

      {/* Gemessen */}
      <Reveal delay={0.3}>
        <section>
          <LandingHeading
            title="Gemessen, nicht behauptet."
            description="In Anlehnung an Ringversuche aus der Laborpraxis wird das System regelmäßig mit präparierten Fällen getestet, deren versteckte Fehler vorab dokumentiert und versiegelt sind."
          />
          <div className="rounded-md border border-[var(--border-default)] bg-[var(--brand-soft)] p-5">
            <p className="mb-5 max-w-3xl text-[13px] leading-6 text-[var(--text-secondary)]">
              So ist belegbar, was es findet, was es übersieht — und dass es bei
              fehlerfreien Unterlagen ruhig bleibt.
            </p>
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
            <div className="mt-2 max-w-2xl text-[11px] leading-5 text-[var(--text-tertiary)]">
              Stand 11.06.2026, aus den Messdaten des letzten abgeschlossenen Laufs — nicht
              der beste ausgewählte. Der vollständige Lauf inklusive aller Fälle ist im
              Qualifizierungsnachweis einsehbar.
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

      {/* Fußnote */}
      <Reveal delay={0.4}>
        <section className="border-t border-[var(--border-default)] pt-5">
          <p className="max-w-3xl text-[12px] leading-6 text-[var(--text-tertiary)]">
            Dies ist ein Prototyp. Ein produktiver Einsatz erfordert formale Validierung,
            SOPs und die Freigabe im Qualitätssystem des Anwenders. Genau dafür ist die
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

function InfoBlock({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-primary)] p-4">
      <div className="text-[13px] font-medium text-[var(--text-primary)]">{title}</div>
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
