/* eslint-disable */
if (!self.define) {
  const e = e => {
      "require" !== e && (e += ".js");
      let s = Promise.resolve();
      return (
        o[e] ||
          (s = new Promise(async s => {
            if ("document" in self) {
              const o = document.createElement("script");
              (o.src = e), document.head.appendChild(o), (o.onload = s);
            } else importScripts(e), s();
          })),
        s.then(() => {
          if (!o[e]) throw new Error(`Module ${e} didn’t register its module`);
          return o[e];
        })
      );
    },
    s = (s, o) => {
      Promise.all(s.map(e)).then(e => o(1 === e.length ? e[0] : e));
    },
    o = { require: Promise.resolve(s) };
  self.define = (s, r, i) => {
    o[s] ||
      (o[s] = Promise.resolve().then(() => {
        let o = {};
        const a = { uri: location.origin + s.slice(1) };
        return Promise.all(
          r.map(s => {
            switch (s) {
              case "exports":
                return o;
              case "module":
                return a;
              default:
                return e(s);
            }
          })
        ).then(e => {
          const s = i(...e);
          return o.default || (o.default = s), o;
        });
      }));
  };
}
define("./sw.js", ["./workbox-9a26cde2"], function(e) {
  "use strict";
  self.addEventListener("message", e => {
    e.data && "SKIP_WAITING" === e.data.type && self.skipWaiting();
  }),
    e.precacheAndRoute(
      [
        { url: "App.vue", revision: "dd6cc0d2abccba8f888ea47d28c319a6" },
        {
          url: "assets/logo-light.svg",
          revision: "2d45f5a18e0e1895d828955d6f6355a8"
        },
        {
          url: "assets/logo.png",
          revision: "f844954952434a2a6977af5c358a50ca"
        },
        {
          url: "assets/logo.svg",
          revision: "60ff54d9dbc103501aba15a7a5e6e0fd"
        },
        {
          url: "components/applications/ApplicationDeployFromTemplate.vue",
          revision: "7057e9e0da11e5ad36fd4057c5c6d17f"
        },
        {
          url: "components/applications/ApplicationDetails.vue",
          revision: "9542d807cc291085ec8bdf073fc66363"
        },
        {
          url:
            "components/applications/ApplicationDetailsComponents/AppContent.vue",
          revision: "f423db5682ba61f04b7ea139a2aa94f8"
        },
        {
          url:
            "components/applications/ApplicationDetailsComponents/AppLogs.vue",
          revision: "fd45eb7a195fbb980fa6958393cd40bf"
        },
        {
          url:
            "components/applications/ApplicationDetailsComponents/AppProcesses.vue",
          revision: "c9ea4dce3dcf13b0ee0831c82a630790"
        },
        {
          url:
            "components/applications/ApplicationDetailsComponents/AppStats.vue",
          revision: "d7d2aaa62881739b2f046de4624f6b83"
        },
        {
          url: "components/applications/ApplicationsForm.vue",
          revision: "727a81d9f4038c768c9ce1f0d1669d28"
        },
        {
          url: "components/applications/ApplicationsList.vue",
          revision: "9ca8e9328d4eea335bb66c87113ea7bd"
        },
        {
          url: "components/auth/LoginForm.vue",
          revision: "2d5640b1f7ef7941abd645cc8cf3123a"
        },
        {
          url: "components/charts/PercentBarChart.vue",
          revision: "ae5788526bb243325fd4a1c2c1ebb143"
        },
        {
          url: "components/charts/PercentLineChart.vue",
          revision: "4b840662cd8cf4b470191bc08967ed18"
        },
        {
          url: "components/compose/ProjectDetails.vue",
          revision: "bfb2c79f06cfd1723adb6c601f15f8fe"
        },
        {
          url: "components/compose/ProjectEditor.vue",
          revision: "8f5fe769beff8fb1a88f553549c73cdd"
        },
        {
          url: "components/compose/ProjectList.vue",
          revision: "cf928ee021d09d5572794dc45789ecd4"
        },
        {
          url: "components/HelloWorld.vue",
          revision: "d1addc86b3ba73583cf8d9e27c11e234"
        },
        {
          url: "components/nav/Appbar.vue",
          revision: "504a7886265aa77f45fcb9f20a757e38"
        },
        {
          url: "components/nav/Bottombar.vue",
          revision: "ce8673753ad2a1d69c39f1979fd6f0f4"
        },
        {
          url: "components/nav/Sidebar.vue",
          revision: "fd629274835bdf7d12a473cecdd40cd1"
        },
        {
          url: "components/notifications/snackbar.vue",
          revision: "cdda434500e68c08b6c067cd63bd6d4f"
        },
        {
          url: "components/resources/images/ImageDetails.vue",
          revision: "adcfb7d44892f850a6951c9ea4f9b6a7"
        },
        {
          url: "components/resources/images/ImageList.vue",
          revision: "1227f0e943db97eec07828ee453812e2"
        },
        {
          url: "components/resources/networks/NetworkDetails.vue",
          revision: "6664a856393f3f52a766de9bfe639c31"
        },
        {
          url: "components/resources/networks/NetworkForm.vue",
          revision: "95f652e171fa1d2d17ba7cc1852140cc"
        },
        {
          url: "components/resources/networks/NetworkList.vue",
          revision: "ae2b5d5ba8f335bbca3efd663aa531f9"
        },
        {
          url: "components/resources/volumes/VolumeDetails.vue",
          revision: "ec1f271809bd8849470fc1836f41998b"
        },
        {
          url: "components/resources/volumes/VolumeList.vue",
          revision: "5b8cde34b6a7c7d7fa845eba4dc88a1b"
        },
        {
          url: "components/serverSettings/Prune.vue",
          revision: "25462f4f9af4f502f9a895fe27f4246a"
        },
        {
          url: "components/serverSettings/ServerInfo.vue",
          revision: "4a762fa25124814f127f927a86bcc5ef"
        },
        {
          url: "components/serverSettings/ServerSettingsNav.vue",
          revision: "e04d347ec03885a506e152e09d2a1d78"
        },
        {
          url: "components/serverSettings/ServerUpdate.vue",
          revision: "82c363af058240b85dadf724155d7d39"
        },
        {
          url: "components/serverSettings/ServerVariables.vue",
          revision: "4a4af2d21af6cd3f27c7ee234a9ebe63"
        },
        {
          url: "components/serverSettings/Theme.vue",
          revision: "475ae502883c3775571fa67d1077d61d"
        },
        {
          url: "components/templates/TemplatesDetails.vue",
          revision: "f2d48a4c9cdbead28417abb711a9af58"
        },
        {
          url: "components/templates/TemplatesForm.vue",
          revision: "0001ac727769ed71494fb44f65262c9c"
        },
        {
          url: "components/templates/TemplatesList.vue",
          revision: "4a836d527cbdd05f7620edd011516eec"
        },
        {
          url: "components/userSettings/ChangePasswordForm.vue",
          revision: "0ef9832162e095f7fe833901485b84ce"
        },
        {
          url: "components/userSettings/UserInfo.vue",
          revision: "efac951a91ef420de72d9cd907e41dfd"
        },
        {
          url: "components/userSettings/UserSettingsNav.vue",
          revision: "d78933ad27f6f287ae3679ae2dd0f7f6"
        },
        { url: "config.js", revision: "670b1e8a8bb5882ab187707a9d7f83e8" },
        { url: "main.js", revision: "e0f4ef1b1d5e06b36e1ac176bbff2c21" },
        {
          url: "plugins/vuetify.js",
          revision: "015fceccfa96259165580d1a440c5f7a"
        },
        {
          url: "plugins/vueutils.js",
          revision: "309224b5367b5a6dd13b0c09ef4a4c3a"
        },
        {
          url: "registerServiceWorker.js",
          revision: "0ff849d18bb23c5a386f02f93a3183a4"
        },
        {
          url: "router/index.js",
          revision: "5137126c84eff7ebe602e06585f59538"
        },
        {
          url: "store/actions/auth.js",
          revision: "73d742a4033b8def17be794aa0372a31"
        },
        { url: "store/index.js", revision: "34f3a5a6d41a237f180b11725ba5eec4" },
        {
          url: "store/modules/apps.js",
          revision: "32f80ac72660786c2d6539a7b4cec3b4"
        },
        {
          url: "store/modules/auth.js",
          revision: "76b4dc421e5e63c2bd547ac4302d2967"
        },
        {
          url: "store/modules/images.js",
          revision: "57947f309c0343f0283db82a8157dfb6"
        },
        {
          url: "store/modules/networks.js",
          revision: "16f6f81ec89879e11e5d9a1423b89039"
        },
        {
          url: "store/modules/projects.js",
          revision: "d39a0cad6c801e4ccd18c57bb5d4c223"
        },
        {
          url: "store/modules/snackbar.js",
          revision: "646d4f012b1dbafae5b8e5992554db30"
        },
        {
          url: "store/modules/templates.js",
          revision: "1390831db9f2094c08ac132ac4e45b41"
        },
        {
          url: "store/modules/volumes.js",
          revision: "d2b538d52e7c1f87e0958383aa5493ca"
        },
        {
          url: "vee-validate.js",
          revision: "97267839f1b28e5224f2ecb4e57b5bd1"
        },
        {
          url: "views/Applications.vue",
          revision: "85b734df27543e7af12329a751e87711"
        },
        {
          url: "views/Container.vue",
          revision: "d6341b18d1c5731b497e0611b5b1fbfe"
        },
        { url: "views/Home.vue", revision: "1fde54733a7d9abf7ddcd1a04446cb27" },
        {
          url: "views/Project.vue",
          revision: "3389f2781046961ce610c6cb62cca1a7"
        },
        {
          url: "views/Resources.vue",
          revision: "fbeee3af7e25653b7fc352f52838ac4c"
        },
        {
          url: "views/ServerSettings.vue",
          revision: "a6dcf519afa94e3019daba9bf5b10e11"
        },
        {
          url: "views/Templates.vue",
          revision: "554f8df6ad308aa8464633e9260f8c07"
        },
        {
          url: "views/UserSettings.vue",
          revision: "63a5303e0d91c743855ace35eb33e690"
        }
      ],
      {}
    );
});
//# sourceMappingURL=sw.js.map
