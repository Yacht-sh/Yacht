import React from "react";
import { Link } from "react-router-dom";
import ApplicationsIcon from "../../icons/Nav/ApplicationsIcon";
import DashboardIcon from "../../icons/Nav/DashboardIcon";
import DocsIcon from "../../icons/Nav/DocsIcon";
import GithubIcon from "../../icons/Nav/GithubIcon";
import ProjectsIcon from "../../icons/Nav/ProjectsIcon";
import ResourcesIcon from "../../icons/Nav/ResourcesIcon";
import SettingsIcon from "../../icons/Nav/SettingsIcon";
import TemplatesIcon from "../../icons/Nav/TemplatesIcon";
import SideNavLink from "./SideNavLink";

export interface navLink {
  label: string;
  address: string;
  icon?: JSX.Element;
}

export const navLinks: navLink[] = [
  { label: "dash", address: "/", icon: <DashboardIcon /> },
  { label: "apps", address: "/apps", icon: <ApplicationsIcon /> },
  { label: "tmpl", address: "/templates", icon: <TemplatesIcon /> },
  { label: "proj", address: "/projects", icon: <ProjectsIcon /> },
  { label: "rsrc", address: "/resources", icon: <ResourcesIcon /> },
  { label: "stgs", address: "/settings", icon: <SettingsIcon /> },
];

const bottomLinks: navLink[] = [
  { label: "yacht", address: "/docs", icon: <DocsIcon /> },
  { label: "github", address: "/github", icon: <GithubIcon /> },
];

const Nav = () => {
  return (
    <div className={"nav"} data-testid={"app-nav"}>
      <div className={"side-nav"}>
        <div className={"side-nav-container"}>
          <div>
            {navLinks.map((link, index) => (
              <SideNavLink key={`link-${index}`} link={link} />
            ))}
          </div>
          <div>
            {bottomLinks.map((link, index) => (
              <SideNavLink key={`link-${index}`} link={link} />
            ))}
          </div>
        </div>
      </div>
      <div className={"bottom-nav"}>
        <div
          className={"bottom-nav-container"}
        >
          {navLinks.map((link, index) => (
            <Link
              key={`link-${index}`}
              to={link.address}
              data-testid={"nav-link"}
            >
              {link.label}
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Nav;
