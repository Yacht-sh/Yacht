import axios from "axios";
import router from "@/router/index";

const state = {
  projects: [],
  isLoading: false,
  action: ""
};

const mutations = {
  setProjects(state, projects) {
    state.projects = projects;
  },
  setProject(state, project) {
    const idx = state.projects.findIndex(x => x.name === project.name);
    if (idx < 0) {
      state.projects.push(project);
    } else {
      state.projects.splice(idx, 1, project);
    }
  },
  addProject(state, project) {
    state.projects.push(project);
  },
  removeProject(state, project) {
    const idx = state.projects.findIndex(x => x.name === project.name);
    if (idx < 0) {
      return;
    }
    state.projects.splice(idx, 1);
  },
  setLoading(state, loading) {
    state.isLoading = loading;
  },
  setAction(state, action) {
    state.action = action;
  }
};

const actions = {
  _readProjects({ commit }) {
    const url = "/api/compose/";
    commit("setLoading", true);
    return new Promise((resolve, reject) => {
      axios
        .get(url)
        .then(response => {
          const projects = response.data;
          commit("setLoading", false);
          commit("setProjects", projects);
          resolve(projects);
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
  readProjects({ commit }) {
    commit("setLoading", true);
    const url = "/api/compose/";
    axios
      .get(url)
      .then(response => {
        const projects = response.data;
        commit("setProjects", projects);
      })
      .catch(err => {
        commit("snackbar/setErr", err, { root: true });
      })
      .finally(() => {
        commit("setLoading", false);
      });
  },
  readProject({ commit }, Name) {
    const url = `/api/compose/${Name}`;
    commit("setLoading", true);
    return new Promise((resolve, reject) => {
      axios
        .get(url)
        .then(response => {
          const project = response.data;
          commit("setLoading", false);
          commit("setProject", project);
          resolve(project);
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
  writeProject({ commit }, payload) {
    commit("setLoading", true);
    const url = "/api/compose/";
    axios
      .post(url, payload)
      .then(response => {
        const projects = response.data;
        commit("setProjects", projects);
      })
      .catch(err => {
        commit("snackbar/setErr", err, { root: true });
      })
      .finally(() => {
        commit("setLoading", false);
        router.push({ name: "Projects" });
      });
  },
  ProjectAction({ commit, dispatch }, { Name, Action }) {
    commit("setLoading", true);
    commit("setAction", Action);
    const url = `/api/compose/${Name}/actions/${Action}`;
    axios
      .get(url)
      .then(response => {
        const projects = response.data;
        commit("setProjects", projects);
        dispatch("apps/readApps", null, { root: true });
        commit("snackbar/setMessage", `${Name} has been ${Action}ed.`, {
          root: true
        });
      })
      .catch(err => {
        console.log(err);
        commit("snackbar/setErr", err, { root: true });
      })
      .finally(() => {
        commit("setLoading", false);
        commit("setAction", "");
      });
  },
  ProjectAppAction({ commit, dispatch }, { Project, Name, Action }) {
    commit("setLoading", true);
    commit("setAction", Action);
    const url = `/api/compose/${Project}/actions/${Action}/${Name}`;
    axios
      .get(url)
      .then(response => {
        const projects = response.data;
        commit("setProjects", projects);
        dispatch("apps/readApps", null, { root: true });
        commit("snackbar/setMessage", `${Name} has been ${Action}ed.`, {
          root: true
        });
      })
      .catch(err => {
        commit("snackbar/setErr", err, { root: true });
      })
      .finally(() => {
        commit("setLoading", false);
        commit("setAction", "");
      });
  }
};

const getters = {
  getProjectByName(state) {
    return name => {
      return state.projects.find(x => x.name == name);
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
