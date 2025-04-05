import axios from "axios";
import router from "@/router/index";

const state = {
  networks: [],
  isLoading: false
};

const mutations = {
  setNetworks(state, networks) {
    state.networks = networks;
  },
  setNetwork(state, network) {
    const idx = state.networks.findIndex(x => x.Id === network.Id);
    if (idx < 0) {
      state.networks.push(network);
    } else {
      state.networks.splice(idx, 1, network);
    }
  },
  addNetwork(state, network) {
    state.networks.push(network);
  },
  removeNetwork(state, network) {
    const idx = state.networks.findIndex(x => x.Id === network.Id);
    if (idx < 0) {
      return;
    }
    state.networks.splice(idx, 1);
  },
  setLoading(state, loading) {
    state.isLoading = loading;
  }
};

const actions = {
  _readNetworks({ commit }) {
    const url = "/api/resources/networks/";
    commit("setLoading", true);
    return new Promise((resolve, reject) => {
      axios
        .get(url)
        .then(response => {
          const networks = response.data;
          commit("setLoading", false);
          commit("setNetworks", networks);
          resolve(networks);
        })
        .finally(() => {
          commit("setLoading", false);
        })
        .catch(error => {
          commit("snackbar/setErr", error, { root: true });
          reject(error);
        });
    });
  },
  readNetworks({ commit }) {
    commit("setLoading", true);
    const url = "/api/resources/networks/";
    axios
      .get(url)
      .then(response => {
        console.log(response);
        const networks = response.data;
        commit("setNetworks", networks);
      })
      .catch(err => {
        commit("snackbar/setErr", err, { root: true });
      })
      .finally(() => {
        commit("setLoading", false);
      });
  },
  readNetwork({ commit }, id) {
    commit("setLoading", true);
    const url = `/api/resources/networks/${id}`;
    axios
      .get(url)
      .then(response => {
        const network = response.data;
        commit("setNetwork", network);
      })
      .catch(err => {
        commit("snackbar/setErr", err, { root: true });
      })
      .finally(() => {
        commit("setLoading", false);
      });
  },
  writeNetwork({ commit }, payload) {
    commit("setLoading", true);
    const url = "/api/resources/networks/";
    axios
      .post(url, payload)
      .then(response => {
        const networks = response.data;
        commit("setNetworks", networks);
      })
      .catch(err => {
        commit("snackbar/setErr", err, { root: true });
      })
      .finally(() => {
        commit("setLoading", false);
        router.push({ name: "Networks" });
      });
  },
  //   updateNetwork({ commit }, id) {
  //     commit("setLoading", true);
  //     const url = `/api/resources/networks/${id}/pull`;
  //     axios
  //       .get(url)
  //       .then(response => {
  //         const network = response.data;
  //         commit("setNetwork", network);
  //       })
  //       .catch(err => {
  //         commit("snackbar/setErr", err, { root: true });
  //       })
  //       .finally(() => {
  //         commit("setLoading", false);
  //       });
  //   },
  deleteNetwork({ commit }, id) {
    commit("setLoading", true);
    const url = `/api/resources/networks/${id}`;
    axios
      .delete(url)
      .then(response => {
        const network = response.data;
        commit("removeNetwork", network);
        commit("setLoading", false);
      })
      .catch(err => {
        commit("snackbar/setErr", err, { root: true });
        commit("setLoading", false);
      });
  }
};

const getters = {
  getNetworkById(state) {
    return Id => {
      return state.networks.find(x => x.Id == Id);
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
