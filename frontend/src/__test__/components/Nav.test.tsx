import React from "react";
import { render, screen } from "@testing-library/react";
import Nav, { bottomNavLinks, sideNavLinks } from "../../components/Nav";
import { BrowserRouter as Router } from "react-router-dom";

describe("<Nav /> tests", () => {
  it("should render a sidebar or bottombar with links", () => {
    render(
      <Router>
        <Nav />
      </Router>
    );

    const sideNavLinksFound = screen.getAllByTestId("side-nav-link");
    const bottomNavLinksFound = screen.getAllByTestId("bottom-nav-link");

    expect(sideNavLinksFound.length).toEqual(sideNavLinks.length + 2);
    expect(bottomNavLinksFound.length).toEqual(bottomNavLinks.length);
  });
});
