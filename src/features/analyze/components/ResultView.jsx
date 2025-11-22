import { useMemo, useState } from "react";
import {
  Alert,
  Badge,
  Button,
  Code,
  Group,
  Paper,
  ScrollArea,
  Stack,
  Text,
  Title,
} from "@mantine/core";

import CopyButton from "../../../components/common/CopyButton.jsx";
import { renderMarkdown } from "../../../lib/markdown.js";

const isObjectLike = (value) => value !== null && typeof value === "object";

const formatPrimitive = (value) => {
  if (typeof value === "string") {
    return `"${value}"`;
  }
  if (typeof value === "number" || typeof value === "bigint") {
    return String(value);
  }
  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }
  if (value === null) {
    return "null";
  }
  if (typeof value === "undefined") {
    return "undefined";
  }
  return JSON.stringify(value);
};

const TreeNode = ({ value, depth = 0 }) => {
  if (!isObjectLike(value)) {
    return <Text size="sm">{formatPrimitive(value)}</Text>;
  }

  const entries = Array.isArray(value)
    ? value.map((item, index) => [index, item])
    : Object.entries(value);

  return (
    <Stack gap={4} ml={depth === 0 ? 0 : 16}>
      {entries.map(([key, childValue]) => (
        <Stack key={`${depth}-${key}`} gap={4} ml={8}>
          <Group gap="xs" align="flex-start" wrap="nowrap">
            <Code>{String(key)}</Code>
            {isObjectLike(childValue) ? (
              <TreeNode value={childValue} depth={depth + 1} />
            ) : (
              <Text size="sm" c="dimmed">
                {formatPrimitive(childValue)}
              </Text>
            )}
          </Group>
        </Stack>
      ))}
    </Stack>
  );
};

const ResultView = ({ data }) => {
  const [isCollapsed, setIsCollapsed] = useState(true);

  const jsonString = useMemo(() => (data ? JSON.stringify(data, null, 2) : ""), [data]);

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
  const docMarkdown = !presentText && !narration && data.present?.doc_md ? data.present.doc_md : null;

  const hasNarrative = Boolean(
    presentText || data.present?.title || narration || docMarkdown
  );
  const hasWarnings = Array.isArray(data.warnings) && data.warnings.length > 0;
  const hasErrors = Array.isArray(data.errors) && data.errors.length > 0;

  const handleToggleCollapse = () => {
    setIsCollapsed((prev) => !prev);
  };

  return (
    <Stack gap="sm">
      <Group justify="flex-end" gap="xs">
        {hasWarnings ? <Badge color="yellow">Warnings {data.warnings.length}</Badge> : null}
        {hasErrors ? <Badge color="red">Errors {data.errors.length}</Badge> : null}
        <CopyButton value={jsonString} label="Copy JSON" />
        <Button size="xs" variant="light" type="button" onClick={handleToggleCollapse}>
          {isCollapsed ? "Expand" : "Collapse"}
        </Button>
      </Group>

      {hasNarrative ? (
        <Paper withBorder shadow="xs" p="md" radius="md">
          <Stack gap="sm">
            {data.present?.title ? <Title order={3}>{data.present.title}</Title> : null}
            {presentText ? (
              <Text style={{ whiteSpace: "pre-line" }}>{presentText}</Text>
            ) : null}
            {!presentText && narration ? (
              <Text style={{ whiteSpace: "pre-line" }}>{narration}</Text>
            ) : null}
            {!presentText && !narration && docMarkdown ? (
              <Text component="div" dangerouslySetInnerHTML={renderMarkdown(docMarkdown)} />
            ) : null}
          </Stack>
        </Paper>
      ) : null}

      <ScrollArea h={360} type="auto" offsetScrollbars>
        {isCollapsed ? (
          <Code block>{jsonString}</Code>
        ) : (
          <Stack gap="xs" pt="xs">
            <TreeNode value={data} />
          </Stack>
        )}
      </ScrollArea>

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
