import { redirect } from "next/navigation";
import { AppShell } from "@/src/components/app-shell";

export default async function SectionPage({ params }: { params: Promise<{ section: string }> }) {
  const { section } = await params;
  if (section === "case-workspace") {
    redirect("/review-ui");
  }
  return <AppShell section={section} />;
}
