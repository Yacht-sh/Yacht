import { atom } from "recoil";

export enum ViewState {
  "DASHBOARD",
  "APPLICATIONS",
  "TEMPLATES",
  "PROJECTS",
  "RESOURCES",
  "SETTINGS",
}

export const viewState = atom({
  key: "ViewState",
  default: ViewState[0],
});
