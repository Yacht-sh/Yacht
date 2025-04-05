import {
  AUTH_REQUEST,
  AUTH_ERROR,
  AUTH_SUCCESS,
  AUTH_LOGOUT,
  AUTH_REFRESH,
  AUTH_CLEAR,
  AUTH_CHANGE_PASS,
  AUTH_CHECK,
  AUTH_DISABLED,
  AUTH_ENABLED
} from "../actions/auth";
import axios from "axios";
import router from "@/router/index";

const state = {
  status: "",
  username: localStorage.getItem("username") || "",
  authDisabled: null
};

const getters = {
  isAuthenticated: state => !!state.username,
  authStatus: state => state.status,
  getUsername: state => state.username
};

const actions = {
  [AUTH_REQUEST]: ({ commit }, credentials) => {
    return new Promise((resolve, reject) => {
      commit(AUTH_REQUEST);
      const url = "/api/auth/login";
      axios
        .post(url, credentials, { withCredentials: true })
        .then(resp => {
          localStorage.setItem("username", resp.data.username);
          axios.defaults.withCredentials = true;
          axios.defaults.xsrfCookieName = "csrf_access_token";
          axios.defaults.xsrfHeaderName = "X-CSRF-TOKEN";
          commit(AUTH_SUCCESS, resp);
          resolve(resp);
        })
        .catch(err => {
          commit(AUTH_ERROR, err);
          commit("snackbar/setErr", err, { root: true });
          localStorage.removeItem("username");
          reject(err);
        });
    });
  },

  [AUTH_LOGOUT]: ({ commit }) => {
    return new Promise(resolve => {
      commit(AUTH_REQUEST);
      const url = "/api/auth/logout";
      axios
        .get(url, {}, { withCredentials: true })
        .then(resp => {
          let rurl = "/api/auth/logout/refresh";
          axios
            .get(
              rurl,
              {},
              {
                xsrfCookieName: "csrf_refresh_token",
                xsrfHeaderName: "X-CSRF-TOKEN",
                withCredentials: true
              }
            )
            .then(resp => {
              commit(AUTH_CLEAR, resp);
              localStorage.removeItem("username");
              router.push({ path: "/" });
              resolve(resp);
            });

          resolve(resp);
        })
        .catch(error => {
          console.log(error);
          commit(AUTH_CLEAR);
        });
    });
  },
  [AUTH_REFRESH]: ({ commit }) => {
    return new Promise(resolve => {
      commit(AUTH_REQUEST);
      const url = "/api/auth/refresh";
      axios
        .post(
          url,
          {},
          {
            xsrfCookieName: "csrf_refresh_token",
            xsrfHeaderName: "X-CSRF-TOKEN",
            withCredentials: true
          }
        )
        .then(resp => {
          resolve(resp);
        })
        .catch(error => {
          console.log(error);
          commit(AUTH_CLEAR);
        });
    });
  },
  [AUTH_CHANGE_PASS]: ({ commit }, credentials) => {
    return new Promise((resolve, reject) => {
      commit(AUTH_REQUEST);
      const url = "/api/auth/me";
      axios
        .post(url, credentials)
        .then(resp => {
          localStorage.setItem("username", resp.data.username);
          commit(AUTH_SUCCESS, resp);
          resolve(resp);
        })
        .finally(() => {
          router.push({ path: `/user/info` });
        })
        .catch(err => {
          reject(err);
        });
    });
  },
  [AUTH_CHECK]: ({ commit }) => {
    commit(AUTH_REQUEST);
    const url = "/api/auth/me";
    axios
      .get(url)
      .then(resp => {
        if (resp.data.authDisabled == true) {
          localStorage.setItem("username", resp.data.username);
          commit(AUTH_DISABLED);
          commit(AUTH_SUCCESS, resp);
        } else {
          commit(AUTH_ENABLED);
        }
      })
      .catch(() => {
        commit(AUTH_ENABLED);
      });
  }
};

const mutations = {
  [AUTH_REQUEST]: state => {
    state.status = "loading";
  },
  [AUTH_SUCCESS]: (state, resp) => {
    state.status = "success";
    state.username = resp.data.username;
    if (resp.data.authDisabled) {
      state.authDisabled = true;
    }
  },
  [AUTH_ERROR]: state => {
    state.status = "error";
  },
  [AUTH_DISABLED]: state => {
    state.authDisabled = true;
  },
  [AUTH_ENABLED]: state => {
    state.authDisabled = false;
  },
  [AUTH_CLEAR]: state => {
    state.accessToken = "";
    state.refreshToken = "";
    state.username = "";
  }
};

export default {
  namespaced: true,
  state,
  mutations,
  getters,
  actions
};
