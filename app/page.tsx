import { redirect } from "next/navigation";

// The signed-in tool has one door: the cases page, with the upload on top.
// The public pitch lives at /ueberblick.
export default function HomePage() {
  redirect("/review-ui");
}
