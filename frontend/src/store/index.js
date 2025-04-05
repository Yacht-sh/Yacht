import Vue from "vue";
import Vuex from "vuex";
import auth from "./modules/auth";
import templates from "./modules/templates.js";
import apps from "./modules/apps.js";
import snackbar from "./modules/snackbar.js";
import images from "./modules/images.js";
import volumes from "./modules/volumes.js";
import networks from "./modules/networks.js";
import projects from "./modules/projects.js";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    // templates: [],
    // itemCount: 10
  },
  mutations: {
    // setTemplates(state, templates) {
    //   state.templates = templates;
    //   console.log(templates);
    //   console.log(state.templates);
    // }
  },
  actions: {
    // readTemplates({ commit }) {
    //   const url = "/api/templates/";
    //   axios
    //     .get(url)
    //     .then(response => {
    //       let templates = response.data.data;
    //       console.log(templates);
    //       commit("setTemplates", templates);
    //     });
    // }
  },
  getters: {
    // getTemplates(state) {
    //   return state.templates;
    // }
  },
  modules: {
    templates,
    apps,
    images,
    volumes,
    networks,
    projects,
    auth,
    snackbar
  }
});
