import React from "react";

const pathD = "M13,3V9H21V3M13,21H21V11H13M3,21H11V15H3M3,13H11V3H3V13Z";

const DashboardIcon = () => {
  return (
    <svg
      xmlns={"http://www.w3.org/2000/svg"}
      viewBox={"0 0 24 24"}
      className={"w-6 h-6"}
    >
      <path d={pathD} fill={"currentColor"} />
    </svg>
  );
};

export default DashboardIcon;
