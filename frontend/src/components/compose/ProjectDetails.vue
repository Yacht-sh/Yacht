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
          <v-expansion-panel
            v-for="(service, index) in Object.keys(project.services)"
            :key="index"
          >
            <v-expansion-panel-header color="secondary">
              <v-row no-gutters style="max-height: 20px">
                <v-col cols="2">{{ service }} </v-col>
                <v-col cols="5" class="text--secondary">
                  ({{ project.services[service].image || "No Image" }})
                </v-col>
                <v-col cols="2" class="text--secondary">
                  {{
                    getStatus(
                      project.services[service].container_name || service
                    ) || "not created"
                  }}
                </v-col>
              </v-row>
            </v-expansion-panel-header>
            <v-expansion-panel-content color="foreground">
              <div class="text-center mt-2">
                <v-item-group dense class="v-btn-toggle">
                  <v-btn
                    small
                    @click="
                      projectAppAction({
                        Project: project.name,
                        Name: service,
                        Action: 'up'
                      })
                    "
                  >
                    <v-icon small>mdi-arrow-up-bold</v-icon>
                    up
                  </v-btn>
                  <v-divider vertical />
                  <v-btn
                    small
                    @click="
                      projectAppAction({
                        Project: project.name,
                        Name: service,
                        Action: 'start'
                      })
                    "
                  >
                    <v-icon small>mdi-play</v-icon>
                    start
                  </v-btn>
                  <v-btn
                    small
                    @click="
                      projectAppAction({
                        Project: project.name,
                        Name: service,
                        Action: 'stop'
                      })
                    "
                  >
                    <v-icon small>mdi-stop</v-icon>
                    stop
                  </v-btn>
                  <v-btn
                    small
                    @click="
                      projectAppAction({
                        Project: project.name,
                        Name: service,
                        Action: 'restart'
                      })
                    "
                  >
                    <v-icon small>mdi-refresh</v-icon>
                    restart
                  </v-btn>
                  <v-divider vertical />
                  <v-btn
                    small
                    @click="
                      projectAppAction({
                        Project: project.name,
                        Name: service,
                        Action: 'pull'
                      })
                    "
                  >
                    <v-icon small>mdi-update</v-icon>
                    pull
                  </v-btn>
                  <v-divider vertical />
                  <v-btn
                    small
                    @click="
                      projectAppAction({
                        Project: project.name,
                        Name: service,
                        Action: 'kill'
                      })
                    "
                  >
                    <v-icon small>mdi-fire</v-icon>
                    kill
                  </v-btn>
                  <v-btn
                    small
                    @click="
                      projectAppAction({
                        Project: project.name,
                        Name: service,
                        Action: 'rm'
                      })
                    "
                  >
                    <v-icon small>mdi-delete</v-icon>
                    remove
                  </v-btn>
                </v-item-group>
              </div>
              <v-list color="foreground" dense>
                <v-list-item v-if="project.services[service].container_name">
                  <v-list-item-content> Container Name </v-list-item-content>
                  <v-list-item-content>
                    {{ project.services[service].container_name }}
                  </v-list-item-content>
                </v-list-item>
                <v-list-item v-if="project.services[service].image">
                  <v-list-item-content> Image </v-list-item-content>
                  <v-list-item-content>
                    {{ project.services[service].image }}
                  </v-list-item-content>
                </v-list-item>
                <v-list-item v-if="project.services[service].env_file">
                  <v-list-item-content> Env File </v-list-item-content>
                  <v-list-item-content>
                    {{ project.services[service].env_file }}
                  </v-list-item-content>
                </v-list-item>
                <v-list-item v-if="project.services[service].depends_on">
                  <v-list-item-content> Depends on </v-list-item-content>
                  <v-list-item-content>
                    {{ project.services[service].depends_on.join(", ") }}
                  </v-list-item-content>
                </v-list-item>
                <v-list-item v-if="project.services[service].restart">
                  <v-list-item-content> Restart Policy </v-list-item-content>
                  <v-list-item-content>
                    {{ project.services[service].restart }}
                  </v-list-item-content>
                </v-list-item>
                <v-list-item v-if="project.services[service].read_only">
                  <v-list-item-content> Read Only </v-list-item-content>
                  <v-list-item-content>
                    {{ project.services[service].read_only }}
                  </v-list-item-content>
                </v-list-item>
                <v-list-item
                  v-if="
                    project.services[service].networks &&
                      Array.isArray(project.services[service].networks)
                  "
                >
                  <v-list-item-content> Networks </v-list-item-content>
                  <v-list-item-content>
                    {{ project.services[service].networks.join(", ") }}
                  </v-list-item-content>
                </v-list-item>
                <v-list-item
                  v-else-if="
                    project.services[service].networks &&
                      typeof project.services[service].networks === 'object'
                  "
                >
                  <v-list-item-content> Networks </v-list-item-content>
                  <v-list-item-content
                    v-for="(content, network) in project.services[service]
                      .networks"
                    :key="network"
                  >
                    {{ network }}, {{ content[Object.keys(content)[0]] }}
                  </v-list-item-content>
                </v-list-item>
                <v-list-item v-if="project.services[service].ports">
                  <v-list-item-content> Ports </v-list-item-content>
                  <v-list-item-content>
                    {{ project.services[service].ports.join(", ") }}
                  </v-list-item-content>
                </v-list-item>
                <v-list-item v-if="project.services[service].volumes">
                  <v-list-item-content> Volumes </v-list-item-content>
                  <v-list-item-content>
                    <v-card outlined tile>
                      <v-simple-table class="secondary" dense>
                        <thead>
                          <tr>
                            <th>Host</th>
                            <th>Container</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr
                            v-for="(value, index) in project.services[service]
                              .volumes"
                            :key="index"
                          >
                            <td>
                              {{ value.split(":")[0] }}
                            </td>
                            <td>
                              {{ value.split(":")[1] }}
                            </td>
                          </tr>
                        </tbody>
                      </v-simple-table>
                    </v-card>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item v-if="project.services[service].environment">
                  <v-list-item-content> Environment </v-list-item-content>
                  <v-list-item-content>
                    <v-card outlined tile>
                      <v-simple-table class="secondary" dense>
                        <thead>
                          <tr>
                            <th>Variable</th>
                            <th>Value</th>
                          </tr>
                        </thead>
                        <tbody
                          v-if="
                            Array.isArray(project.services[service].environment)
                          "
                        >
                          <tr
                            v-for="(value, index) in project.services[service]
                              .environment"
                            :key="index"
                          >
                            <td>
                              {{ value.split("=")[0] }}
                            </td>
                            <td>
                              {{ value.split("=")[1] }}
                            </td>
                          </tr>
                        </tbody>
                        <tbody
                          v-else-if="
                            isObject(project.services[service].environment)
                          "
                        >
                          <tr
                            v-for="(value, index) in project.services[service]
                              .environment"
                            :key="index"
                          >
                            <td>
                              {{ index }}
                            </td>
                            <td>
                              {{ value }}
                            </td>
                          </tr>
                        </tbody>
                      </v-simple-table>
                    </v-card>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item v-if="project.services[service].labels">
                  <v-list-item-content> Labels </v-list-item-content>
                  <v-list-item-content>
                    <v-card outlined tile>
                      <v-simple-table class="secondary" dense>
                        <thead>
                          <tr>
                            <th>Label</th>
                            <th>Value</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr
                            v-for="(value, index) in project.services[service]
                              .labels"
                            :key="index"
                          >
                            <td>
                              {{ value.split("=")[0] }}
                            </td>
                            <td>
                              {{ value.split("=")[1] }}
                            </td>
                          </tr>
                        </tbody>
                      </v-simple-table>
                    </v-card>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item v-if="project.services[service].command">
                  <v-list-item-content> Command </v-list-item-content>
                  <v-list-item-content>
                    <v-card outlined tile>
                      <v-simple-table class="secondary" dense>
                        <tbody
                          v-if="
                            Array.isArray(project.services[service].command)
                          "
                        >
                          <tr
                            v-for="(value, index) in project.services[service]
                              .command"
                            :key="index"
                          >
                            <td>
                              {{ value }}
                            </td>
                          </tr>
                        </tbody>
                        <tbody v-else>
                          <tr>
                            <td>
                              {{ project.services[service].command }}
                            </td>
                          </tr>
                        </tbody>
                      </v-simple-table>
                    </v-card>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-expansion-panel-content>
          </v-expansion-panel>
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
        :href="`/api/compose/${project.name}/support`"
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

export default {
  data() {
    return {
      selectedProject: null,
      deleteDialog: false
    };
  },
  computed: {
    ...mapState("projects", ["project", "projects", "isLoading", "action"]),
    ...mapState("apps", ["apps"]),
    ...mapGetters({
      getProjectByName: "projects/getProjectByName"
    }),
    project() {
      const projectName = this.$route.params.projectName;
      return this.getProjectByName(projectName);
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
    postDelete() {
      this.$router.push({ name: "View Projects" });
    },
    isObject(val) {
      if (val === null) {
        return false;
      }
      return typeof val === "function" || typeof val === "object";
    },
    getStatus(name) {
      for (var app in this.apps) {
        if (
          this.apps[app].name == name ||
          this.apps[app].name ==
            this.project.name.toLowerCase() + "_" + name + "_1"
        ) {
          return this.apps[app].State.Status;
        }
      }
    },

    reload() {
      const projectName = this.$route.params.projectName;
      this.readProject(projectName);
      this.readApps();
    }
  },
  mounted() {
    const projectName = this.$route.params.projectName;
    this.readProject(projectName);

    this.readApps();
  }
};
</script>

<style scoped></style>
