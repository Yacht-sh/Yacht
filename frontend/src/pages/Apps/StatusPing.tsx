import clsx from "clsx";
import React from "react";

interface OwnProps {
  status: string;
}

const StatusPing = ({ status }: OwnProps) => {
  return (
    <div
      className={clsx(
        "w-4 h-4 rounded-full",
        status !== "running" ? "bg-red-500" : "bg-green-500"
      )}
      style={{ content: " " }}
    />
  );
};

export default StatusPing;
