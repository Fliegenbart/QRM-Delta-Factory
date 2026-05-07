import { demoUsers } from "./demo-data";

export function authenticateDemoUser(email: string, password: string) {
  const user = demoUsers.find((candidate) => candidate.email === email);
  if (!user || password !== "demo123") return null;
  return user;
}
