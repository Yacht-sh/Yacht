import React from "react";
import { render, screen } from "@testing-library/react";
import Projects from "../../components/Content/pages/Projects";

describe("Projects page tests", () => {
  it("should render the projects page", () => {
    render(<Projects />);
    const projects = screen.getByText(/projects/i);
  });
});
