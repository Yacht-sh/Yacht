import axios from "axios";
import router from "@/router/index";

const state = {
  volumes: [],
  isLoading: false
};

const mutations = {
  setVolumes(state, volumes) {
    state.volumes = volumes;
  },
  setVolume(state, volume) {
    const idx = state.volumes.findIndex(x => x.Name === volume.Name);
    if (idx < 0) {
      state.volumes.push(volume);
    } else {
      state.volumes.splice(idx, 1, volume);
    }
  },
  addVolume(state, volume) {
    state.volumes.push(volume);
  },
  removeVolume(state, volume) {
    const idx = state.volumes.findIndex(x => x.Name === volume.Name);
    if (idx < 0) {
      return;
    }
    state.volumes.splice(idx, 1);
  },
  setLoading(state, loading) {
    state.isLoading = loading;
  }
};

const actions = {
  _readVolumes({ commit }) {
    const url = "/api/resources/volumes/";
    commit("setLoading", true);
    return new Promise((resolve, reject) => {
      axios
        .get(url)
        .then(response => {
          const volumes = response.data;
          commit("setLoading", false);
          commit("setVolumes", volumes);
          resolve(volumes);
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
  readVolumes({ commit }) {
    commit("setLoading", true);
    const url = "/api/resources/volumes/";
    axios
      .get(url)
      .then(response => {
        const volumes = response.data;
        commit("setVolumes", volumes);
      })
      .catch(err => {
        commit("snackbar/setErr", err, { root: true });
      })
      .finally(() => {
        commit("setLoading", false);
      });
  },
  readVolume({ commit }, id) {
    commit("setLoading", true);
    const url = `/api/resources/volumes/${id}`;
    axios
      .get(url)
      .then(response => {
        const volume = response.data;
        commit("setVolume", volume);
      })
      .catch(err => {
        commit("snackbar/setErr", err, { root: true });
      })
      .finally(() => {
        commit("setLoading", false);
      });
  },
  writeVolume({ commit }, payload) {
    commit("setLoading", true);
    const url = "/api/resources/volumes/";
    axios
      .post(url, payload)
      .then(response => {
        const volumes = response.data;
        commit("setVolumes", volumes);
      })
      .catch(err => {
        commit("snackbar/setErr", err, { root: true });
      })
      .finally(() => {
        commit("setLoading", false);
        router.push({ name: "Volumes" });
      });
  },
  updateVolume({ commit }, id) {
    commit("setLoading", true);
    const url = `/api/resources/volumes/${id}/pull`;
    axios
      .get(url)
      .then(response => {
        const volume = response.data;
        commit("setVolume", volume);
      })
      .catch(err => {
        commit("snackbar/setErr", err, { root: true });
      })
      .finally(() => {
        commit("setLoading", false);
      });
  },
  deleteVolume({ commit }, id) {
    commit("setLoading", true);
    const url = `/api/resources/volumes/${id}`;
    axios
      .delete(url)
      .then(response => {
        const volume = response.data;
        commit("removeVolume", volume);
      })
      .catch(err => {
        commit("snackbar/setErr", err, { root: true });
      })
      .finally(() => {
        commit("setLoading", false);
      });
  }
};

const getters = {
  getVolumeByName(state) {
    return Name => {
      return state.volumes.find(x => x.Name == Name);
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
