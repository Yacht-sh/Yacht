<template>
  <v-app id="yacht">
    <div v-if="isLoggedIn">
      <Sidebar v-if="$vuetify.breakpoint.mdAndUp" />
      <Bottombar v-if="$vuetify.breakpoint.smAndDown" />
      <Appbar />
      <v-main>
        <!-- Provides the application the proper gutter -->
        <v-container fluid>
          <!-- If using vue-router -->
          <transition
            name="slide"
            enter-active-class="animated slideInRight delay"
            leave-active-class="animated slideOutLeft"
          >
            <router-view></router-view>
          </transition>
        </v-container>
      </v-main>

      <!--
    <v-footer app>
       <span class="px-4">&copy; {{ new Date().getFullYear() }}</span>
    </v-footer>
  -->
    </div>
    <div v-else>
      <v-container fluid>
        <LoginForm />
      </v-container>
    </div>
    <snackbar />
  </v-app>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import Sidebar from "./components/nav/Sidebar";
import Appbar from "./components/nav/Appbar";
import Bottombar from "./components/nav/Bottombar";
import LoginForm from "./components/auth/LoginForm";
import snackbar from "./components/notifications/snackbar";
export default {
  name: "App",

  components: {
    Sidebar: Sidebar,
    Appbar: Appbar,
    Bottombar: Bottombar,
    LoginForm: LoginForm,
    snackbar: snackbar
  },
  data: () => ({}),
  computed: {
    ...mapGetters({
      isLoggedIn: "auth/isAuthenticated",
      authDisabled: "auth/authDisabled"
    }),
    theme() {
      return this.$vuetify.theme.dark ? "dark" : "light";
    }
  },
  methods: {
    ...mapActions({
      authCheck: "auth/AUTH_CHECK"
    })
  },
  created() {
    this.authCheck();
    const dark_theme = localStorage.getItem("dark_theme");
    const theme = JSON.parse(localStorage.getItem("theme"));

    if (dark_theme == "false") {
      this.$vuetify.theme.dark = false;
    } else if (dark_theme == "true") {
      this.$vuetify.theme.dark = true;
    }
    if (theme) {
      this.$vuetify.theme.themes = theme;
    }
  },
  mounted() {
    const dark_theme = localStorage.getItem("dark_theme");
    const theme = JSON.parse(localStorage.getItem("theme"));

    if (dark_theme == "false") {
      this.$vuetify.theme.dark = false;
    } else if (dark_theme == "true") {
      this.$vuetify.theme.dark = true;
    }
    if (theme) {
      this.$vuetify.theme.themes = theme;
    }
  }
};
</script>

<style>
.v-application {
  background-color: var(--v-background-base) !important;
}
html {
  background-color: var(--v-background-base) !important;
  overflow-y: auto;
}
.animated {
  --animate-duration: 0.3s;
}
.fast-anim {
  --animate-duration: 0.1s;
}
#yacht {
  display: flex;
  width: 100vw;
}
.page {
  position: relative;
  flex-grow: 1;
}
.component {
  position: absolute;
  min-width: 100%;
}
</style>
