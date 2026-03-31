<template lang="html">
  <v-card color="foreground" class="d-flex mx-auto page">
    <v-container fluid class="component">
      <div>
        <v-tabs
          v-model="AppTab"
          class="mb-3"
          background-color="tabs"
          mobile-breakpoint="sm"
        >
          <v-tab class="text-left" @click="$router.go(-1)">
            <v-icon left class="mr-1">mdi-arrow-left-bold-outline</v-icon> Back
          </v-tab>
          <v-tab class="text-left">
            <v-icon left class="mr-1">mdi-information-outline</v-icon>Info
          </v-tab>
          <v-tab class="text-left">
            <v-icon left class="mr-1">mdi-view-list-outline</v-icon>Processes
          </v-tab>
          <v-tab class="text-left">
            <v-icon left class="mr-1">mdi-book-open-outline</v-icon>Logs
          </v-tab>
          <v-tab class="text-left">
            <v-icon left class="mr-1">mdi-gauge</v-icon>Stats
          </v-tab>
        </v-tabs>
        <v-fade-transition>
          <v-progress-linear
            indeterminate
            v-if="isLoading"
            color="primary"
            bottom
          />
        </v-fade-transition>
      </div>
      <v-card color="foreground" class="pb-3" tile>
        <ApplicationDetailsHeader
          v-if="app"
          :app="app"
          :app-host-name="appHostName"
          :support-bundle-url="supportBundleUrl(app.name)"
          @edit="editClick({ Name: app.name })"
          @refresh="refresh()"
          @action="handleAppAction"
        />
        <transition
          name="slide"
          enter-active-class="animated slideInRight delay"
          leave-active-class="animated slideOutRight"
          mode="out-in"
        >
          <v-tabs-items v-model="AppTab" touchless class="mt-3">
            <v-tab-item> </v-tab-item>
            <v-tab-item>
              <Content :app="app" />
            </v-tab-item>
            <v-tab-item>
              <Processes :app="app" :processes="processes" />
            </v-tab-item>
            <v-tab-item>
              <Logs :app="app" :logs="logs" />
            </v-tab-item>
            <v-tab-item>
              <Stats :app="app" :stats="stats" />
            </v-tab-item>
          </v-tabs-items>
        </transition>
      </v-card>
    </v-container>
  </v-card>
</template>

<script>
import AppStats from "./ApplicationDetailsComponents/AppStats";
import AppProcesses from "./ApplicationDetailsComponents/AppProcesses";
import AppContent from "./ApplicationDetailsComponents/AppContent";
import AppLogs from "./ApplicationDetailsComponents/AppLogs";
import ApplicationDetailsHeader from "./ApplicationDetailsComponents/ApplicationDetailsHeader";
import { mapActions, mapGetters, mapState } from "vuex";
export default {
  components: {
    Content: AppContent,
    Processes: AppProcesses,
    Logs: AppLogs,
    Stats: AppStats,
    ApplicationDetailsHeader,
  },
  data() {
    return {
      AppTab: 1,
      logs: [],
      stats: {
        time: [],
        cpu_percent: [],
        mem_percent: [],
        mem_current: [],
        mem_total: [],
      },
      logConnection: null,
      statConnection: null,
    };
  },
  computed: {
    ...mapState("apps", ["apps", "app", "isLoading", "processes"]),
    ...mapState("hosts", ["selectedHostId", "hosts"]),
    ...mapGetters({
      getAppByName: "apps/getAppByName",
    }),
    app() {
      const appName = this.$route.params.appName;
      return this.getAppByName(appName);
    },
    appHostName() {
      if (this.app && this.app.YachtHost) {
        return this.app.YachtHost.name;
      }
      const selectedHost = this.hosts.find(host => host.id === this.selectedHostId);
      return selectedHost ? selectedHost.name : "Local";
    }
  },
  methods: {
    ...mapActions({
      readApp: "apps/readApp",
      readAppProcesses: "apps/readAppProcesses",
      AppAction: "apps/AppAction",
    }),
    editClick(appName) {
      this.$router.push({ path: `/apps/edit/${appName.Name}` });
    },
    appQueryString() {
      const query = new URLSearchParams();
      if (this.selectedHostId != null) {
        query.set("host_id", this.selectedHostId);
      }
      const suffix = query.toString();
      return suffix ? `?${suffix}` : "";
    },
    supportBundleUrl(appName) {
      return `/api/apps/${appName}/support${this.appQueryString()}`;
    },
    refresh() {
      const appName = this.$route.params.appName;
      this.readApp(appName);
      this.readAppProcesses(appName);
      this.closeLogs();
      this.closeStats();
      this.readAppLogs(appName);
      this.readAppStats(appName);
    },
    handleAppAction(action) {
      if (!this.app) {
        return;
      }
      const payload = { Name: this.app.name, Action: action };

      if (action === "start") {
        this.AppAction(payload);
        this.readAppLogs(this.app.name);
        this.readAppStats(this.app.name);
        return;
      }

      if (action === "stop" || action === "kill") {
        this.AppAction(payload);
        this.closeLogs();
        this.closeStats();
        return;
      }

      if (action === "remove") {
        this.AppAction(payload);
        this.closeLogs();
        this.closeStats();
        this.postRemove();
        return;
      }

      this.AppAction(payload);
    },
    postRemove() {
      this.$router.push({ name: "View Applications" });
    },
    readAppLogs(appName) {
      this.logConnection = new EventSource(
        `/api/apps/${appName}/logs${this.appQueryString()}`
      );
      this.logConnection.addEventListener("update", event => {
        this.logs.push(event.data);
      });
    },
    readAppStats(appName) {
      this.statConnection = new EventSource(
        `/api/apps/${appName}/stats${this.appQueryString()}`
      );
      this.statConnection.addEventListener("update", event => {
        let statsGroup = JSON.parse(event.data);
        this.stats.time.push(statsGroup.time);
        this.stats.cpu_percent.push(Math.round(statsGroup.cpu_percent));
        this.stats.mem_percent.push(Math.round(statsGroup.mem_percent));
        this.stats.mem_current.push(statsGroup.mem_current);
        this.stats.mem_total.push(statsGroup.mem_total);
        for (let key in this.stats) {
          if (this.stats[key].length > 300) {
            this.stats[key].shift();
          }
        }
      });
    },
    closeLogs() {
      if (this.logConnection && this.logConnection.close) {
        this.logConnection.close();
      }
      this.logs = [];
    },
    closeStats() {
      if (this.statConnection && this.statConnection.close) {
        this.statConnection.close();
      }
      this.stats = {
        time: [],
        cpu_percent: [],
        mem_percent: [],
        mem_current: [],
        mem_total: [],
      };
    },
  },
  created() {
    const appName = this.$route.params.appName;
    this.readApp(appName);
    this.readAppProcesses(appName);
  },
  async mounted() {
    const appName = this.$route.params.appName;
    await this.readApp(appName);
    await this.readAppProcesses(appName);
    await this.readAppLogs(appName);
    await this.readAppStats(appName);
  },
  watch: {
    selectedHostId() {
      this.refresh();
    }
  },
  beforeDestroy() {
    this.closeLogs();
    this.closeStats();
  },
};
</script>

<style></style>
