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
      <div className={"flex flex-row justify-between items-center"}>
        <div className={"flex flex-row text-xl"}>
          {isThemeTypeDark ? <YachtLogoDark /> : <YachtLogoLight />}{" "}
          <span className={"ml-2 hidden sm:block"}>Yacht</span>
        </div>
        <span className={"font-bold text-xl hidden sm:block"}>Home</span>
        <span className={"font-bold text-xl block sm:hidden"}>Yacht</span>
        <div
          className={"btn mat-ui-shadow cursor-pointer -mt-0.5"}
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
