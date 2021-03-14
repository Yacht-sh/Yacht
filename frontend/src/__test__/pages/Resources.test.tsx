import React from "react";
import { render, screen } from "@testing-library/react";
import Resources from "../../components/Content/pages/Resources";

describe("Resources page tests", () => {
  it("should render the resources page", () => {
    render(<Resources />);
    const resources = screen.getByText(/resources/i);
  });
});
