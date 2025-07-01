<template>
  <v-card color="foreground">
    <v-card-title class="primary font-weight-bold">
      Dashboard <v-icon v-on:click="refresh()">mdi-refresh</v-icon>
    </v-card-title>
    <v-card-text class="secondary text-center px-5 py-5">
      <v-row dense class="mt-3">
        <v-col
          v-for="app in sortByTitle(stats)"
          :key="app.name"
          cols="12"
          xl="2"
          lg="2"
          md="3"
          sm="3"
          class="d-flex"
          style="flex-direction: column"
        >
          <v-card color="foreground" class="flex-grow-1">
            <v-card-title class="pb-0">
              <v-tooltip top transition="scale-transition">
                <template v-slot:activator="{ on, attrs }">
                  <span
                    v-bind="attrs"
                    v-on="on"
                    @click="handleAppClick(app.name)"
                    class="AppTitle"
                    >{{ app.name }}</span
                  >
                </template>
                <span>{{ app.name }}</span>
              </v-tooltip>
            </v-card-title>
            <v-tooltip bottom transition="scale-transition">
              <template v-slot:activator="{ on, attrs }">
                <v-card-text
                  v-bind="attrs"
                  v-on="on"
                  class="text-left pt-0 AppTitle"
                >
                  CPU Usage:
                  <v-progress-linear :value="app.cpu_percent" color="primary" />
                  {{ app.cpu_percent }}%
                  <br />
                  MEM Usage:
                  <v-progress-linear :value="app.mem_percent" color="blue" />
                  {{ app.mem_percent }}%, {{ app.mem_current }} /
                  {{ app.mem_total }}
                </v-card-text>
              </template>
              <span
                >CPU Usage: {{ app.cpu_percent }}%
                <br />
                MEM Usage: {{ app.mem_percent }}%, {{ app.mem_current }}/{{
                  app.mem_total
                }}
              </span>
            </v-tooltip>
          </v-card>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
import { mapActions, mapState } from "vuex";
export default {
  data() {
    return {
      stats: {},
      statConnection: {}
    };
  },
  methods: {
    ...mapActions({
      readApps: "apps/readApps"
    }),
    formatBytes(bytes, decimals = 2) {
      if (bytes === 0) return "0 Bytes";

      const k = 1024;
      const dm = decimals < 0 ? 0 : decimals;
      const sizes = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];

      const i = Math.floor(Math.log(bytes) / Math.log(k));

      return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
    },
    readAppStats() {
      this.statConnection = new EventSource(`/api/apps/stats`);
      this.statConnection.addEventListener("update", event => {
        let statsGroup = JSON.parse(event.data);
        if (!(statsGroup.name in this.stats)) {
          this.stats[statsGroup.name] = {};
          this.stats[statsGroup.name].name = statsGroup.name;
        }
        this.stats[statsGroup.name].cpu_percent = Math.round(
          statsGroup.cpu_percent
        );
        this.stats[statsGroup.name].mem_percent = Math.round(
          statsGroup.mem_percent
        );
        this.stats[statsGroup.name].mem_current = this.formatBytes(
          statsGroup.mem_current,
          2
        );
        this.stats[statsGroup.name].mem_total = this.formatBytes(
          statsGroup.mem_total,
          2
        );
        this.$forceUpdate();
      });
    },
    refresh() {
      this.closeStats();
      this.readApps();
      for (var app in this.apps) {
        this.readAppStats(this.apps[app].name);
      }
    },
    sortByTitle(arr) {
      let sorted = Object.keys(arr)
        .sort()
        .reduce(
          (acc, key) => ({
            ...acc,
            [key]: arr[key]
          }),
          {}
        );
      return sorted;
    },
    handleAppClick(appName) {
      this.$router.push({ path: `/apps/${appName}/info` });
    },
    closeStats() {
      this.statConnection.close();
      this.stats = {};
    },
    fillStats(app) {
      let datacollection = {
        labels: ["Resource Usage"],
        datasets: [
          {
            label: "CPU Usage",
            backgroundColor: "#41b883",
            data: app.cpu_percent
          },
          {
            label: "Mem Usage",
            backgroundColor: "#008bcf",
            data: app.mem_percent
          }
        ]
      };
      return datacollection;
    }
  },
  computed: {
    ...mapState("apps", ["apps"])
  },
  async created() {
    await this.readApps();
    for (var app in this.apps) {
      this.readAppStats(this.apps[app].name);
    }
  },
  beforeDestroy() {
    this.closeStats();
  }
};
</script>

<style>
.AppTitle {
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}
</style>
