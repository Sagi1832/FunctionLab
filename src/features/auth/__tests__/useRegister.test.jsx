import { vi } from "vitest";

vi.mock("@mantine/notifications", () => ({
  notifications: {
    show: vi.fn(),
  },
}));

import { useEffect } from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, useLocation } from "react-router-dom";

import { notifications } from "@mantine/notifications";
import useRegister from "../useRegister.js";

const TestComponent = () => {
  const register = useRegister();
  const location = useLocation();

  useEffect(() => {
    if (!register.isLoading) {
      register.mutate({ username: "tester", password: "secret123" });
    }
  }, [register]);

  return <div data-testid="location">{location.pathname}</div>;
};

const renderWithProviders = (ui) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return render(
    <MemoryRouter initialEntries={["/register"]}>
      <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
    </MemoryRouter>
  );
};

describe("useRegister", () => {
  it("navigates to /ask and shows notification when token present", async () => {
    renderWithProviders(<TestComponent />);

    await waitFor(() => {
      expect(window.localStorage.getItem("fl_token")).toBe("test-token-123");
    });

    await waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith(
        expect.objectContaining({ title: "Account ready" })
      );
    });

    const location = await screen.findByTestId("location");
    expect(location.textContent).toBe("/ask");
  });
});
