import "@testing-library/jest-dom/vitest";
import "whatwg-fetch";

import { afterAll, afterEach, beforeAll } from "vitest";

import { server } from "./server.js";

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => {
  server.resetHandlers();
  window.localStorage.clear();
});
afterAll(() => server.close());
