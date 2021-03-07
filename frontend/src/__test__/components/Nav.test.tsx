import React from "react";
import { render, screen } from "@testing-library/react";
import Nav, { navLinks } from "../../components/Nav";
import { BrowserRouter as Router } from "react-router-dom";

describe("<Nav /> tests", () => {
  it("should render a sidebar or bottombar with links", () => {
    render(
      <Router>
        <Nav />
      </Router>
    );
    
    const navLinksFound = screen.getAllByTestId("nav-link");

    expect(navLinksFound.length).toEqual(navLinks.length * 2 + 2);
  });
});
