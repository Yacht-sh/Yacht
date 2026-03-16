module.exports = {
  publicPath: "./",
  lintOnSave: false,
  transpileDependencies: ["vuetify"],

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
