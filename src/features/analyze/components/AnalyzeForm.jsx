import { useEffect, useMemo } from "react";
import {
  Button,
  Checkbox,
  Group,
  Select,
  Stack,
  Text,
  TextInput,
  Tooltip,
} from "@mantine/core";
import { useForm } from "@mantine/form";
import { notifications } from "@mantine/notifications";

const ACTION_OPTIONS = [
  { value: "domain", label: "domain" },
  { value: "derivative", label: "derivative" },
  { value: "x_intercepts", label: "X-intercepts" },
  { value: "y_intercepts", label: "Y-intercept" },
  { value: "asymptotes_and_holes", label: "asymptotes" },
  { value: "extrema_and_monotonic", label: "extrema & monotonic" },
];

const INTERVAL_REQUIRED_ACTIONS = new Set([
  "asymptotes_and_holes",
  "extrema_and_monotonic",
  "x_intercepts",
]);
const INTERVAL_OPTIONAL_ACTIONS = new Set(["y_intercepts"]);
const INTERVAL_ACTIONS = new Set([...INTERVAL_REQUIRED_ACTIONS, ...INTERVAL_OPTIONAL_ACTIONS]);

const INFINITY_TOKENS = new Map(
  ["inf", "+inf", "infinity", "+infinity"].map((token) => [token, Number.POSITIVE_INFINITY])
);
INFINITY_TOKENS.set("-inf", Number.NEGATIVE_INFINITY);
INFINITY_TOKENS.set("-infinity", Number.NEGATIVE_INFINITY);

const parseBound = (token) => {
  const trimmed = token.trim();
  const key = trimmed.toLowerCase();
  if (INFINITY_TOKENS.has(key)) {
    return INFINITY_TOKENS.get(key);
  }
  const parsed = Number(trimmed);
  if (Number.isNaN(parsed)) {
    throw new Error("Bounds must be numbers or +/-inf");
  }
  return parsed;
};

const parseIntervalInput = (input) => {
  const trimmed = input.trim();
  const match = trimmed.match(/^\s*(\(|\[)\s*([^,]+)\s*,\s*([^)\]]+)\s*(\)|\])\s*$/);
  if (!match) {
    throw new Error("Invalid interval. Use formats like [-2, 5] or (-inf, 3].");
  }

  const [, leftBracket, rawLeft, rawRight, rightBracket] = match;
  const leftClosed = leftBracket === "[";
  const rightClosed = rightBracket === "]";

  const leftValue = parseBound(rawLeft);
  const rightValue = parseBound(rawRight);

  if (leftValue > rightValue) {
    throw new Error("Lower bound must be less than or equal to upper bound.");
  }

  if (leftValue === rightValue && !leftClosed && !rightClosed) {
    throw new Error("Open interval endpoints cannot be equal.");
  }

  return {
    interval: [leftValue, rightValue],
    closed: [leftClosed, rightClosed],
  };
};

const AnalyzeForm = ({ onSubmit, isSubmitting }) => {
  const form = useForm({
    initialValues: {
      raw: "",
      var: "x",
      action: ACTION_OPTIONS[0].value,
      interval: "",
      present: true,
    },
    validate: {
      raw: (value) => (value.trim().length > 0 ? null : "Function is required"),
      var: (value) =>
        /^[a-zA-Z]+$/.test(value.trim()) ? null : "Variable must be a single latin word",
      action: (value) =>
        ACTION_OPTIONS.some((option) => option.value === value) ? null : "Select a valid action",
      interval: (value, values) => {
        if (!INTERVAL_ACTIONS.has(values.action)) {
          return null;
        }
        if (INTERVAL_REQUIRED_ACTIONS.has(values.action)) {
          return value.trim().length > 0 ? null : "Interval is required";
        }
        if (value.trim().length === 0) {
          return null;
        }
        try {
          parseIntervalInput(value);
          return null;
        } catch (error) {
          return error instanceof Error ? error.message : "Invalid interval";
        }
      },
    },
    validateInputOnBlur: true,
  });

  const showInterval = INTERVAL_ACTIONS.has(form.values.action);
  const intervalOptional = INTERVAL_OPTIONAL_ACTIONS.has(form.values.action);

  useEffect(() => {
    if (!showInterval) {
      form.setFieldValue("interval", "");
      form.clearFieldError("interval");
    }
  }, [showInterval, form]);

  const handleSubmit = form.onSubmit((values) => {
    const payload = {
      raw: values.raw.trim(),
      var: values.var.trim(),
      action: values.action,
      present: values.present,
    };

    if (INTERVAL_ACTIONS.has(values.action)) {
      try {
        if (values.interval.trim().length === 0) {
          if (INTERVAL_REQUIRED_ACTIONS.has(values.action)) {
            throw new Error("Interval is required");
          }
        } else {
          const parsed = parseIntervalInput(values.interval);
          payload.interval = parsed.interval;
          payload.closed = parsed.closed;
        }
        form.clearFieldError("interval");
      } catch (error) {
        const message = error instanceof Error ? error.message : "Invalid interval";
        form.setFieldError("interval", message);
        notifications.show({
          title: "Interval error",
          message,
          color: "red",
        });
        return;
      }
    }

    onSubmit(payload);
  });

  const actionData = useMemo(() => ACTION_OPTIONS, []);
  const intervalInvalid =
    showInterval &&
    ((INTERVAL_REQUIRED_ACTIONS.has(form.values.action) && !form.values.interval.trim()) ||
      Boolean(form.errors.interval));

  const isSubmitDisabled = isSubmitting || intervalInvalid;

  return (
    <form onSubmit={handleSubmit}>
      <Stack>
        <TextInput
          label="Function"
          placeholder="e.g. (x^2 - 1)/(x - 1)"
          {...form.getInputProps("raw")}
          required
          disabled={isSubmitting}
        />

        <Group align="flex-end" gap="md" wrap="wrap">
          <TextInput
            label="Variable"
            w={120}
            {...form.getInputProps("var")}
            required
            disabled={isSubmitting}
          />
          <Select
            label="Action"
            data={actionData}
            {...form.getInputProps("action")}
            disabled={isSubmitting}
            data-testid="analyze-action"
          />
          {showInterval ? (
            <Tooltip label="Round brackets = open, square brackets = closed." withinPortal>
              <TextInput
                label={`Interval${intervalOptional ? "" : " *"}`}
                placeholder="Example: [-2, 5] or (-inf, 3]"
                description="Round brackets = open, square brackets = closed."
                {...form.getInputProps("interval")}
                required={!intervalOptional}
                disabled={isSubmitting}
                style={{ flex: 1, minWidth: 200 }}
                data-testid="analyze-interval"
                error={form.errors.interval}
              />
            </Tooltip>
          ) : null}
        </Group>

        <Checkbox
          label="Pretty presentation"
          {...form.getInputProps("present", { type: "checkbox" })}
          disabled={isSubmitting}
        />

        <Button type="submit" loading={isSubmitting} disabled={isSubmitDisabled}>
          Analyze
        </Button>

        {showInterval && form.errors.interval ? (
          <Text size="sm" c="red">
            {form.errors.interval}
          </Text>
        ) : null}
      </Stack>
    </form>
  );
};

export default AnalyzeForm;
