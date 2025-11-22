describe("Auth and Ask flow", () => {
  beforeEach(() => {
    cy.intercept("POST", "**/auth/register", {
      statusCode: 201,
      body: { token: "test-token-123" },
    }).as("register");
    cy.intercept("POST", "**/auth/login", {
      body: { access_token: "test-token-123" },
    }).as("login");
    cy.intercept("POST", "**/llm/analyze", {
      body: {
        action: "domain",
        expr: "(x^2 - 1)/(x - 1)",
        var: "x",
        report: "Sample report",
        warnings: [],
        errors: [],
        present: {
          title: "Domain Analysis",
          doc_md: "<p>All real numbers except x = 1.</p>",
        },
      },
    }).as("analyze");
  });

  it("registers, logs in, and submits an analysis", () => {
    cy.visit("/register");

    cy.get('input[placeholder="Choose a username"]').type("tester");
    cy.get('input[placeholder="Create a password"]').type("secret123");
    cy.contains("button", "Create account").click();
    cy.wait("@register");
    cy.url().should("include", "/ask");

    cy.contains("button", "Logout").click();
    cy.url().should("include", "/login");

    cy.get('input[placeholder="Your username"]').type("tester");
    cy.get('input[placeholder="Your password"]').type("secret123");
    cy.contains("button", "Sign in").click();
    cy.wait("@login");
    cy.url().should("include", "/ask");

    cy.get('input[placeholder="e.g. (x^2 - 1)/(x - 1)"]').clear().type("(x^2 - 1)/(x - 1)");
    cy.get('[data-testid="analyze-action"]').click();
    cy.contains("extrema & monotonic").click();
    cy.get('[data-testid="analyze-interval"]').should("be.visible").type("[-2, 5]");
    cy.contains("button", "Analyze").click();
    cy.wait("@analyze");
    cy.contains("Domain Analysis").should("be.visible");
  });
});
