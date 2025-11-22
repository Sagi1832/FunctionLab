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
import useLogin from "../useLogin.js";

const TestComponent = () => {
  const login = useLogin();
  const location = useLocation();

  useEffect(() => {
    if (!login.isLoading) {
      login.mutate({ username: "tester", password: "secret123" });
    }
  }, [login]);

  return <div data-testid="location">{location.pathname}</div>;
};

const renderWithProviders = (ui) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return render(
    <MemoryRouter initialEntries={["/login"]}>
      <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
    </MemoryRouter>
  );
};

describe("useLogin", () => {
  it("saves token, navigates to /ask, and shows notification on success", async () => {
    renderWithProviders(<TestComponent />);

    await waitFor(() => {
      expect(window.localStorage.getItem("fl_token")).toBe("test-token-123");
    });

    await waitFor(() => {
      expect(notifications.show).toHaveBeenCalledWith(
        expect.objectContaining({ title: "Welcome back" })
      );
    });

    const location = await screen.findByTestId("location");
    expect(location.textContent).toBe("/ask");
  });
});
