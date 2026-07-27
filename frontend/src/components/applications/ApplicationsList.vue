<template>
  <v-card color="foreground">
    <v-card-title class="primary font-weight-bold">
      Applications
      <v-spacer />
      <v-btn to="/apps/deploy" icon small color="accent">
        <v-icon small>mdi-plus</v-icon>
      </v-btn>
      <v-btn icon small color="primary" @click="refresh">
        <v-icon small>mdi-refresh</v-icon>
      </v-btn>
    </v-card-title>
    <v-data-table
      :headers="headers"
      :items="apps"
      :loading="isLoading"
      :search="search"
      class="elevation-0"
      item-key="Name"
      loading-text="Loading Applications..."
      no-data-text="No applications found."
      no-results-text="No matching applications."
    >
      <template v-slot:item.Name="{ item }">
        <span class="primary--text" style="cursor: pointer" @click="openApp(item)">
          {{ item.Name }}
        </span>
      </template>
      <template v-slot:item.State.Status="{ item }">
        <v-chip x-small :color="chipColor(item.State.Status)">
          {{ readableStatus(item.State.Status) }}
        </v-chip>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-menu open-on-hover offset-y>
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon small v-on="on" v-bind="attrs">
              <v-icon small>mdi-dots-vertical</v-icon>
            </v-btn>
          </template>
          <v-list dense>
            <v-list-item @click="appAction(item, 'start')">
              <v-list-item-icon><v-icon small>mdi-play</v-icon></v-list-item-icon>
              <v-list-item-title>Start</v-list-item-title>
            </v-list-item>
            <v-list-item @click="appAction(item, 'stop')">
              <v-list-item-icon><v-icon small>mdi-stop</v-icon></v-list-item-icon>
              <v-list-item-title>Stop</v-list-item-title>
            </v-list-item>
            <v-list-item @click="appAction(item, 'restart')">
              <v-list-item-icon><v-icon small>mdi-refresh</v-icon></v-list-item-icon>
              <v-list-item-title>Restart</v-list-item-title>
            </v-list-item>
            <v-list-item @click="appAction(item, 'remove')">
              <v-list-item-icon><v-icon small>mdi-delete</v-icon></v-list-item-icon>
              <v-list-item-title>Remove</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import { mapActions, mapState } from "vuex";

export default {
  name: "ApplicationsList",
  data() {
    return {
      search: "",
      headers: [
        { text: "Name", value: "Name" },
        { text: "Image", value: "Config.Image", sortable: true },
        { text: "Status", value: "State.Status", sortable: true },
        { text: "Actions", value: "actions", sortable: false, align: "right" }
      ]
    };
  },
  computed: {
    ...mapState("apps", ["apps", "isLoading"]),
    ...mapState("hosts", ["selectedHostId"])
  },
  methods: {
    ...mapActions({
      readApps: "apps/readApps",
      AppAction: "apps/AppAction"
    }),
    refresh() {
      this.readApps();
    },
    openApp(app) {
      const name = typeof app.Name === "string" ? app.Name.replace(/^\//, "") : "";
      this.$router.push(`/apps/${name}/info`);
    },
    readableStatus(status) {
      return String(status || "").replace(/_/g, " ");
    },
    chipColor(status) {
      const state = String(status || "").toLowerCase();
      if (["running"].includes(state)) return "success";
      if (["exited", "dead", "paused"].includes(state)) return "error";
      return "secondary";
    },
    async appAction(app, action) {
      const name = typeof app.Name === "string" ? app.Name.replace(/^\//, "") : "";
      if (!name) {
        return;
      }
      await this.AppAction({ Name: name, Action: action });
      await this.readApps();
    }
  },
  async created() {
    await this.readApps();
  },
  watch: {
    async selectedHostId() {
      await this.readApps();
    }
  }
};
</script>

<style scoped></style>
