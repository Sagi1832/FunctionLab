import { Alert, Container, Paper, Stack, Text } from "@mantine/core";
import { useMemo } from "react";

import HeaderBar from "../components/common/HeaderBar.jsx";
import AnalyzeForm from "../features/analyze/components/AnalyzeForm.jsx";
import ResultView from "../features/analyze/components/ResultView.jsx";
import useAnalyze from "../features/analyze/useAnalyze.js";

const AskPage = () => {
  const analyze = useAnalyze();

  const handleSubmit = (values) => {
    const payload = {
      raw: values.raw,
      var: values.var,
      action: values.action,
      present: values.present,
    };

    if (values.action === "extrema_and_monotonic") {
      payload.interval = values.interval;
      payload.closed = values.closed;
    }

    if (values.action === "x_intercepts") {
      payload.interval = values.interval;
      payload.closed = values.closed;
    }

    if (values.action === "y_intercepts") {
      if (values.interval && values.closed) {
        payload.interval = values.interval;
        payload.closed = values.closed;
      }
    }

    if (values.action === "asymptotes_and_holes") {
      payload.interval = values.interval;
      payload.closed = values.closed;
    }

    analyze.mutate(payload);
  };

  const errorMessage = useMemo(() => analyze.error?.message ?? null, [analyze.error]);

  return (
    <>
      <HeaderBar />
      <main role="main">
        <Container py="xl">
          <Paper withBorder shadow="xs" p="xl" radius="md">
            <Stack gap="xl">
              <Stack gap="xs">
                <Text fw={600} size="lg">
                  Analyze
                </Text>
                <Text c="dimmed" size="sm">
                  Submit a function, choose an action, and optionally request a narrative summary.
                </Text>
              </Stack>

              <AnalyzeForm onSubmit={handleSubmit} isSubmitting={analyze.isLoading} />

              {analyze.isPending ? <Text>Working…</Text> : null}

              {errorMessage ? <Alert color="red">{errorMessage}</Alert> : null}

              <ResultView data={analyze.data} />
            </Stack>
          </Paper>
        </Container>
      </main>
    </>
  );
};

export default AskPage;
