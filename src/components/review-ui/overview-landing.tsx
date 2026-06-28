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

function Reveal({ delay = 0, children }: { delay?: number; children: React.ReactNode }) {
  return (
    <motion.div
      variants={reveal}
      initial="initial"
      animate="animate"
      transition={{ duration: 0.5, delay, ease: [0.21, 0.65, 0.36, 1] }}
    >
      {children}
    </motion.div>
  );
}

/* ----- Hauptkomponente ----- */

export function OverviewLanding() {
  return (
    <div className="qrm-landing min-h-screen">
      <TopBar />

      <main id="main-content">
        {/* Hero */}
        <section className="border-b border-[var(--border-muted)]">
          <div className="mx-auto grid max-w-6xl items-center gap-12 px-5 py-16 sm:px-8 sm:py-24 lg:grid-cols-[minmax(0,1fr)_minmax(0,420px)]">
            <div>
              <Eyebrow>Pharma QRM · Delta Engine</Eyebrow>
              <h1 className="mt-5 font-[family-name:var(--font-serif)] text-[40px] font-medium leading-[1.06] tracking-[-0.015em] text-[var(--text-primary)] sm:text-[58px]">
                Ihre GMP-Fälle, vorgeprüft und belegt.
              </h1>
              <p className="mt-6 max-w-xl text-[17px] leading-8 text-[var(--text-secondary)]">
                Laden Sie Change Control, Abweichungen, CAPA oder Audit-Findings hoch.
                Zurück kommt eine geordnete Prüfmappe: belegte Befunde, markierte
                Widersprüche, fehlende Pflichtangaben. Sie sparen die Stunden Vorarbeit
                und behalten die Bewertung.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <PrimaryCta href="#trust-steps">Blindtest starten</PrimaryCta>
                <SecondaryCta href="#how-it-works">Wie es funktioniert</SecondaryCta>
              </div>
            </div>
            <FindingArtifact />
          </div>
        </section>

        {/* Beweis-Zone */}
        <section id="proof" className="border-b border-[var(--border-muted)] bg-[var(--surface-secondary)]">
          <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-20">
            <Eyebrow accent>Im Ringversuch gemessen.</Eyebrow>
            <h2 className="mt-4 max-w-2xl text-[26px] font-semibold tracking-[-0.01em] text-[var(--text-primary)] sm:text-[30px]">
              Geprüft an präparierten Fällen, deren Fehler vorab dokumentiert und
              versiegelt waren.
            </h2>
            <p className="mt-4 max-w-2xl text-[15px] leading-7 text-[var(--text-secondary)]">
              Das System sah die Fälle zum ersten Mal im Lauf. Erst danach wurde der
              Umschlag geöffnet. So lässt sich nachvollziehen, was es fand, was es übersah
              und wie es auf fehlerfreie Unterlagen reagierte.
            </p>
            <div className="mt-10 grid gap-px overflow-hidden rounded-2xl border border-[var(--border-default)] bg-[var(--border-default)] sm:grid-cols-3">
              <BigStat value="24 / 25" label="versteckte Fehler gefunden" />
              <BigStat value="0" label="Fehlalarme bei 11 harmlosen Kontrollstellen" />
              <BigStat value="93 %" label="der Befunde mit wörtlich geprüftem Zitat" accent />
            </div>
            <div className="mt-6 flex flex-wrap items-center justify-between gap-3">
              <Link
                href="/ringversuch"
                className="inline-flex items-center gap-1.5 text-[14px] font-medium text-[var(--brand-strong)] hover:underline"
              >
                Zum vollständigen Nachweis
                <ArrowRight className="h-4 w-4" aria-hidden />
              </Link>
              <p className="max-w-md text-[12px] leading-5 text-[var(--text-tertiary)]">
                Stand 11.06.2026, jüngster abgeschlossener Lauf — nicht der beste
                ausgewählte. Vollständig einsehbar im Qualifizierungsnachweis.
              </p>
            </div>
          </div>
        </section>

        {/* Was Sie damit machen */}
        <Band>
          <SectionHead
            title="Was Sie damit machen."
            description="Sie geben einen Stapel GMP-Unterlagen hinein: Change Control, Abweichung, CAPA, Audit-Findings. Sie bekommen eine geordnete, belegte Prüfmappe zurück, für die Sie sonst Stunden Handarbeit bräuchten."
          />
          <div className="grid gap-6 text-[15px] leading-8 text-[var(--text-secondary)] lg:grid-cols-3">
            <p>
              In der Mappe steht zu jeder Aussage die Fundstelle. Widersprüche sind
              markiert, fehlende Pflichtnachweise benannt.
            </p>
            <p>
              Die Risikobewertung treffen weiter Sie. Das Tool bereitet sie vor: Befunde,
              Belege, Lücken und gewichtete Risiken, soweit die Unterlagen das hergeben.
            </p>
            <p>
              Kein Chatbot und keine Freigabe-Automatik. Ein Werkzeug, das den Fall
              sortiert und Ihnen vorlegt.
            </p>
          </div>
        </Band>

        {/* Warum Sie dem Ergebnis vertrauen können */}
        <Band tint>
          <SectionHead
            title="Warum Sie dem Ergebnis vertrauen können."
            description="Der Engpass war nie die Geschwindigkeit, sondern die Frage, ob man dem Ergebnis trauen kann."
          />
          <div className="mb-8 max-w-2xl space-y-4 text-[15px] leading-8 text-[var(--text-secondary)]">
            <p>
              Was solche Systeme ausgaben, mussten Sie von Hand nachprüfen. Sobald Sie
              alles nachprüfen, ist die Ersparnis weg. Eine falsche, aber selbstsicher
              formulierte Aussage ist dabei schlimmer als gar keine.
            </p>
            <p>
              Dieses Tool ist um genau dieses Problem herum gebaut. Drei Prinzipien, keines
              davon abschaltbar.
            </p>
          </div>
          <div className="grid gap-4 lg:grid-cols-3">
            <PrincipleCard
              icon={Quote}
              title="Sie prüfen keine erfundenen Zitate mehr."
              body="Jedes Zitat wird per Code Zeichen für Zeichen gegen das Original geprüft, bevor es in die Mappe kommt. Was sich nicht wörtlich belegen lässt, erscheint gar nicht erst. Sie bewerten nur, was nachweislich im Dokument steht."
            />
            <PrincipleCard
              icon={FlaskConical}
              title="Keine Fehlalarme zum Wegklicken."
              body="Befunde, die keine sind, kosten am meisten Zeit. Im Ringversuch waren es bei elf sauberen Kontrollstellen null. Wo nichts ist, meldet das System nichts."
            />
            <PrincipleCard
              icon={UserCheck}
              title="Bei dünner Beleglage rät es nicht."
              body="Reichen die Unterlagen nicht, hält das System an und gibt den Fall zurück an Sie, statt eine Antwort zu erfinden. So sehen Sie sofort, wo Sie selbst hinschauen müssen."
            />
          </div>
          <p className="mt-6 max-w-3xl border-l-2 border-[var(--brand)] pl-5 text-[15px] leading-8 text-[var(--text-secondary)]">
            Ihr Aufwand verschiebt sich: weniger Zeit fürs Kontrollieren der Maschine, mehr
            fürs Entscheiden des Falls. Die Sorgfalt bleibt gleich, sie landet nur an der
            richtigen Stelle.
          </p>
        </Band>

        {/* Was rein- und was rauskommt */}
        <Band>
          <SectionHead
            title="Was rein- und was rauskommt."
            description="Change Control, Abweichungen, CAPA, Audit-Findings und Periodic Reviews, mehrere Dokumente pro Fall. Die Originaldateien bleiben die Quelle: nichts wird umgeschrieben, alles bleibt rückverfolgbar."
          />
          <div className="grid gap-4 lg:grid-cols-3">
            <InfoBlock
              title="Was reingeht"
              body="Change Control, Abweichungen, CAPA, Audit-Findings und Periodic Reviews. Mehrere Dokumente pro Fall."
            />
            <InfoBlock title="Was es findet">
              <ul className="space-y-2">
                <li>Eine Abweichung als „Minor“ eingestuft — ohne die Labordaten, die das tragen würden.</li>
                <li>Eine CAPA mit dokumentierten Maßnahmen, aber offener Wirksamkeitsprüfung.</li>
                <li>Ein Annex-Zitat, das auf Seite 14 anders steht, als der Bericht behauptet.</li>
                <li>Zwei Dokumente, die sich widersprechen, ohne dass es jemandem aufgefallen ist.</li>
              </ul>
            </InfoBlock>
            <InfoBlock
              title="Was rauskommt"
              body="Eine Prüfmappe pro Fall: Befund, belegendes Zitat, offene Lücke, nächster QA-Schritt. Bei sauberen Unterlagen bleibt sie leer. Keine erfundene Arbeit."
            />
          </div>
          <p className="mt-5 max-w-3xl text-[14px] leading-7 text-[var(--text-tertiary)]">
            Was es nicht tut: bewerten, freigeben oder Verantwortung übernehmen. Die letzte
            Entscheidung trifft immer ein Mensch, fest verdrahtet.
          </p>
        </Band>

        {/* Wie es funktioniert */}
        <Band tint id="how-it-works">
          <SectionHead
            title="In drei Schritten zur Prüfmappe."
            description="Vom Dokumentenstapel zur Prüfmappe, ohne dass die Verantwortung an die Maschine wandert."
          />
          <div className="grid gap-4 sm:grid-cols-3">
            <StepCard
              number="01"
              title="Lesen und belegen"
              body="Jedes Dokument wird in einzelne, zitierfähige Aussagen zerlegt. Jede behält ihre Fundstelle: Dokument, Seite, wörtliches Zitat. Von jeder Aussage sind Sie einen Klick von der Quelle entfernt."
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
        </Band>

        {/* Vertrauensstufen */}
        <Band id="trust-steps">
          <SectionHead
            title="Vertrauen in Stufen, jede mit einem prüfbaren Kriterium."
            description="Der nächste Schritt ist kein Sprung in den Produktivbetrieb, sondern ein Blindtest mit Ihren Fällen."
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
        </Band>
      </main>

      <Footer />
    </div>
  );
}

