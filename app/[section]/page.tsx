import { AppShell } from "@/src/components/app-shell";

export default async function SectionPage({ params }: { params: Promise<{ section: string }> }) {
  const { section } = await params;
  return <AppShell section={section} />;
}
