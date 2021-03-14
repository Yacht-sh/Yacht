import React from "react";
import { render, screen } from "@testing-library/react";
import Settings from "../../components/Content/pages/Settings";

describe("Settings page tests", () => {
  it("should render the settings page", () => {
    render(<Settings />);
    const settings = screen.getByText(/settings/i);
  });
});