/* ----- Seitengerüst ----- */

function TopBar() {
  return (
    <header className="sticky top-0 z-20 border-b border-[var(--border-default)] bg-[var(--background)]">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-5 py-3.5 sm:px-8">
        <div className="flex items-center gap-2.5">
          <div
            className="grid h-7 w-7 place-items-center rounded-md bg-[var(--brand)] text-[12px] font-semibold text-white"
            aria-hidden
          >
            Q
          </div>
          <span className="text-[14px] font-semibold tracking-[0.01em] text-[var(--text-primary)]">
            Pharma QRM
          </span>
        </div>
        <nav className="hidden items-center gap-7 text-[13px] text-[var(--text-secondary)] md:flex">
          <a href="#proof" className="hover:text-[var(--text-primary)]">Beweis</a>
          <a href="#how-it-works" className="hover:text-[var(--text-primary)]">Funktionsweise</a>
          <a href="#trust-steps" className="hover:text-[var(--text-primary)]">Vertrauensstufen</a>
        </nav>
        <div className="flex items-center gap-2">
          <Link
            href="/"
            className="hidden text-[13px] font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] sm:inline"
          >
            Zum Tool
          </Link>
          <PrimaryCta href="#trust-steps" compact>Blindtest starten</PrimaryCta>
        </div>
      </div>
    </header>
  );
}

