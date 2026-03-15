<template>
  <v-app-bar app clipped-left color="secondary">
    <img :src="themeLogo()" class="main-logo" />
    <v-toolbar-title class="ml-2">Yacht</v-toolbar-title>
    <v-toolbar-title class="mx-auto font-weight-bold hidden-sm-and-down">
      {{ $route.name }}
    </v-toolbar-title>
    <v-select
      v-if="hosts.length"
      v-model="selectedHostValue"
      :items="hosts"
      item-text="name"
      item-value="id"
      dense
      hide-details
      flat
      solo
      background-color="primary"
      class="mx-4 hidden-sm-and-down host-select"
      label="Host"
    />
    <v-spacer class="hidden-md-and-up" />
    <v-menu bottom offset-y v-if="!authDisabled">
      <template v-slot:activator="{ on, attrs }">
        <v-btn color="primary" v-bind="attrs" v-on="on" class="pr-2">
          {{ username }}
          <v-icon> mdi-chevron-down </v-icon>
        </v-btn>
      </template>
      <v-list color="foreground">
        <v-list-item :to="{ path: `/user/info` }">
          <v-list-item-icon>
            <v-icon>mdi-account-settings-outline</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            User
          </v-list-item-content>
        </v-list-item>
        <v-list-item @click="logout()">
          <v-list-item-icon>
            <v-icon>mdi-logout-variant</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            Logout
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-menu>
  </v-app-bar>
</template>

<script>
import { mapActions, mapState } from "vuex";
import lightLogo from "@/assets/logo-light.svg";
import darkLogo from "@/assets/logo.svg";
import { themeLogo } from "../../config.js";
export default {
  methods: {
    ...mapActions({
      logout: "auth/AUTH_LOGOUT",
      readHosts: "hosts/readHosts",
      selectHost: "hosts/selectHost",
      readImages: "images/readImages",
      readImage: "images/readImage",
      readVolumes: "volumes/readVolumes",
      readVolume: "volumes/readVolume",
      readNetworks: "networks/readNetworks",
      readNetwork: "networks/readNetwork",
      readProjects: "projects/readProjects",
      readProject: "projects/readProject"
    }),
    themeLogo() {
      if (themeLogo) {
        return themeLogo;
      } else if (this.$vuetify.theme.dark == true) {
        return darkLogo;
      } else if (this.$vuetify.theme.dark == false) {
        return lightLogo;
      }
    },
    async handleHostChange(value) {
      this.selectHost(value);
      if (this.$route.name === "Images") {
        await this.readImages();
      } else if (this.$route.name === "Image Details") {
        await this.readImage(this.$route.params.imageid);
      } else if (this.$route.name === "Volumes") {
        await this.readVolumes();
      } else if (this.$route.name === "Volume Details") {
        await this.readVolume(this.$route.params.volumeName);
      } else if (this.$route.name === "Networks") {
        await this.readNetworks();
      } else if (this.$route.name === "Network Details") {
        await this.readNetwork(this.$route.params.networkid);
      } else if (this.$route.name === "View Projects") {
        await this.readProjects();
      } else if (this.$route.name === "Project Details") {
        await this.readProject(this.$route.params.projectName);
      }
    }
  },
  computed: {
    ...mapState("auth", ["username", "authDisabled"]),
    ...mapState("hosts", ["hosts", "selectedHostId"]),
    selectedHostValue: {
      get() {
        return this.selectedHostId;
      },
      set(value) {
        this.handleHostChange(value);
      }
    }
  },
  created() {
    this.readHosts().catch(() => {});
  }
};
</script>

<style scoped>
.main-logo {
  max-width: 47px;
  max-height: 32px;
}
.host-select {
  max-width: 220px;
}
</style>
