import React from "react";
import { render, screen } from "@testing-library/react";
import Templates from "../../components/Content/pages/Templates";

describe("Templates page tests", () => {
  it("should render the templates page", () => {
    render(<Templates />);
    const templates = screen.getByText(/templates/i);
  });
});
