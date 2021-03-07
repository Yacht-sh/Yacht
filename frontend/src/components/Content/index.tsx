import React from "react";
import { Switch, Route } from "react-router-dom";
import Apps from "../../pages/Apps";
import Dashboard from "../../pages/Dashboard";
import Projects from "../../pages/Projects";
import Resources from "../../pages/Resources";
import Settings from "../../pages/Settings";
import Templates from "../../pages/Templates";

const Content = () => {
  return (
    <div className={"ml-0 sm:ml-14 p-4"} data-testid={"app-content"}>
      <Switch>
        <Route path="/" exact component={Dashboard} />
        <Route path="/apps" component={Apps} />
        <Route path="/templates" component={Templates} />
        <Route path="/projects" component={Projects} />
        <Route path="/resources" component={Resources} />
        <Route path="/settings" component={Settings} />
        <Route
          path="/docs"
          component={() => {
            window.location.href = "https://yacht.sh";
            return null;
          }}
        />
        <Route
          path="/github"
          component={() => {
            window.location.href = "https://github.com/SelfHostedPro/Yacht";
            return null;
          }}
        />
      </Switch>
    </div>
  );
};

export default Content;
