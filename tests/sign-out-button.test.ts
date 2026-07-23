/** @vitest-environment jsdom */

import { createElement } from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { SignOutButton } from "@/src/components/auth/sign-out-button";

const replace = vi.fn();
const refresh = vi.fn();
const signOut = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace, refresh }),
}));

vi.mock("@/utils/supabase/client", () => ({
  createClient: () => ({ auth: { signOut } }),
}));

describe("sign out button", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    signOut.mockResolvedValue({ error: null });
  });

  it("clears the local Supabase session and returns to login", async () => {
    render(createElement(SignOutButton));

    fireEvent.click(screen.getByRole("button", { name: "Abmelden" }));

    await waitFor(() => {
      expect(signOut).toHaveBeenCalledWith({ scope: "local" });
      expect(replace).toHaveBeenCalledWith("/login");
      expect(refresh).toHaveBeenCalledTimes(1);
    });
  });
});
