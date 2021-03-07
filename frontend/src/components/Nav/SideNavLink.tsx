import React from "react";
import { Link } from "react-router-dom";
import { navLink } from ".";

interface OwnProps {
  link: navLink;
}

const SideNavLink = ({ link }: OwnProps) => {
  return (
    <div>
      <Link to={link.address} data-testid={"nav-link"}>
        <div className={"side-nav-icon-container"}>
          <div className={"side-nav-icon"}>{link.icon}</div>
        </div>
      </Link>
      <hr className={""} />
    </div>
  );
};

export default SideNavLink;
