import http from "../lib/http.js";

const ACTION_ALIASES = {
  asymptotes: "asymptotes_and_holes",
};

export const analyze = async ({ raw, var: variable, action, present, interval, closed }) => {
  const normalizedAction = ACTION_ALIASES[action] ?? action;

  const payload = {
    raw: raw ?? "",
    var: variable ?? "",
    action: normalizedAction ?? "",
    present: typeof present === "boolean" ? present : true,
  };

  if (Array.isArray(interval) && interval.length === 2) {
    payload.interval = interval;
  }

  if (Array.isArray(closed) && closed.length === 2) {
    payload.closed = closed.map((value) => Boolean(value));
  }

  try {
    const response = await http.post("/llm/analyze", payload);
    return response.data;
  } catch (error) {
    const status = error?.response?.status ?? null;
    if (status && status >= 400 && status < 500) {
      const detail = error?.response?.data?.detail;
      const message = Array.isArray(detail)
        ? detail.find((item) => typeof item?.msg === "string")?.msg
        : typeof detail === "string"
          ? detail
          : error?.response?.data?.error ?? null;
      if (message) {
        error.message = message;
      }
    }
    if (error?.response?.data) {
      console.error("[LLM analyze] error response", error.response.data);
    }
    throw error;
  }
};
