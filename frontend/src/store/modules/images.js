import axios from "axios";
import router from "@/router/index";

const resourceUrl = (path = "", hostId = null) => {
  const search = new URLSearchParams();
  if (hostId != null) {
    search.set("host_id", hostId);
  }
  const query = search.toString();
  return `/api/resources/images/${path}${query ? `?${query}` : ""}`;
};

const state = {
  images: [],
  isLoading: false
};

const mutations = {
  setImages(state, images) {
    state.images = images;
  },
  setImage(state, image) {
    const idx = state.images.findIndex(x => x.Id === image.Id);
    if (idx < 0) {
      state.images.push(image);
    } else {
      state.images.splice(idx, 1, image);
    }
  },
  addImage(state, image) {
    state.images.push(image);
  },
  removeImage(state, image) {
    const idx = state.images.findIndex(x => x.Id === image.Id);
    if (idx < 0) {
      return;
    }
    state.images.splice(idx, 1);
  },
  setLoading(state, loading) {
    state.isLoading = loading;
  }
};

const actions = {
  readImages({ commit, rootState }) {
    commit("setLoading", true);
    const url = resourceUrl("", rootState.hosts.selectedHostId);
    axios
      .get(url)
      .then(response => {
        const images = response.data;
        commit("setImages", images);
      })
      .catch(err => {
        commit("snackbar/setErr", err, { root: true });
      })
      .finally(() => {
        commit("setLoading", false);
      });
  },
  readImage({ commit, rootState }, id) {
    commit("setLoading", true);
    const url = resourceUrl(id, rootState.hosts.selectedHostId);
    axios
      .get(url)
      .then(response => {
        const image = response.data;
        commit("setImage", image);
      })
      .catch(err => {
        commit("snackbar/setErr", err, { root: true });
      })
      .finally(() => {
        commit("setLoading", false);
      });
  },
  writeImage({ commit, rootState }, payload) {
    commit("setLoading", true);
    const url = resourceUrl("", rootState.hosts.selectedHostId);
    axios
      .post(url, payload)
      .then(response => {
        const images = response.data;
        commit("setImages", images);
      })
      .catch(err => {
        commit("snackbar/setErr", err, { root: true });
      })
      .finally(() => {
        commit("setLoading", false);
        router.push({ name: "Images" });
      });
  },
  updateImage({ commit, dispatch, rootState }, id) {
    commit("setLoading", true);
    const url = resourceUrl(`${id}/pull`, rootState.hosts.selectedHostId);
    axios
      .get(url)
      .then(response => {
        const image = response.data;
        commit("setImage", image);
        dispatch("readImages");
      })
      .catch(err => {
        commit("snackbar/setErr", err, { root: true });
      })
      .finally(() => {
        commit("setLoading", false);
      });
  },
  deleteImage({ commit, rootState }, id) {
    commit("setLoading", true);
    const url = resourceUrl(id, rootState.hosts.selectedHostId);
    axios
      .delete(url)
      .then(response => {
        const image = response.data;
        commit("removeImage", image);
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
  getImageById(state) {
    return Id => {
      return state.images.find(x => x.Id == Id);
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
