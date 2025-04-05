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
        <v-row>
          <v-col xs="12" sm="12" md="6" class="flex-grow-1 flex-shrink-0">
            <v-card
              :class="{
                'mx-4 primary': $vuetify.breakpoint.smAndDown,
                'ml-4 primary flex-shrink-1 flex-grow-0':
                  $vuetify.breakpoint.mdAndUp
              }"
            >
              <v-card-title>
                {{ app.name }}
                <v-spacer />
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn
                      size="x-small"
                      color="secondary"
                      v-bind="attrs"
                      v-on="on"
                      :href="`/api/apps/${app.name}/support`"
                      target="_blank"
                      download
                      class="mx-1 my-1 hidden-sm-and-down"
                    >
                      <span class="hidden-md-and-down">Help</span>
                      <v-icon>mdi-help-circle-outline</v-icon>
                    </v-btn>
                  </template>
                  <span>Download Support Bundle</span>
                </v-tooltip>
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn
                      size="x-small"
                      color="secondary"
                      v-bind="attrs"
                      v-on="on"
                      class="mx-1 my-1 hidden-sm-and-down"
                      @click="editClick({ Name: app.name })"
                    >
                      <span class="hidden-md-and-down">Edit</span>
                      <v-icon>mdi-file-document-edit-outline</v-icon>
                    </v-btn>
                  </template>
                  <span>Edit</span>
                </v-tooltip>
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn
                      size="x-small"
                      @click="refresh()"
                      v-bind="{ attrs }"
                      v-on="on"
                      color="secondary"
                      ><v-icon>mdi-refresh</v-icon></v-btn
                    >
                  </template>
                  <span>Refresh</span>
                </v-tooltip>
                <v-menu
                  close-on-click
                  close-on-content-click
                  offset-y
                  class="hidden-md-and-up"
                >
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn
                      size="small"
                      color="secondary"
                      v-bind="attrs"
                      v-on="on"
                      class="hidden-md-and-up mx-1"
                    >
                      <v-icon>mdi-chevron-down</v-icon>
                    </v-btn>
                  </template>
                  <v-list color="foreground" class="hidden-md-and-up" dense>
                    <v-list-item @click="editClick({ Name: app.name })">
                      <v-list-item-icon>
                        <v-icon>mdi-file-document-edit-outline</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>Edit</v-list-item-title>
                    </v-list-item>
                    <v-list-item
                      :href="`/api/apps/${app.name}/support`"
                      target="_blank"
                      color="primary"
                      download
                    >
                      <v-list-item-icon>
                        <v-icon>mdi-help-circle-outline</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>Help</v-list-item-title>
                    </v-list-item>
                    <v-divider />
                    <v-list-item
                      @click="
                        AppAction({ Name: app.name, Action: 'start' });
                        readAppLogs(app.name);
                        readAppStats(app.name);
                      "
                    >
                      <v-list-item-icon>
                        <v-icon>mdi-play</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>Start</v-list-item-title>
                    </v-list-item>
                    <v-list-item
                      @click="
                        AppAction({ Name: app.name, Action: 'stop' });
                        closeLogs();
                        closeStats();
                      "
                    >
                      <v-list-item-icon>
                        <v-icon>mdi-stop</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>Stop</v-list-item-title>
                    </v-list-item>
                    <v-list-item
                      @click="AppAction({ Name: app.name, Action: 'restart' })"
                    >
                      <v-list-item-icon>
                        <v-icon>mdi-refresh</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>Restart</v-list-item-title>
                    </v-list-item>
                    <v-divider />
                    <v-list-item
                      @click="
                        AppAction({ Name: app.name, Action: 'kill' });
                        closeLogs();
                        closeStats();
                      "
                    >
                      <v-list-item-icon>
                        <v-icon>mdi-fire</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>Kill</v-list-item-title>
                    </v-list-item>
                    <v-list-item @click="removeDialog = true">
                      <v-list-item-icon>
                        <v-icon>mdi-delete</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>Remove</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-menu>
                <v-dialog v-if="app" v-model="removeDialog" max-width="290">
                  <v-card>
                    <v-card-title
                      class="headline"
                      style="word-break: break-all;"
                    >
                      Remove {{ app.name }}?
                    </v-card-title>
                    <v-card-text>
                      Are you sure you want to permanently delete the
                      template?<br />
                      This action cannot be revoked.
                    </v-card-text>
                    <v-card-actions>
                      <v-spacer></v-spacer>
                      <v-btn text @click="removeDialog = false">
                        Cancel
                      </v-btn>
                      <v-btn
                        text
                        color="error"
                        @click="
                          AppAction({ Name: app.name, Action: 'remove' });
                          removeDialog = false;
                          postRemove();
                        "
                      >
                        Delete
                      </v-btn>
                    </v-card-actions>
                  </v-card>
                </v-dialog>
              </v-card-title>
            </v-card>
          </v-col>
          <v-spacer class="hidden-sm-and-down" />
          <v-col sm="12" md="6" class="hidden-sm-and-down">
            <v-card
              :class="{
                'mx-4 primary': $vuetify.breakpoint.smAndDown,
                'mr-4 primary': $vuetify.breakpoint.mdAndUp
              }"
            >
              <v-card-title class="d-flex justify-space-between">
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn
                      v-bind="{ attrs }"
                      v-on="on"
                      color="secondary"
                      class="mx-1 my-1"
                      @click="
                        AppAction({ Name: app.name, Action: 'start' });
                        readAppLogs(app.name);
                        readAppStats(app.name);
                      "
                    >
                      <span class="hidden-md-and-down">start</span>
                      <v-icon>mdi-play</v-icon>
                    </v-btn>
                  </template>
                  <span>Start</span>
                </v-tooltip>
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn
                      v-bind="{ attrs }"
                      v-on="on"
                      color="secondary"
                      class="mx-1 my-1"
                      @click="
                        AppAction({ Name: app.name, Action: 'stop' });
                        closeLogs();
                        closeStats();
                      "
                    >
                      <span class="hidden-md-and-down">stop</span>
                      <v-icon>mdi-stop</v-icon>
                    </v-btn>
                  </template>
                  <span>Stop</span>
                </v-tooltip>
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn
                      v-bind="{ attrs }"
                      v-on="on"
                      color="secondary"
                      class="mx-1 my-1"
                      @click="AppAction({ Name: app.name, Action: 'restart' })"
                    >
                      <span class="hidden-md-and-down">restart</span>
                      <v-icon>mdi-refresh</v-icon>
                    </v-btn>
                  </template>
                  <span>Restart</span>
                </v-tooltip>
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn
                      v-bind="attrs"
                      v-on="on"
                      color="secondary"
                      class="mx-1 my-1"
                      @click="
                        AppAction({ Name: app.name, Action: 'kill' });
                        closeLogs();
                        closeStats();
                      "
                    >
                      <span class="hidden-md-and-down">kill</span>
                      <v-icon>mdi-fire</v-icon>
                    </v-btn>
                  </template>
                  <span>Kill</span>
                </v-tooltip>
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn
                      v-bind="attrs"
                      v-on="on"
                      color="secondary"
                      class="mx-1 my-1"
                      @click="removeDialog = true"
                    >
                      <span class="hidden-md-and-down">remove</span>
                      <v-icon>mdi-delete</v-icon>
                    </v-btn>
                  </template>
                  <span>Remove</span>
                </v-tooltip>
              </v-card-title>
            </v-card>
          </v-col>
        </v-row>
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
import { mapActions, mapGetters, mapState } from "vuex";
export default {
  components: {
    Content: AppContent,
    Processes: AppProcesses,
    Logs: AppLogs,
    Stats: AppStats
  },
  data() {
    return {
      AppTab: 1,
      removeDialog: false,
      logs: [],
      stats: {
        time: [],
        cpu_percent: [],
        mem_percent: [],
        mem_current: [],
        mem_total: []
      },
      connection: null,
      statConnection: null
    };
  },
  computed: {
    ...mapState("apps", ["apps", "app", "isLoading", "processes"]),
    ...mapGetters({
      getAppByName: "apps/getAppByName"
    }),
    app() {
      const appName = this.$route.params.appName;
      return this.getAppByName(appName);
    }
  },
  methods: {
    ...mapActions({
      readApp: "apps/readApp",
      readAppProcesses: "apps/readAppProcesses",
      AppAction: "apps/AppAction"
    }),
    editClick(appName) {
      this.$router.push({ path: `/apps/edit/${appName.Name}` });
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
    postRemove() {
      this.$router.push({ name: "View Applications" });
    },
    readAppLogs(appName) {
      this.logConnection = new EventSource(`/api/apps/${appName}/logs`);
      this.logConnection.addEventListener("update", event => {
        this.logs.push(event.data);
      });
    },
    readAppStats(appName) {
      this.statConnection = new EventSource(`/api/apps/${appName}/stats`);
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
      this.logConnection.close();
      this.logs = [];
    },
    closeStats() {
      this.statConnection.close();
      this.stats = {
        time: [],
        cpu_percent: [],
        mem_percent: [],
        mem_current: [],
        mem_total: []
      };
    }
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
  beforeDestroy() {
    this.closeLogs();
    this.closeStats();
  }
};
</script>

<style></style>
