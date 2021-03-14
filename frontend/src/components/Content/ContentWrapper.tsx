import React, { FC } from "react";

interface OwnProps {
  header: string;
}

const ContentWrapper: FC<OwnProps> = ({ header, children }) => {
  return (
    <div
      className={
        "rounded bg-gray-50 dark:bg-content-drk shadow-md ml-0 sm:ml-2"
      }
    >
      <div
        className={
          "text-black dark:text-white text-3xl bg-content-header rounded-t p-4"
        }
      >
        {header}
      </div>
      <div className={"dark:text-white text-black p-2"}>{children}</div>
    </div>
  );
};

export default ContentWrapper;
