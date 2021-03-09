import React from "react";
import ChevronDown from "../../icons/ChevronDown";
import YachtLogoDark from "../../icons/YachtLogoDark";
import YachtLogoLight from "../../icons/YachtLogoLight";
import { User } from "../../utils";

interface OwnProps {
  user: User;
  isThemeTypeDark: boolean;
  toggleThemeType: () => void;
}

const Header = ({ user, isThemeTypeDark, toggleThemeType }: OwnProps) => {
  return (
    <div className={"header mat-ui-shadow"} data-testid={"app-header"}>
      <div className={"flex flex-row justify-between"}>
        <div className={"flex flex-row text-xl"}>
          {isThemeTypeDark ? <YachtLogoDark /> : <YachtLogoLight />}{" "}
          <span className={"ml-2 hidden xs:block"}>Yacht</span>
        </div>
        <span className={"font-bold text-xl hidden md:block"}>Home</span>
        <div
          className={"btn mat-ui-shadow cursor-pointer"}
          style={{ backgroundColor: "#41B883", height: "36px" }}
          onClick={toggleThemeType}
        >
          <span className={"hidden sm:block"}>{user.username}</span>
          <ChevronDown />
        </div>
      </div>
    </div>
  );
};

export default Header;
