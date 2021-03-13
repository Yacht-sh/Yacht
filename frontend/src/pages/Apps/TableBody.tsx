import React from "react";
import { useRecoilValue } from "recoil";
import { appsState } from "../../store/apps";
import TableRow from "./TableRow";

const TableBody = () => {
  const apps = useRecoilValue(appsState);

  return (
    <tbody
      className={
        "text-gray-700 dark:text-gray-300 bg-transparent text-sm font-light"
      }
    >
      {apps.length > 0 ? (
        apps.map((app, index) => <TableRow app={app} key={`row-${index}`} />)
      ) : (
        <tr>
          <span>Loading apps...</span>
        </tr>
      )}
    </tbody>
  );
};

export default TableBody;
