import { redirect } from "next/navigation";
import { AppShell } from "@/src/components/app-shell";
import { loadPublicRingversuchRuns } from "@/src/lib/ringversuch-server";

export default async function SectionPage({ params }: { params: Promise<{ section: string }> }) {
  const { section } = await params;
  if (section === "case-workspace") {
    redirect("/review-ui");
  }
  // Ringversuch and the pitch landing render from server data — no client fetch waterfall.
  const ringversuchRuns =
    section === "ringversuch" || section === "ueberblick"
      ? await loadPublicRingversuchRuns()
      : undefined;
  return <AppShell section={section} ringversuchRuns={ringversuchRuns} />;
}
