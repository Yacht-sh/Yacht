import clsx from "clsx";
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { navLink } from ".";

interface OwnProps {
  link: navLink;
  isNavExpanded: boolean;
}

const SideNavLink = ({ link, isNavExpanded = false }: OwnProps) => {
  const [isDisplayText, setIsDisplayText] = useState(false);

  useEffect(() => {
    const expandTimeout = () =>
      setTimeout(() => {
        setIsDisplayText(true);
      }, 150);

    isNavExpanded && expandTimeout();
    !isNavExpanded && setIsDisplayText(false);

    return clearTimeout(expandTimeout());
  }, [isNavExpanded]);

  return (
    <div>
      <Link to={link.address} data-testid={"side-nav-link"}>
        <div className={"side-nav-icon-container"}>
          <div className={"side-nav-icon"}>
            <div className={"self-start"}>{link.icon}</div>
            <div className={clsx("ml-5", isDisplayText ? "block" : "hidden")}>
              {link.label}
            </div>
          </div>
        </div>
      </Link>
      <hr className={""} />
    </div>
  );
};

export default SideNavLink;
