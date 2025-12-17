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
            primary: "#00E5FF", // Cyan A400 - Modern neon accent
            secondary: "#1E293B", // Slate 800
            accent: "#10B981", // Emerald 500
            error: "#EF4444", // Red 500
            info: "#3B82F6", // Blue 500
            success: "#10B981", // Emerald 500
            warning: "#F59E0B", // Amber 500
            background: "#0F172A", // Slate 900
            tabs: "#1E293B",
            foreground: "#1E293B"
          },
          light: {
            primary: "#0EA5E9", // Sky 500
            secondary: "#F1F5F9", // Slate 100
            accent: "#10B981",
            error: "#EF4444",
            info: "#3B82F6",
            success: "#10B981",
            warning: "#F59E0B",
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
    // Keeping other themes for backward compatibility but default is updated
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
    }
  };
  return presetThemes[themeTheme || process.env.VUE_APP_THEME || "Default"];
}

export default new Vuetify(theme());
