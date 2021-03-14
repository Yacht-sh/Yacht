import clsx from "clsx";
import { Link } from "react-router-dom";
import { navLink } from ".";

interface OwnProps {
  link: navLink;
  onClick: () => void;
  isActiveView?: boolean;
}

const SideNavLink = ({ link, isActiveView, onClick }: OwnProps) => {
  return (
    <div onClick={onClick}>
      <Link to={link.address} data-testid={"side-nav-link"}>
        <div className={"side-nav-icon-container"}>
          <div className={clsx("side-nav-icon", isActiveView && "nav-active")}>
            <div className={"self-start"}>{link.icon}</div>
            <div className={"ml-6 truncate"}>{link.label}</div>
          </div>
        </div>
      </Link>
      <hr className={""} />
    </div>
  );
};

export default SideNavLink;
