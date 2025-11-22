import { vi } from "vitest";

vi.mock("@mantine/notifications", () => ({
  notifications: {
    show: vi.fn(),
  },
}));

vi.mock("../../../components/common/CopyButton.jsx", () => ({
  __esModule: true,
  default: ({ label }) => <button>{label}</button>,
}));

import { render, screen } from "@testing-library/react";

import ResultView from "../ResultView.jsx";

describe("ResultView", () => {
  it("renders narrative content when present", () => {
    render(
      <ResultView
        data={{
          action: "domain",
          expr: "x^2",
          var: "x",
          report: "",
          warnings: [],
          errors: [],
          present: { title: "Title", doc_md: "<p>Markdown</p>" },
        }}
      />
    );

    expect(screen.getByText("Title")).toBeInTheDocument();
    expect(screen.getByText("Markdown")).toBeInTheDocument();
  });

  it("falls back to JSON when no narrative", () => {
    render(
      <ResultView
        data={{
          action: "domain",
          expr: "x^2",
          var: "x",
          report: "",
          warnings: [],
          errors: [],
          present: {},
        }}
      />
    );

    expect(screen.getByText("Copy JSON")).toBeInTheDocument();
    expect(screen.getByText(/"action":/)).toBeInTheDocument();
  });

  it("renders warnings and errors", () => {
    render(
      <ResultView
        data={{
          action: "domain",
          expr: "x^2",
          var: "x",
          report: "",
          warnings: ["be careful"],
          errors: ["invalid"],
          present: {},
        }}
      />
    );

    expect(screen.getByText("Warnings 1")).toBeInTheDocument();
    expect(screen.getByText("Errors 1")).toBeInTheDocument();
    expect(screen.getByText("be careful")).toBeInTheDocument();
    expect(screen.getByText("invalid")).toBeInTheDocument();
  });
});
