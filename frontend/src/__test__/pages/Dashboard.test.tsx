import React from "react";
import { render, screen } from "@testing-library/react";
import Dashboard from "../../components/Content/pages/Dashboard";

describe("Dashboard page tests", () => {
  it("should render the dashboard page", () => {
    render(<Dashboard />);
    const dashboard = screen.getByText(/dashboard/i);
  });
});
