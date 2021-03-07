const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
  purge: [],
  darkMode: "class", // or 'media' or 'class'
  theme: {
    extend: {
      fontFamily: {
        yacht: ["Roboto", "sans-serif"],
      },
      colors: {
        "header-lgt": "#C4C4C4",
        "header-drk": "#424242",
        "icon-lgt": "#5A5A5A",
        "icon-drk": "#FFFFFF",
      },
    },
    screens: {
      'xs': '475px',
      ...defaultTheme.screens,
    },
  },
  variants: {
    extend: {},
  },
  plugins: [],
};
