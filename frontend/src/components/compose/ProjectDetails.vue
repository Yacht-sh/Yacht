<template>
  <div class="page">
    <v-card color="foreground">
      <v-fade-transition>
        <v-progress-linear
          indeterminate
          v-if="isLoading"
          color="primary"
          bottom
        />
      </v-fade-transition>
      <v-card-title>
        <v-row>
          <v-col>
            {{ project.name }}
            <v-chip small class="ml-3" color="secondary">
              {{ projectHostName }}
            </v-chip>
            <v-menu
              :close-on-click="true"
              :close-on-content-click="true"
              offset-y
            >
              <template v-slot:activator="{ on, attrs }">
                <v-btn icon size="small" v-bind="attrs" v-on="on" class="">
                  <v-icon>mdi-chevron-down</v-icon>
                </v-btn>
              </template>
              <v-list color="foreground" dense>
                <v-list-item
                  @click="ProjectAction({ Name: project.name, Action: 'up' })"
                >
                  <v-list-item-icon>
                    <v-icon>mdi-arrow-up-bold</v-icon>
                  </v-list-item-icon>
                  <v-list-item-title>Up</v-list-item-title>
                </v-list-item>
                <v-list-item
                  @click="ProjectAction({ Name: project.name, Action: 'down' })"
                >
                  <v-list-item-icon>
                    <v-icon>mdi-arrow-down-bold</v-icon>
                  </v-list-item-icon>
                  <v-list-item-title>Down</v-list-item-title>
                </v-list-item>
                <v-divider />
                <v-list-item
                  @click="
                    ProjectAction({ Name: project.name, Action: 'start' })
                  "
                >
                  <v-list-item-icon>
                    <v-icon>mdi-play</v-icon>
                  </v-list-item-icon>
                  <v-list-item-title>Start</v-list-item-title>
                </v-list-item>
                <v-list-item
                  @click="ProjectAction({ Name: project.name, Action: 'stop' })"
                >
                  <v-list-item-icon>
                    <v-icon>mdi-stop</v-icon>
                  </v-list-item-icon>
                  <v-list-item-title>Stop</v-list-item-title>
                </v-list-item>
                <v-list-item
                  @click="
                    ProjectAction({ Name: project.name, Action: 'restart' })
                  "
                >
                  <v-list-item-icon>
                    <v-icon>mdi-refresh</v-icon>
                  </v-list-item-icon>
                  <v-list-item-title>Restart</v-list-item-title>
                </v-list-item>
                <v-divider />
                <v-list-item
                  @click="ProjectAction({ Name: project.name, Action: 'pull' })"
                >
                  <v-list-item-icon>
                    <v-icon>mdi-update</v-icon>
                  </v-list-item-icon>
                  <v-list-item-title>Pull</v-list-item-title>
                </v-list-item>
                <v-list-item
                  @click="
                    ProjectAction({ Name: project.name, Action: 'create' })
                  "
                >
                  <v-list-item-icon>
                    <v-icon>mdi-plus-box-multiple</v-icon>
                  </v-list-item-icon>
                  <v-list-item-title>Create</v-list-item-title>
                </v-list-item>
                <v-divider />
                <v-list-item
                  @click="ProjectAction({ Name: project.name, Action: 'kill' })"
                >
                  <v-list-item-icon>
                    <v-icon>mdi-fire</v-icon>
                  </v-list-item-icon>
                  <v-list-item-title>Kill</v-list-item-title>
                </v-list-item>

                <v-list-item
                  @click="ProjectAction({ Name: project.name, Action: 'rm' })"
                >
                  <v-list-item-icon>
                    <v-icon>mdi-delete</v-icon>
                  </v-list-item-icon>
                  <v-list-item-title>Remove</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </v-col>
          <v-col class="text-right">
            <v-btn @click="editProject(project.name)">
              Edit
              <v-icon>mdi-file-document-edit-outline</v-icon>
            </v-btn>
            <v-btn
              @click="
                selectedProject = project;
                deleteDialog = true;
              "
              color="error"
            >
              Delete
              <v-icon>mdi-trash-can-outline</v-icon>
            </v-btn>
          </v-col>
        </v-row>
      </v-card-title>
      <v-card-subtitle v-if="action"
        >Running docker-compose {{ action }} ...</v-card-subtitle
      >
    </v-card>
    <v-card color="foreground" class="mt-2">
      <v-card-title> Project Details </v-card-title>
      <v-list color="foreground" dense>
        <v-list-item>
          <v-list-item-content> Name </v-list-item-content>
          <v-list-item-content>
            {{ project.name }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content> Path </v-list-item-content>
          <v-list-item-content>
            {{ project.path }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content> Version </v-list-item-content>
          <v-list-item-content>
            {{ project.version }}
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>
    <v-card color="foreground" class="mt-2">
      <v-card-title> Services </v-card-title>
      <v-card-text>
        <v-expansion-panels>
          <project-service-panel
            v-for="serviceName in serviceNames"
            :key="serviceName"
            :project-name="project.name"
            :service-name="serviceName"
            :service="project.services[serviceName]"
            :status="serviceStatus(serviceName, project.services[serviceName])"
            @service-action="projectAppAction"
          />
        </v-expansion-panels>
      </v-card-text>
    </v-card>
    <v-card color="foreground" v-if="project.networks" class="mt-2">
      <v-card-title> Networks </v-card-title>
      <v-card-text>
        {{ project.networks.join(", ") }}
      </v-card-text>
    </v-card>
    <v-card color="foreground" v-if="project.volumes" class="mt-2">
      <v-card-title> Volumes </v-card-title>
      <v-card-text>
        {{ project.volumes.join(", ") }}
      </v-card-text>
    </v-card>
    <v-card color="foreground" class="mt-2">
      <v-card-title> Download Support Bundle </v-card-title>
      <v-card-text>
        Download the logs and docker-compose to get help with your
        project</v-card-text
      >
      <v-btn
        :href="supportBundleUrl(project.name)"
        target="_blank"
        class="mb-2 ml-2"
        color="primary"
        download
        >Download</v-btn
      >
    </v-card>
    <v-dialog v-if="selectedProject" v-model="deleteDialog" max-width="400">
      <v-card>
        <v-card-title class="headline" style="word-break: break-all">
          Delete {{ selectedProject["name"] }} project?
        </v-card-title>
        <v-card-text>
          The project directory and all files within it will be permanently
          deleted. This action cannot be revoked.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="deleteDialog = false"> Cancel </v-btn>
          <v-btn
            text
            color="error"
            @click="
              ProjectAction({ Name: selectedProject.name, Action: 'delete' });
              postDelete();
            "
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapActions, mapGetters, mapState } from "vuex";
import ProjectServicePanel from "./ProjectServicePanel.vue";

export default {
  components: {
    ProjectServicePanel
  },
  data() {
    return {
      selectedProject: null,
      deleteDialog: false
    };
  },
  computed: {
    ...mapState("projects", ["isLoading", "action"]),
    ...mapState("apps", ["apps"]),
    ...mapState("hosts", ["selectedHostId", "hosts"]),
    ...mapGetters({
      getProjectByName: "projects/getProjectByName"
    }),
    project() {
      const projectName = this.$route.params.projectName;
      return this.getProjectByName(projectName);
    },
    projectHostName() {
      if (this.project && this.project.YachtHost) {
        return this.project.YachtHost.name;
      }
      const selectedHost = this.hosts.find(
        host => host.id === this.selectedHostId
      );
      return selectedHost ? selectedHost.name : "Local";
    },
    appStatusMap() {
      return this.apps.reduce((statuses, app) => {
        statuses[app.name] = app.State.Status;
        return statuses;
      }, {});
    },
    serviceNames() {
      return Object.keys(this.project.services || {});
    }
  },
  methods: {
    ...mapActions({
      readProject: "projects/readProject",
      projectAppAction: "projects/ProjectAppAction",
      ProjectAction: "projects/ProjectAction",
      readApps: "apps/readApps"
    }),
    editProject(projectname) {
      this.$router.push({ path: `/projects/${projectname}/edit` });
    },
    serviceStatus(serviceName, service) {
      return (
        this.appStatusMap[service.container_name || serviceName] ||
        this.appStatusMap[
          `${this.project.name.toLowerCase()}_${serviceName}_1`
        ] ||
        null
      );
    },
    postDelete() {
      this.$router.push({ name: "View Projects" });
    },
    reload() {
      const projectName = this.$route.params.projectName;
      this.readProject(projectName);
      this.readApps();
    },
    supportBundleUrl(projectName) {
      const query = new URLSearchParams();
      if (this.selectedHostId != null) {
        query.set("host_id", this.selectedHostId);
      }
      const suffix = query.toString();
      return `/api/compose/${projectName}/support${suffix ? `?${suffix}` : ""}`;
    }
  },
  mounted() {
    const projectName = this.$route.params.projectName;
    this.readProject(projectName);

    this.readApps();
  },
  watch: {
    selectedHostId() {
      this.reload();
    }
  }
};
</script>

<style scoped></style>
