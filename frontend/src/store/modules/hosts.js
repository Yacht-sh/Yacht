import axios from "axios";

const getStoredHostId = () => {
  const value = localStorage.getItem("yacht.selectedHostId");
  if (!value) {
    return null;
  }
  const parsed = parseInt(value, 10);
  return Number.isNaN(parsed) ? null : parsed;
};

const persistSelectedHostId = hostId => {
  if (hostId == null) {
    localStorage.removeItem("yacht.selectedHostId");
    return;
  }
  localStorage.setItem("yacht.selectedHostId", String(hostId));
};

const state = {
  hosts: [],
  agentMap: {},
  selectedHostId: getStoredHostId(),
  isLoading: false
};

const mutations = {
  setHosts(state, hosts) {
    state.hosts = hosts;
  },
  setAgentMap(state, agentMap) {
    state.agentMap = agentMap;
  },
  setSelectedHostId(state, hostId) {
    state.selectedHostId = hostId;
    persistSelectedHostId(hostId);
  },
  setLoading(state, isLoading) {
    state.isLoading = isLoading;
  }
};

const getters = {
  selectedHost(state) {
    return state.hosts.find(host => host.id === state.selectedHostId) || null;
  },
  activeHostLabel(state, getters) {
    return getters.selectedHost ? getters.selectedHost.name : "Local";
  },
  agentForHost: state => hostId => state.agentMap[hostId] || null
};

const actions = {
  async readHosts({ commit, state }) {
    commit("setLoading", true);
    try {
      const response = await axios.get("/api/hosts/");
      const hosts = response.data;
      commit("setHosts", hosts);
      if (!hosts.length) {
        commit("setSelectedHostId", null);
        commit("setAgentMap", {});
        return hosts;
      }
      const selectedExists = hosts.some(host => host.id === state.selectedHostId);
      if (!selectedExists) {
        const defaultHost = hosts.find(host => host.is_default) || hosts[0];
        commit("setSelectedHostId", defaultHost.id);
      }
      const agentIds = hosts.filter(host => host.connection_type === "agent").map(host => host.id);
      const agentMap = {};
      await Promise.all(
        agentIds.map(async hostId => {
          try {
            const { data } = await axios.get(`/api/hosts/${hostId}/agent`);
            agentMap[hostId] = data.agent || null;
          } catch {
            agentMap[hostId] = null;
          }
        })
      );
      commit("setAgentMap", agentMap);
      return hosts;
    } catch (err) {
      commit("snackbar/setErr", err, { root: true });
      throw err;
    } finally {
      commit("setLoading", false);
    }
  },
  async createHost({ dispatch, commit }, payload) {
    commit("setLoading", true);
    try {
      await axios.post("/api/hosts/", payload);
      await dispatch("readHosts");
    } catch (err) {
      commit("snackbar/setErr", err, { root: true });
      throw err;
    } finally {
      commit("setLoading", false);
    }
  },
  selectHost({ commit }, hostId) {
    commit("setSelectedHostId", hostId);
  },
  async readAgent({ commit, state }, hostId) {
    try {
      const { data } = await axios.get(`/api/hosts/${hostId}/agent`);
      const agentMap = { ...state.agentMap, [hostId]: data.agent || null };
      commit("setAgentMap", agentMap);
      return data.agent || null;
    } catch (err) {
      commit("snackbar/setErr", err, { root: true });
      throw err;
    }
  },
  async queueComposeAction({ commit, state }, { hostId, project, action, workingDir }) {
    const payload = { host_id: hostId, project, action };
    if (workingDir) {
      payload.working_dir = workingDir;
    }
    const response = await axios.post("/api/agents/compose-action", payload);
    return response.data;
  }
};

export default {
  namespaced: true,
  state,
  mutations,
  getters,
  actions
};
