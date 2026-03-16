const sass = require("sass");

module.exports = {
  publicPath: "./",
  lintOnSave: false,
  transpileDependencies: ["vuetify"],
  css: {
    loaderOptions: {
      sass: {
        implementation: sass,
        sassOptions: {
          quietDeps: true,
          silenceDeprecations: [
            "legacy-js-api",
            "import",
            "global-builtin",
            "if-function",
            "slash-div",
          ],
        },
      },
      scss: {
        implementation: sass,
        sassOptions: {
          quietDeps: true,
          silenceDeprecations: [
            "legacy-js-api",
            "import",
            "global-builtin",
            "if-function",
            "slash-div",
          ],
        },
      },
    },
  },

  devServer: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        timeout: 6000,
        ws: true,
        changeOrigin: true,
        pathRewrite: {
          "^/api": "",
        },
        logLevel: "debug",
      },
    },
  },
};
