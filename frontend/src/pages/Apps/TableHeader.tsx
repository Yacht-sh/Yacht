import React from "react";
import clsx from "clsx";

interface OwnProps {
  headers: string[];
}

const TableHeader = ({ headers }: OwnProps) => {
  return (
    <thead>
      <tr
        className={
          "bg-gray-300 dark:bg-gray-700 text-black dark:text-white uppercase text-lg leading-normal"
        }
      >
        {headers.map((header, index) => {
          return (
            <th
              className={clsx(
                header === "created" && "hidden lg:table-cell",
                header === "short_id" && "hidden md:table-cell"
              )}
              key={`header-${index}`}
            >
              {header}
            </th>
          );
        })}
      </tr>
    </thead>
  );
};

export default TableHeader;