function Footer() {
  return (
    <footer className="border-t border-[var(--border-default)] bg-[var(--surface-secondary)]">
      <div className="mx-auto max-w-6xl px-5 py-12 sm:px-8">
        <div className="flex flex-col gap-8 md:flex-row md:items-end md:justify-between">
          <div className="max-w-xl">
            <h2 className="font-[family-name:var(--font-serif)] text-[24px] font-medium tracking-[-0.01em] text-[var(--text-primary)] sm:text-[28px]">
              Der nächste Schritt ist ein Blindtest mit Ihren Fällen.
            </h2>
            <p className="mt-3 text-[14px] leading-7 text-[var(--text-secondary)]">
              Ein bis zwei Expertentage. Sie bauen die Fälle, behalten die Lösung, bewerten
              gegen Ihre eigenen Kriterien.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <PrimaryCta href="#trust-steps">Blindtest starten</PrimaryCta>
            <SecondaryCta href="/">Zum Tool</SecondaryCta>
          </div>
        </div>
        <p className="mt-10 max-w-3xl border-t border-[var(--border-default)] pt-6 text-[12px] leading-6 text-[var(--text-tertiary)]">
          Dies ist ein Prototyp. Produktiver Einsatz erfordert formale Validierung, SOPs
          und Freigabe im Qualitätssystem des Anwenders. Genau dafür ist die
          Vertrauensleiter da.
        </p>
      </div>
    </footer>
  );
}

