import { useMutation } from "@tanstack/react-query";

import { analyze } from "../../api/llm.js";

const normalizeAnalyzeResponse = (payload = {}) => {
  const warnings = Array.isArray(payload.warnings) ? payload.warnings : [];
  const errors = Array.isArray(payload.errors) ? payload.errors : [];

  // Handle present as either a string (new format) or object (legacy format)
  let present = null;
  if (typeof payload.present === "string" && payload.present.trim().length > 0) {
    present = payload.present.trim();
  } else if (payload.present && typeof payload.present === "object") {
    // Legacy format: present object with title, narration, doc_md
    present = {
      title: payload.present?.title ?? "",
      narration: payload.present?.narration ?? "",
      doc_md: payload.present?.doc_md ?? "",
    };
  }

  return {
    action: payload.action ?? "",
    expr: payload.expr ?? "",
    var: payload.var ?? "",
    report: payload.report ?? "",
    warnings,
    errors,
    present,
  };
};

const analyzeRequest = async (input = {}) => {
  const payload = {
    raw: input.raw,
    var: input.var,
    action: input.action,
    present: input.present,
  };

  if (Array.isArray(input.interval) && input.interval.length === 2) {
    payload.interval = input.interval;
  }

  if (Array.isArray(input.closed) && input.closed.length === 2) {
    payload.closed = input.closed;
  }

  if (payload.action === "asymptotes_and_holes") {
    console.log("[useAnalyze] asymptotes payload", payload);
  }

  const response = await analyze(payload);
  return normalizeAnalyzeResponse(response);
};

export const useAnalyze = () => {
  const mutation = useMutation({
    mutationKey: ["llm", "analyze"],
    mutationFn: analyzeRequest,
  });

  return {
    ...mutation,
    isLoading: mutation.isPending,
  };
};

export default useAnalyze;
