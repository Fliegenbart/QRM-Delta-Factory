/** @vitest-environment jsdom */

import { createElement } from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { DemoDecisionDesk } from "@/src/components/review-ui/demo-decision-desk";
import { demoReviewCases, demoDecisionStorageKey } from "@/src/lib/review-ui";

describe("demo decision desk", () => {
  const demoCase = demoReviewCases[0];
  let values: Map<string, string>;

  beforeEach(() => {
    values = new Map();
    Object.defineProperty(window, "localStorage", {
      configurable: true,
      value: {
        getItem: (key: string) => values.get(key) ?? null,
        setItem: (key: string, value: string) => values.set(key, value),
        removeItem: (key: string) => values.delete(key),
        clear: () => values.clear(),
        key: (index: number) => [...values.keys()][index] ?? null,
        get length() {
          return values.size;
        }
      } as Storage
    });
  });

  it("stores an explicitly saved demo decision and restores it after remount", async () => {
    const { unmount } = render(createElement(DemoDecisionDesk, { demoCase }));
    const selectedAction = "An QA eskalieren";

    fireEvent.click(screen.getByRole("button", { name: selectedAction }));
    expect(screen.getByRole("button", { name: selectedAction }).getAttribute("aria-pressed")).toBe("true");
    expect(window.localStorage.getItem(demoDecisionStorageKey(demoCase.id))).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Demo-Entscheidung speichern" }));
    expect(window.localStorage.getItem(demoDecisionStorageKey(demoCase.id))).toBe(selectedAction);
    expect(screen.getByRole("status").textContent).toContain(`Demo-Auswahl gespeichert: ${selectedAction}`);
    expect(screen.getByText(/Nur Demo: Die Auswahl wird in diesem Browser gespeichert/)).toBeTruthy();

    unmount();
    render(createElement(DemoDecisionDesk, { demoCase }));

    await waitFor(() => {
      expect(screen.getByRole("button", { name: selectedAction }).getAttribute("aria-pressed")).toBe("true");
    });
    expect(screen.getByRole("status").textContent).toContain(`Demo-Auswahl gespeichert: ${selectedAction}`);
  });
});
