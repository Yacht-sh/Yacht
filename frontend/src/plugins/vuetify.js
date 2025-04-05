import Vue from "vue";
import Vuetify from "vuetify/lib";
import { themeTheme } from "../config.js";
import "@mdi/font/css/materialdesignicons.css";

Vue.use(Vuetify);

function theme() {
  var presetThemes = {
    Default: {
      theme: {
        themes: {
          dark: {
            primary: "#41b883",
            secondary: "#424242",
            background: "#000000",
            tabs: "#1E1E1E",
            foreground: "#1E1E1E"
          },
          light: {
            primary: "#41b883",
            secondary: "#c4c4c4",
            background: "#FFFFFF",
            tabs: "#FFFFFF",
            foreground: "#FFFFFF"
          }
        },
        dark: true,
        options: {
          customProperties: true
        }
      }
    },
    DigitalOcean: {
      theme: {
        dark: false,
        themes: {
          light: {
            primary: "#008bcf",
            secondary: "#F3F5F9",
            background: "#FFFFFF",
            tabs: "#FFFFFF",
            foreground: "#FFFFFF"
          },
          dark: {
            primary: "#008bcf",
            secondary: "#424242",
            background: "#000000",
            tabs: "#1E1E1E",
            foreground: "#1E1E1E"
          }
        },
        options: {
          customProperties: true
        }
      }
    },
    OMV: {
      theme: {
        dark: false,
        themes: {
          light: {
            primary: "#3A6D9C",
            secondary: "#5DACDF",
            background: "#FFFFFF",
            tabs: "#5DACDF",
            foreground: "#ECEFF1"
          },
          dark: {
            primary: "#3A6D9C",
            secondary: "#2B5174",
            background: "#132433",
            tabs: "#333B53",
            foreground: "#333B53"
          }
        },
        options: {
          customProperties: true
        }
      }
    },
    RED: {
      theme: {
        dark: true,
        themes: {
          light: {
            primary: "#B71C1C",
            secondary: "#C4C4C4",
            background: "#FFFFFF",
            tabs: "#FFFFFF",
            foreground: "#FFFFFF"
          },
          dark: {
            primary: "#B71C1C",
            secondary: "#1E1E1E",
            background: "#000000",
            tabs: "#1E1E1E",
            foreground: "#1E1E1E"
          }
        },
        options: {
          customProperties: true
        }
      }
    }
  };
  return presetThemes[themeTheme || process.env.VUE_APP_THEME || "Default"];
}

export default new Vuetify(theme());
