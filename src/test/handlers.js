import { http, HttpResponse } from "msw";

export const handlers = [
  http.post("/auth/login", async () => {
    return HttpResponse.json({ access_token: "test-token-123" });
  }),
  http.post("/auth/register", async () => {
    return HttpResponse.json({ token: "test-token-123" }, { status: 201 });
  }),
  http.post("/llm/analyze", async () => {
    return HttpResponse.json({
      action: "domain",
      expr: "x^2",
      var: "x",
      report: "Sample report",
      warnings: ["Keep domain in mind"],
      errors: [],
      present: {
        title: "Domain Analysis",
        doc_md: "<p>Domain is all real numbers.</p>",
      },
    });
  }),
];

export default handlers;
