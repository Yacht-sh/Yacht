import clsx from "clsx";
import React, { useState } from "react";
import { Link } from "react-router-dom";
import ApplicationsIcon from "../../icons/Nav/ApplicationsIcon";
import DashboardIcon from "../../icons/Nav/DashboardIcon";
import DocsIcon from "../../icons/Nav/DocsIcon";
import GithubIcon from "../../icons/Nav/GithubIcon";
import PlusCircleIcon from "../../icons/Nav/PlusCircleIcon";
import ProjectsIcon from "../../icons/Nav/ProjectsIcon";
import ResourcesIcon from "../../icons/Nav/ResourcesIcon";
import SettingsIcon from "../../icons/Nav/SettingsIcon";
import TemplatesIcon from "../../icons/Nav/TemplatesIcon";
import SideNavLink from "./SideNavLink";

export interface navLink {
  label: string;
  address: string;
  icon: JSX.Element;
}

export const sideNavLinks: navLink[] = [
  { label: "Dashboard", address: "/", icon: <DashboardIcon /> },
  { label: "Applications", address: "/apps", icon: <ApplicationsIcon /> },
  { label: "Templates", address: "/templates", icon: <TemplatesIcon /> },
  { label: "Projects", address: "/projects", icon: <ProjectsIcon /> },
  { label: "Resources", address: "/resources", icon: <ResourcesIcon /> },
  { label: "Settings", address: "/settings", icon: <SettingsIcon /> },
];

const sideNavLowerLinks: navLink[] = [
  { label: "Yacht Home", address: "/docs", icon: <DocsIcon /> },
  { label: "Yacht Github", address: "/github", icon: <GithubIcon /> },
];

export const bottomNavLinks: navLink[] = [
  { label: "Dashboard", address: "/", icon: <DashboardIcon /> },
  { label: "Applications", address: "/apps", icon: <ApplicationsIcon /> },
  { label: "Deploy", address: "/", icon: <PlusCircleIcon /> },
  { label: "Resources", address: "/resources", icon: <ResourcesIcon /> },
  { label: "Settings", address: "/settings", icon: <SettingsIcon /> },
];

const Nav = () => {
  const [isNavExpanded, setIsNavExpanded] = useState(false);

  return (
    <div className={"nav"} data-testid={"app-nav"}>
      <div
        className={clsx("side-nav", isNavExpanded ? "w-52" : "w-16")}
        onMouseEnter={() => setIsNavExpanded(true)}
        onMouseLeave={() => setIsNavExpanded(false)}
      >
        <div className={"side-nav-container"}>
          <div>
            {sideNavLinks.map((link, index) => (
              <SideNavLink
                key={`link-${index}`}
                link={link}
                isNavExpanded={isNavExpanded}
              />
            ))}
          </div>
          <div>
            {sideNavLowerLinks.map((link, index) => (
              <SideNavLink
                key={`link-${index}`}
                link={link}
                isNavExpanded={isNavExpanded}
              />
            ))}
          </div>
        </div>
      </div>
      <div className={"bottom-nav"}>
        <div className={"bottom-nav-container"}>
          {bottomNavLinks.map((link, index) => (
            <Link
              key={`link-${index}`}
              to={link.address}
              data-testid={"bottom-nav-link"}
            >
              <div className={"flex flex-col justify-center items-center"}>
                {link.icon}
                <span className={"text-xs mt-1"}>{link.label}</span>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Nav;
