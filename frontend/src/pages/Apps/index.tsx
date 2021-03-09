import { useEffect } from "react";
import { useRecoilState } from "recoil";
import { appsState } from "../../store/apps";
import TableBody from "./TableBody";
import TableHeader from "./TableHeader";

const Apps = () => {
  const tableHeaders = ["name", "short_id", "created", "status", "ports"];

  const [, setApps] = useRecoilState(appsState);

  useEffect(() => {
    const fetchApps = async () => {
      await fetch("/api/apps/")
        .then((res) => res.json())
        .then((data) => {
          setApps(data);
        })
        .catch((err) => console.log(`Fetch error: ${err}`));
    };

    fetchApps();
  }, [setApps]);

  return (
    <div className={"flex flex-col justify-center align-center"}>
      <div className={"dark:text-white text-black text-4xl"}>
        Behold... apps!
      </div>
      <table className={"w-full table-auto my-4"}>
        <TableHeader headers={tableHeaders} />
        <TableBody />
      </table>
    </div>
  );
};

export default Apps;
