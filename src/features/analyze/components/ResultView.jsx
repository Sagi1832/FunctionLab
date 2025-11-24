import { useMemo } from "react";
import {
  Alert,
  Badge,
  Group,
  Paper,
  Stack,
  Text,
  Title,
} from "@mantine/core";

import CopyButton from "../../../components/common/CopyButton.jsx";
import { renderMarkdown } from "../../../lib/markdown.js";

const ResultView = ({ data }) => {
  const jsonString = useMemo(
    () => (data ? JSON.stringify(data, null, 2) : ""),
    [data]
  );

  if (!data) {
    return null;
  }

  // Handle present as string (new format) or object (legacy format)
  const presentText =
    typeof data.present === "string" && data.present.trim().length > 0
      ? data.present
      : null;

  const narration =
    !presentText &&
    typeof data.present?.narration === "string" &&
    data.present.narration.trim().length > 0
      ? data.present.narration
      : null;

  const docMarkdown =
    !presentText && !narration && data.present?.doc_md
      ? data.present.doc_md
      : null;

  const hasNarrative = Boolean(
    presentText || data.present?.title || narration || docMarkdown
  );
  const hasWarnings = Array.isArray(data.warnings) && data.warnings.length > 0;
  const hasErrors = Array.isArray(data.errors) && data.errors.length > 0;

  return (
    <Stack gap="sm">
      {/* Upper title – in badges and Copy JSON button */}
      <Group justify="flex-end" gap="xs">
        {hasWarnings ? (
          <Badge color="yellow">Warnings {data.warnings.length}</Badge>
        ) : null}
        {hasErrors ? (
          <Badge color="red">Errors {data.errors.length}</Badge>
        ) : null}
        <CopyButton value={jsonString} label="Copy JSON" />
      </Group>

      {/* Beautiful presentation */}
      {hasNarrative ? (
        <Paper withBorder shadow="xs" p="md" radius="md">
          <Stack gap="sm">
            {data.present?.title ? (
              <Title order={3}>{data.present.title}</Title>
            ) : null}

            {presentText ? (
              <Text style={{ whiteSpace: "pre-line" }}>{presentText}</Text>
            ) : null}

            {!presentText && narration ? (
              <Text style={{ whiteSpace: "pre-line" }}>{narration}</Text>
            ) : null}

            {!presentText && !narration && docMarkdown ? (
              <Text
                component="div"
                dangerouslySetInnerHTML={renderMarkdown(docMarkdown)}
              />
            ) : null}
          </Stack>
        </Paper>
      ) : null}

      {/* Warnings */}
      {hasWarnings ? (
        <Alert color="yellow" title="Warnings">
          <ul style={{ paddingLeft: "1.2rem", margin: 0 }}>
            {data.warnings.map((warning, index) => (
              <li key={`warning-${index}`}>
                <Text size="sm">{warning}</Text>
              </li>
            ))}
          </ul>
        </Alert>
      ) : null}

      {/* Errors */}
      {hasErrors ? (
        <Alert color="red" title="Errors">
          <ul style={{ paddingLeft: "1.2rem", margin: 0 }}>
            {data.errors.map((err, index) => (
              <li key={`error-${index}`}>
                <Text size="sm">{err}</Text>
              </li>
            ))}
          </ul>
        </Alert>
      ) : null}
    </Stack>
  );
};

export default ResultView;
