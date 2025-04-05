<template lang="html">
  <div class="projects-list component" style="max-width: 90%">
    <v-card color="foreground">
      <v-fade-transition>
        <v-progress-linear
          indeterminate
          v-if="isLoading"
          color="primary"
          bottom
        />
      </v-fade-transition>
      <v-card-title class="primary font-weight-bold">
        Projects
        <v-btn class="ml-2" color="secondary" to="/projects/_/edit">
          <v-icon>mdi-plus</v-icon>
        </v-btn>
        <v-spacer />
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
        ></v-text-field>
      </v-card-title>
      <v-card-subtitle v-if="action"
        >Running docker-compose {{ action }} ...</v-card-subtitle
      >

      <v-data-table
        style="max-width: 99%;"
        class="mx-auto project-datatable foreground"
        :headers="headers"
        :items="projects"
        :items-per-page="25"
        :footer-props="{
          'items-per-page-options': [15, 25, 50, -1]
        }"
        :search="search"
        @click:row="handleRowClick"
      >
        <template slot="no-data">
          <div>
            No Projects available.
          </div>
        </template>
        <template v-slot:item.name="{ item }">
          <div class="d-flex">
            <v-menu
              :close-on-click="true"
              :close-on-content-click="false"
              offset-y
            >
              <template v-slot:activator="{ on, attrs }">
                <v-btn icon size="small" v-bind="attrs" v-on="on" class="">
                  <v-icon>mdi-chevron-down</v-icon>
                </v-btn>
              </template>
              <v-list color="foreground" dense>
                <v-list-group prepend-icon="mdi-gamepad">
                  <template slot="activator">
                    <v-list-item-title>Controls </v-list-item-title></template
                  >
                  <v-list color="background" dense>
                    <v-list-item
                      @click="ProjectAction({ Name: item.name, Action: 'up' })"
                    >
                      <v-list-item-icon>
                        <v-icon>mdi-arrow-up-bold</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>Up</v-list-item-title>
                    </v-list-item>
                    <v-list-item
                      @click="
                        ProjectAction({ Name: item.name, Action: 'down' })
                      "
                    >
                      <v-list-item-icon>
                        <v-icon>mdi-arrow-down-bold</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>Down</v-list-item-title>
                    </v-list-item>
                    <v-divider />
                    <v-list-item
                      @click="
                        ProjectAction({ Name: item.name, Action: 'start' })
                      "
                    >
                      <v-list-item-icon>
                        <v-icon>mdi-play</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>Start</v-list-item-title>
                    </v-list-item>
                    <v-list-item
                      @click="
                        ProjectAction({ Name: item.name, Action: 'stop' })
                      "
                    >
                      <v-list-item-icon>
                        <v-icon>mdi-stop</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>Stop</v-list-item-title>
                    </v-list-item>
                    <v-list-item
                      @click="
                        ProjectAction({ Name: item.name, Action: 'restart' })
                      "
                    >
                      <v-list-item-icon>
                        <v-icon>mdi-refresh</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>Restart</v-list-item-title>
                    </v-list-item>
                    <v-divider />
                    <v-list-item
                      @click="
                        ProjectAction({ Name: item.name, Action: 'pull' })
                      "
                    >
                      <v-list-item-icon>
                        <v-icon>mdi-update</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>Pull</v-list-item-title>
                    </v-list-item>
                    <v-list-item
                      @click="
                        ProjectAction({ Name: item.name, Action: 'create' })
                      "
                    >
                      <v-list-item-icon>
                        <v-icon>mdi-plus-box-multiple</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>Create</v-list-item-title>
                    </v-list-item>
                    <v-divider />
                    <v-list-item
                      @click="
                        ProjectAction({ Name: item.name, Action: 'kill' })
                      "
                    >
                      <v-list-item-icon>
                        <v-icon>mdi-fire</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>Kill</v-list-item-title>
                    </v-list-item>

                    <v-list-item
                      @click="ProjectAction({ Name: item.name, Action: 'rm' })"
                    >
                      <v-list-item-icon>
                        <v-icon>mdi-delete</v-icon>
                      </v-list-item-icon>
                      <v-list-item-title>Remove</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-list-group>
                <v-list-item @click="projectDetails(item.name)">
                  <v-list-item-icon>
                    <v-icon>mdi-eye</v-icon>
                  </v-list-item-icon>
                  <v-list-item-title>View</v-list-item-title>
                </v-list-item>
                <v-list-item @click="editProject(item.name)">
                  <v-list-item-icon>
                    <v-icon>mdi-file-document-edit-outline</v-icon>
                  </v-list-item-icon>
                  <v-list-item-title>Edit</v-list-item-title>
                </v-list-item>
                <v-divider />
                <v-list-item
                  @click="
                    selectedProject = item;
                    deleteDialog = true;
                  "
                >
                  <v-list-item-icon>
                    <v-icon>mdi-delete</v-icon>
                  </v-list-item-icon>
                  <v-list-item-title>Delete</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
            <span class="align-streatch text-truncate nametext mt-2">{{
              item.name
            }}</span>
            <v-spacer />

            <v-chip
              outlined
              small
              color="orange lighten-1"
              class="align-center mt-1"
              label
              v-if="item.inUse == false"
              >Unused</v-chip
            >
          </div>
        </template>
        <template v-slot:item.version="{ item }">
          <div class="projectcell">
            <span class="d-inline-block text-truncate idtext">
              {{ item.version }}
            </span>
          </div>
        </template>
        <template v-slot:item.path="{ item }" class="idcell">
          <div class="idcell">
            <span class="d-inline-block text-truncate idtext">
              {{ item.path }}
            </span>
          </div>
        </template>
        <template v-slot:item.services="{ item }" class="idcell">
          <div class="idcell">
            <span class="d-inline-block text-truncate idtext">
              {{ Object.keys(item.services).length }}
            </span>
          </div>
        </template>
      </v-data-table>
    </v-card>
    <v-dialog v-if="selectedProject" v-model="deleteDialog" max-width="400">
      <v-card>
        <v-card-title class="headline" style="word-break: break-all;">
          Delete {{ selectedProject["name"] }} project?
        </v-card-title>
        <v-card-text>
          The project directory and all files within it will be permanently
          deleted. This action cannot be revoked.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="deleteDialog = false">
            Cancel
          </v-btn>
          <v-btn
            text
            color="error"
            @click="
              ProjectAction({ Name: selectedProject.name, Action: 'delete' });
              deleteDialog = false;
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
import { mapActions, mapState } from "vuex";
export default {
  data() {
    return {
      selectedProject: null,
      deleteDialog: false,
      form: {
        name: ""
      },
      createDialog: false,
      search: "",
      headers: [
        {
          text: "Name",
          value: "name",
          sortable: true
        },
        {
          text: "Version",
          value: "version",
          sortable: true
        },
        {
          text: "Services",
          value: "services",
          sortable: false
        },
        {
          text: "Path",
          value: "path",
          sortable: true
        }
      ]
    };
  },
  methods: {
    ...mapActions({
      readProjects: "projects/readProjects",
      ProjectAction: "projects/ProjectAction"
    }),
    handleRowClick(item) {
      this.$router.push({ path: `/projects/${item.name}` });
    },
    editProject(projectname) {
      this.$router.push({ path: `/projects/${projectname}/edit` });
    },
    projectDetails(projectname) {
      this.$router.push({ path: `/projects/${projectname}` });
    }
  },
  computed: {
    ...mapState("projects", ["projects", "isLoading", "action"])
  },
  mounted() {
    this.readProjects();
  }
};
</script>

<style lang="css" scoped></style>
