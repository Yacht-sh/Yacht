import clsx from "clsx";
import { useState } from "react";
import { mockUser } from "../../utils";
import Content from "../Content";
import Header from "../Header";
import Nav from "../Nav";

enum ThemeType {
  DARK = "dark",
  LIGHT = "light"
}

const App = () => {
  const [themeType, setThemeType] = useState(ThemeType.DARK)

  const toggleThemeType = () => {
    if (themeType === ThemeType.DARK) {
      setThemeType(ThemeType.LIGHT)
    } else {
      setThemeType(ThemeType.DARK)
    }
  }

   return (
    <div className={clsx("app-container overflow-hidden", themeType)} data-testid={"app-container"}>
      <Header user={mockUser} isThemeTypeDark={themeType === ThemeType.DARK} toggleThemeType={toggleThemeType}/>
      <Nav />
      <Content />
    </div>
  );
};

export default App;
