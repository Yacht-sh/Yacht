<template>
  <v-card color="foreground">
    <v-card-title class="primary font-weight-bold">
      Containers
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
      :items="containers"
      :loading="isLoading"
      :search="search"
      class="elevation-0"
      item-key="Name"
      loading-text="Loading containers..."
      no-data-text="No containers found."
      no-results-text="No matching containers."
    >
      <template v-slot:item.Name="{ item }">
        <span class="primary--text" style="cursor: pointer" @click="openContainer(item)">
          {{ displayName(item) }}
        </span>
      </template>
      <template v-slot:item.Config.Image="{ item }">
        {{ tagFor(item) }}
      </template>
      <template v-slot:item.State.Status="{ item }">
        <v-chip x-small :color="chipColor(item.State.Status)">
          {{ readableState(item.State.Status) }}
        </v-chip>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-icon small class="mr-2" @click="containerAction(item, 'start')" title="Start">mdi-play</v-icon>
        <v-icon small class="mr-2" @click="containerAction(item, 'stop')" title="Stop">mdi-stop</v-icon>
        <v-icon small class="mr-2" @click="containerAction(item, 'restart')" title="Restart">mdi-refresh</v-icon>
        <v-icon small @click="containerAction(item, 'remove')" title="Remove">mdi-delete</v-icon>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import { mapActions, mapState } from "vuex";

export default {
  name: "ContainerList",
  data() {
    return {
      search: "",
      headers: [
        { text: "Name", value: "Name", sortable: true },
        { text: "Image", value: "Config.Image", sortable: true },
        { text: "Status", value: "State.Status", sortable: true },
        { text: "Actions", value: "actions", sortable: false, align: "right" }
      ]
    };
  },
  computed: {
    ...mapState("apps", ["apps", "isLoading"]),
    ...mapState("hosts", ["selectedHostId"]),
    containers() {
      return this.apps || [];
    }
  },
  methods: {
    ...mapActions({
      readApps: "apps/readApps",
      AppAction: "apps/AppAction"
    }),
    refresh() {
      this.readApps();
    },
    openContainer(item) {
      const name = this.containerName(item);
      this.$router.push(`/apps/${name}/info`);
    },
    containerName(item) {
      const raw = item && item.Name;
      if (typeof raw !== "string") return "";
      const trimmed = raw.replace(/^\//, "");
      return trimmed.split("/").pop() || trimmed;
    },
    displayName(item) {
      return this.containerName(item);
    },
    readableState(status) {
      return String(status || "").replace(/_/g, " ");
    },
    tagFor(item) {
      const image = item && item.Config && item.Config.Image;
      if (!image) {
        return item && item.Image ? String(item.Image).split("/").pop() : "";
      }
      return String(image).split("/").pop();
    },
    chipColor(status) {
      const state = String(status || "").toLowerCase();
      if (["running"].includes(state)) return "success";
      if (["exited", "dead", "paused", "created"].includes(state)) return "error";
      return "secondary";
    },
    async containerAction(item, action) {
      const name = this.containerName(item);
      if (!name) return;
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

<style scoped>
.primary--text {
  text-decoration: none;
}
</style>