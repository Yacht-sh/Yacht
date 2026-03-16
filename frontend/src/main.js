// Setup Vue
import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import VueChatScroll from "vue-chat-scroll";
// API Calls
import axios from "axios";
// UI Framework
import vuetify from "./plugins/vuetify";
// Form Validation
import VueUtils from "./plugins/vueutils";
import "./vee-validate";
// Animations
require("animate.css/animate.compat.css");

Vue.use(VueChatScroll);

Vue.config.productionTip = false;

// Handle Token Refresh on 401
function createAxiosResponseInterceptor() {
  const interceptor = axios.interceptors.response.use(
    response => response,
    error => {
      if (!error.response) {
        return Promise.reject(error);
      }

      if (error.response.status !== 401) {
        return Promise.reject(error);
      }

      axios.interceptors.response.eject(interceptor);

      return store
        .dispatch("auth/AUTH_REFRESH")
        .then(() => {
          error.response.config.xsrfCookieName = "csrf_access_token";
          error.response.config.xsrfHeaderName = "X-CSRF-TOKEN";
          error.response.config.withCredentials = true;
          return axios(error.response.config);
        })
        .catch(refreshError => {
          if (!refreshError.response || refreshError.response.status !== 401) {
            return Promise.reject(refreshError);
          } else {
            store.dispatch("auth/AUTH_LOGOUT");
            router.push("/");
            return Promise.reject(refreshError);
          }
        })
        .finally(() => {
          createAxiosResponseInterceptor();
        });
    }
  );
}

// Call interceptor
createAxiosResponseInterceptor();
Vue.use(VueUtils);
new Vue({
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount("#app");
