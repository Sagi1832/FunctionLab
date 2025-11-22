import "@mantine/core/styles.css";
import "@mantine/notifications/styles.css";

import { MantineProvider, createTheme } from "@mantine/core";
import { Notifications } from "@mantine/notifications";
import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { BrowserRouter } from "react-router-dom";

import { queryClient } from "../lib/queryClient.js";

const theme = createTheme({
  defaultRadius: "md",
  fontFamily:
    "system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif",
});

const AppProviders = ({ children }) => (
  // Provider stack order: Router → Mantine → React Query → Notifications/devtools
  <BrowserRouter>
    <MantineProvider theme={theme} defaultColorScheme="light">
      <QueryClientProvider client={queryClient}>
        <Notifications position="top-right" />
        {children}
        {import.meta.env.DEV ? <ReactQueryDevtools initialIsOpen={false} /> : null}
      </QueryClientProvider>
    </MantineProvider>
  </BrowserRouter>
);

export default AppProviders;
