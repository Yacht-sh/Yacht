import axios from "axios";
import router from "@/router/index";

const resourceUrl = (path = "", hostId = null) => {
  const search = new URLSearchParams();
  if (hostId != null) {
    search.set("host_id", hostId);
  }
  const query = search.toString();
  return `/api/resources/volumes/${path}${query ? `?${query}` : ""}`;
};

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
  _readVolumes({ commit, rootState }) {
    const url = resourceUrl("", rootState.hosts.selectedHostId);
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
  readVolumes({ commit, rootState }) {
    commit("setLoading", true);
    const url = resourceUrl("", rootState.hosts.selectedHostId);
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
  readVolume({ commit, rootState }, id) {
    commit("setLoading", true);
    const url = resourceUrl(id, rootState.hosts.selectedHostId);
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
  writeVolume({ commit, rootState }, payload) {
    commit("setLoading", true);
    const url = resourceUrl("", rootState.hosts.selectedHostId);
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
  updateVolume({ commit, rootState }, id) {
    commit("setLoading", true);
    const url = resourceUrl(`${id}/pull`, rootState.hosts.selectedHostId);
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
  deleteVolume({ commit, rootState }, id) {
    commit("setLoading", true);
    const url = resourceUrl(id, rootState.hosts.selectedHostId);
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
