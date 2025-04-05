import axios from "axios";

const state = {
  apps: [],
  updatable: [],
  logs: [],
  processes: [],
  isLoading: false,
  isLoadingValue: null,
  action: ""
};

const mutations = {
  setApps(state, apps) {
    state.apps = apps;
  },
  setApp(state, app) {
    const idx = state.apps.findIndex(x => x.Name === app.Name);
    if (idx < 0) {
      state.apps.push(app);
    } else {
      state.apps.splice(idx, 1, app);
    }
  },
  setAppProcesses(state, processes) {
    state.processes = processes;
  },
  setAppLogs(state, logs) {
    state.logs = logs;
  },
  setLoading(state, loading) {
    state.isLoading = loading;
  },
  setLoadingItems(state) {
    state.isLoadingValue = 0;
  },
  setLoadingItemCompleted(state, total) {
    let quotent = 1 / total;
    let increment = quotent * 100;
    state.isLoadingValue += increment;
  },
  setLoadingComplete(state) {
    state.isLoadingValue == null;
  },
  setAction(state, action) {
    state.action = action;
  },
  setUpdatable(state, updatable) {
    state.updatable = updatable;
  },
  setUpdated(state, updated) {
    let index = state.updatable.indexOf(updated);
    state.updatable.splice(index, 1);
  }
};

const actions = {
  async readApps({ commit }) {
    await commit("setLoading", true);
    await commit("setAction", "Getting Apps ...");
    const url = "/api/apps/";
    await axios
      .get(url)
      .then(response => {
        var apps = response.data;
        commit("setApps", apps);
      })
      .catch(err => {
        commit("snackbar/setErr", err, { root: true });
      })
      .finally(() => {
        commit("setLoading", false);
        commit("setAction", "");
      });
  },
  // async _checkAppUpdate({ commit }, apps) {
  //   await commit("setLoading", true);
  //   await commit("setLoadingItems");
  //   await commit("setAction", "Checking for updates...");
  //   await Promise.all(
  //     apps.map(async (_update) => {
  //       let url = `/api/apps/${_update.name}/updates`;
  //       await axios
  //         .get(url)
  //         .then((response) => {
  //           let app = response.data;
  //           if (app.isUpdatable) {
  //             commit("setUpdatable", app);
  //             commit("setLoadingItemCompleted", apps.length);
  //           }
  //         })
  //         .catch((err) => {
  //           commit("snackbar/setErr", err, { root: true });
  //         })
  //         .finally(() => {
  //           commit("setLoading", false);
  //           commit("setAction", "");
  //         });
  //     })
  //   );
  // },
  async checkAppUpdate({ commit }, apps) {
    await commit("setLoading", true);
    await commit("setLoadingItems");
    await commit("setAction", "Checking for updates...");
    await Promise.all(
      apps.map(async _app => {
        let url = `/api/apps/${_app.name}/updates`;
        await axios
          .get(url)
          .then(response => {
            let app = response.data;
            commit("setLoadingItemCompleted", apps.length);
            commit("setApp", app);
            commit("setLoading", true);
          })
          .catch(err => {
            console.log(err);
            commit("snackbar/setErr", err, { root: true });
          });
      })
    ).then(() => {
      commit("setLoading", false);
      commit("setAction", "");
    });
  },
  readApp({ commit }, Name) {
    const url = `/api/apps/${Name}`;
    commit("setLoading", true);
    return new Promise((resolve, reject) => {
      axios
        .get(url)
        .then(response => {
          const app = response.data;
          commit("setLoading", false);
          commit("setApp", app);
          resolve(app);
        })
        .catch(err => {
          commit("snackbar/setErr", err, { root: true });
          reject(err);
        });
    });
  },
  async readAppProcesses({ commit }, Name) {
    const url = `/api/apps/${Name}/processes`;
    let response = await axios.get(url);
    if (response) {
      const processes = response.data;
      commit("setAppProcesses", processes);
    }
  },
  async readAppLogs({ commit }, Name) {
    let url = `/api/apps/${Name}/logs`;
    axios
      .get(url)
      .then(response => {
        let logs = [];
        let _log = response.data.logs;
        let split_log = _log.split("\n");
        split_log.forEach(element => {
          logs.push(element);
        });
        commit("setAppLogs", logs);
      })
      .catch(err => {
        commit("snackbar/setErr", err, { root: true });
      });
  },
  AppUpdate({ commit }, Name) {
    commit("setLoading", true);
    commit("setAction", "Updating " + Name + " ...");
    const url = `/api/apps/${Name}/update`;
    axios
      .get(url)
      .then(response => {
        const app = response.data;
        commit("setApps", app);
      })
      .catch(err => {
        commit("snackbar/setErr", err, { root: true });
      })
      .finally(() => {
        commit("setUpdated", Name);
        commit("setLoading", false);
        commit("setAction", "");
      });
  },
  AppAction({ commit }, { Name, Action }) {
    commit("setLoading", true);
    commit("setAction", Action + " " + Name + " ...");
    const url = `/api/apps/actions/${Name}/${Action}`;
    axios
      .get(url)
      .then(response => {
        const app = response.data;
        commit("setApps", app);
      })
      .catch(err => {
        commit("snackbar/setErr", err, { root: true });
      })
      .finally(() => {
        if (Action == "update") {
          commit("setUpdated", Name);
        }
        commit("setLoading", false);
        commit("setAction", "");
      });
  }
};

const getters = {
  getAppByName(state) {
    return Name => {
      Name = "/" + Name;
      return state.apps.find(x => x.Name == Name);
    };
  }
};

export default {
  namespaced: true,
  state,
  mutations,
  getters,
  actions
};
