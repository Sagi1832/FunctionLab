import { vi } from "vitest";

vi.mock("@mantine/notifications", () => ({
  notifications: {
    show: vi.fn(),
  },
}));

import { useEffect } from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import useAnalyze from "../useAnalyze.js";

const TestComponent = () => {
  const analyze = useAnalyze();

  useEffect(() => {
    analyze.mutate({ raw: "x^2", var: "x", action: "domain", present: true });
  }, [analyze]);

  if (!analyze.data) {
    return <div data-testid="status">pending</div>;
  }

  return (
    <div>
      <div data-testid="status">done</div>
      <div data-testid="action">{analyze.data.action}</div>
      <div data-testid="expr">{analyze.data.expr}</div>
      <div data-testid="var">{analyze.data.var}</div>
      <div data-testid="report">{analyze.data.report}</div>
      <div data-testid="present-title">{analyze.data.present.title}</div>
    </div>
  );
};

const renderWithProviders = (ui) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
};

describe("useAnalyze", () => {
  it("normalizes API response", async () => {
    renderWithProviders(<TestComponent />);

    await waitFor(() => {
      expect(screen.getByTestId("status").textContent).toBe("done");
    });

    expect(screen.getByTestId("action").textContent).toBe("domain");
    expect(screen.getByTestId("expr").textContent).toBe("x^2");
    expect(screen.getByTestId("var").textContent).toBe("x");
    expect(screen.getByTestId("report").textContent).toBe("Sample report");
    expect(screen.getByTestId("present-title").textContent).toBe("Domain Analysis");
  });
});
