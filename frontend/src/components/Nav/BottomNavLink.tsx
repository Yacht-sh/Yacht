import clsx from "clsx";
import React from "react";
import { Link } from "react-router-dom";
import { SetterOrUpdater } from "recoil";
import { navLink } from ".";

interface OwnProps {
  link: navLink;
  isActiveView: boolean;
  onClick: SetterOrUpdater<string>;
}

const BottomNavLink = ({ isActiveView, link, onClick }: OwnProps) => {
  return (
    <Link to={link.address} data-testid={"bottom-nav-link"}>
      <div
        className={clsx(
          "flex flex-col justify-center items-center",
          isActiveView && "nav-active"
        )}
        onClick={() => onClick(link.label.toUpperCase())}
      >
        {link.icon}
        <span className={"text-xs mt-1 select none"}>{link.label}</span>
      </div>
    </Link>
  );
};

export default BottomNavLink;