function Band({
  children,
  tint,
  id,
}: {
  children: React.ReactNode;
  tint?: boolean;
  id?: string;
}) {
  return (
    <section
      id={id}
      className={`border-b border-[var(--border-muted)] ${tint ? "bg-[var(--surface-secondary)]" : ""}`}
    >
      <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-20">
        <Reveal>{children}</Reveal>
      </div>
    </section>
  );
}

/* ----- Bausteine ----- */

function Eyebrow({ children, accent }: { children: React.ReactNode; accent?: boolean }) {
  return (
    <div
      className={`text-[12px] font-semibold uppercase tracking-[0.18em] ${
        accent ? "text-[var(--brand-strong)]" : "text-[var(--text-tertiary)]"
      }`}
    >
      {children}
    </div>
  );
}

function SectionHead({ title, description }: { title: string; description: string }) {
  return (
    <div className="mb-10 max-w-3xl">
      <h2 className="text-[26px] font-semibold leading-[1.15] tracking-[-0.01em] text-[var(--text-primary)] sm:text-[32px]">
        {title}
      </h2>
      <p className="mt-4 text-[16px] leading-8 text-[var(--text-secondary)]">{description}</p>
    </div>
  );
}

function PrimaryCta({
  href,
  children,
  compact,
}: {
  href: string;
  children: React.ReactNode;
  compact?: boolean;
}) {
  return (
    <a
      href={href}
      className={`inline-flex items-center gap-2 rounded-lg bg-[var(--brand)] font-medium text-white shadow-sm transition-colors hover:bg-[var(--brand-strong)] ${
        compact ? "h-9 px-3.5 text-[13px]" : "h-11 px-5 text-[14px]"
      }`}
    >
      {children}
      <ArrowRight className={compact ? "h-3.5 w-3.5" : "h-4 w-4"} aria-hidden />
    </a>
  );
}

function SecondaryCta({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <a
      href={href}
      className="inline-flex h-11 items-center rounded-lg border border-[var(--border-strong)] bg-[var(--surface-primary)] px-5 text-[14px] font-medium text-[var(--text-primary)] transition-colors hover:bg-[var(--surface-secondary)]"
    >
      {children}
    </a>
  );
}

function BigStat({ value, label, accent }: { value: string; label: string; accent?: boolean }) {
  return (
    <div className="bg-[var(--surface-primary)] p-7">
      <div
        className={`text-[40px] font-semibold leading-none tracking-[-0.02em] sm:text-[46px] ${
          accent ? "text-[var(--brand-strong)]" : "text-[var(--text-primary)]"
        }`}
      >
        {value}
      </div>
      <div className="mt-3 text-[13px] leading-6 text-[var(--text-secondary)]">{label}</div>
    </div>
  );
}

