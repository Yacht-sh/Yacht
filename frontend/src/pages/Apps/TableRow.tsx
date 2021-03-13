import React from "react";
import clsx from "clsx";

import { App } from "../../store/apps";
import ChevronDown from "../../icons/ChevronDown";
import StatusPing from "./StatusPing";

interface OwnProps {
  app: App;
}

const TableRow = ({ app }: OwnProps) => {
  const { name, short_id, created, status, ports } = app;
  const appData = [name, short_id, created, status];

  return (
    <tr className={"border-b border-gray-200 hover:bg-gray-100"}>
      {appData.map((data, index) => (
        <td
          key={`data-${index}`}
          className={clsx(
            index === 0 && "flex flex-row justify-start",
            index === 1 && "hidden md:table-cell",
            index === 2 && "hidden lg:table-cell",
            index === 3 && "hidden xs:table-cell",
            "py-3 px-6 text-center"
          )}
        >
          {index === 0 && (
            <>
              <StatusPing status={status} /> <ChevronDown />
            </>
          )}
          {data}
        </td>
      ))}
      <td className={"py-2 px-4 sm:px-2 text-center"}>
        {ports.map((port, index) => (
          <div key={`port-${index}`} className={"my-2"}>
            <span className="px-2 py-1 text-purple-600 bg-purple-200 rounded-full tex1t-sm my- has-tooltip">
              <a
                href={`http://${
                  port.HostIp === "0.0.0.0" ? "localhost" : port.HostIp
                }:${port.HostPort}`}
              >
                {port.Label ? port.Label : port.HostPort}
              </a>
            </span>
          </div>
        ))}
      </td>
    </tr>
  );
};

export default TableRow;
