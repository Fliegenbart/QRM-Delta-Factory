import { AppShell } from "@/src/components/app-shell";

export default async function ProjectDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <AppShell section="project-detail" projectId={id} />;
}