function FindingArtifact() {
  return (
    <div aria-hidden className="select-none">
      <div className="rounded-2xl border border-[var(--border-default)] bg-[var(--surface-primary)] p-5 shadow-[0_8px_30px_rgba(15,23,42,0.06)]">
        <div className="flex items-center justify-between gap-2">
          <span className="rounded border border-amber-200 bg-amber-50 px-2 py-0.5 text-[11px] font-medium uppercase tracking-[0.06em] text-amber-700">
            Befund · Hoch
          </span>
          <span className="text-[11px] uppercase tracking-[0.12em] text-[var(--text-tertiary)]">
            Prüfmappe
          </span>
        </div>
        <p className="mt-4 text-[15px] font-medium leading-6 text-[var(--text-primary)]">
          Abweichung als „Minor" eingestuft — ohne Labordaten zur Temperaturunterschreitung.
        </p>
        <div className="mt-4 rounded-r-lg border-l-2 border-[var(--brand-strong)] bg-[var(--surface-secondary)] px-4 py-3">
          <p className="mono text-[12.5px] leading-6 text-[var(--text-secondary)]">
            „Die Abweichung wird als Minor eingestuft, da die Salbe visuell homogen
            blieb …"
          </p>
        </div>
        <div className="mt-3.5 flex items-center justify-between gap-2 text-[12px]">
          <span className="inline-flex items-center gap-1.5 font-medium text-[var(--brand-strong)]">
            <CheckCircle2 className="h-3.5 w-3.5" aria-hidden />
            Zitat wortwörtlich geprüft
          </span>
          <span className="text-[var(--text-tertiary)]">Deviation Report · S. 1</span>
        </div>
        <div className="mt-4 border-t border-[var(--border-default)] pt-3 text-[12px] leading-6 text-[var(--text-tertiary)]">
          Nächster Schritt: QA-Entscheidung — Hochstufung prüfen, Labordaten nachfordern
        </div>
      </div>
    </div>
  );
}

function StepCard({ number, title, body }: { number: string; title: string; body: string }) {
  return (
    <div className="rounded-2xl border border-[var(--border-default)] bg-[var(--surface-primary)] p-6">
      <div className="mono text-[24px] font-semibold text-[var(--brand-strong)]">{number}</div>
      <div className="mt-3 text-[16px] font-semibold text-[var(--text-primary)]">{title}</div>
      <p className="mt-2 text-[13.5px] leading-7 text-[var(--text-secondary)]">{body}</p>
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
    <div className="rounded-2xl border border-[var(--border-default)] bg-[var(--surface-primary)] p-6">
      <div className="text-[14px] font-semibold text-[var(--text-primary)]">{title}</div>
      <div className="mt-3 text-[13.5px] leading-7 text-[var(--text-secondary)]">
        {children ?? body}
      </div>
    </div>
  );
}

function PrincipleCard({
  icon: Icon,
  title,
  body,
}: {
  icon: LucideIcon;
  title: string;
  body: string;
}) {
  return (
    <div className="rounded-2xl border border-[var(--border-default)] bg-[var(--surface-primary)] p-6">
      <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--brand-soft)]">
        <Icon className="h-5 w-5 text-[var(--brand-strong)]" aria-hidden />
      </div>
      <div className="mt-4 text-[16px] font-semibold leading-snug text-[var(--text-primary)]">
        {title}
      </div>
      <p className="mt-2 text-[13.5px] leading-7 text-[var(--text-secondary)]">{body}</p>
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
        ? "bg-amber-50 text-amber-700 border-amber-200"
        : "bg-[var(--surface-secondary)] text-[var(--text-tertiary)] border-[var(--border-default)]";
  return (
    <li className="relative flex gap-5 pb-8 last:pb-0">
      {!last ? (
        <span
          className="absolute left-[17px] top-10 bottom-0 w-px bg-[var(--border-default)]"
          aria-hidden
        />
      ) : null}
      <div
        className={`relative z-10 flex h-9 w-9 shrink-0 items-center justify-center rounded-full border text-[14px] font-semibold ${
          state === "done"
            ? "border-[var(--brand-strong)] bg-[var(--brand-soft)] text-[var(--brand-strong)]"
            : "border-[var(--border-strong)] bg-[var(--surface-primary)] text-[var(--text-secondary)]"
        }`}
      >
        {state === "done" ? <CheckCircle2 className="h-4 w-4" aria-hidden /> : index}
      </div>
      <div className="pt-1">
        <div className="flex flex-wrap items-center gap-2.5">
          <span className="text-[16px] font-semibold text-[var(--text-primary)]">{title}</span>
          <span
            className={`rounded border px-2 py-0.5 text-[11px] font-medium uppercase tracking-[0.06em] ${badgeClasses}`}
          >
            {status}
          </span>
        </div>
        {invitation ? (
          <div className="mt-1 text-[14px] font-medium italic text-[var(--brand-strong)]">
            {invitation}
          </div>
        ) : null}
        <p className="mt-1.5 max-w-2xl text-[13.5px] leading-7 text-[var(--text-secondary)]">
          {body}
        </p>
      </div>
    </li>
  );
}
