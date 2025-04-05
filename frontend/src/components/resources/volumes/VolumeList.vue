<template lang="html">
  <div class="volumes-list component" style="max-width: 90%">
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
        Volumes
        <v-dialog v-model="createDialog" max-width="290">
          <template v-slot:activator="{ on, attrs }">
            <v-btn class="ml-2" color="secondary" v-bind="attrs" v-on="on">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </template>
          <v-card color="foreground">
            <v-card-title class="headline" style="word-break: break-all;">
              Create Volume
            </v-card-title>
            <v-card-text>
              Create a Volume.
            </v-card-text>
            <form ref="form" @submit.prevent="submit">
              <v-text-field
                label="Volume"
                class="mx-5"
                placeholder="yacht_data"
                required
                v-model="form.name"
              >
              </v-text-field>
            </form>
            <v-card-actions>
              <v-spacer />
              <v-btn text @click="createDialog = false">
                Cancel
              </v-btn>
              <v-btn
                text
                color="primary"
                @click="
                  submit();
                  createDialog = false;
                "
              >
                Create
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
        <v-spacer />
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
        ></v-text-field>
      </v-card-title>

      <v-data-table
        style="max-width: 99%;"
        class="mx-auto volume-datatable foreground"
        :headers="headers"
        :items="volumes"
        :items-per-page="25"
        :footer-props="{
          'items-per-page-options': [15, 25, 50, -1]
        }"
        :search="search"
        @click:row="handleRowClick"
      >
        <template slot="no-data">
          <div>
            No Volumes available.
          </div>
        </template>
        <template v-slot:item.Name="{ item }">
          <div class="d-flex">
            <span class="align-streatch text-truncate nametext mt-2">{{
              item.Name
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
            <v-menu close-on-click close-on-content-click offset-y>
              <template v-slot:activator="{ on, attrs }">
                <v-btn
                  icon
                  class="align-streatch"
                  size="small"
                  v-bind="attrs"
                  v-on="on"
                >
                  <v-icon>mdi-dots-horizontal</v-icon>
                </v-btn>
              </template>
              <v-list color="foreground" dense>
                <v-list-item @click="volumeDetails(item.Name)">
                  <v-list-item-icon>
                    <v-icon>mdi-eye</v-icon>
                  </v-list-item-icon>
                  <v-list-item-title>View</v-list-item-title>
                </v-list-item>
                <v-divider />
                <v-list-item
                  @click="
                    selectedVolume = item;
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
          </div>
        </template>
        <template v-slot:item.Project="{ item }">
          <div class="projectcell">
            <span
              class="d-inline-block text-truncate idtext"
              v-if="item.Labels"
            >
              {{ item.Labels["com.docker.compose.project"] || "-" }}
            </span>
          </div>
        </template>
        <template v-slot:item.Driver="{ item }" class="idcell">
          <div class="idcell">
            <span class="d-inline-block text-truncate idtext">
              {{ item.Driver }}
            </span>
          </div>
        </template>
        <template v-slot:item.CreatedAt="{ item }">
          <span
            class="d-inline-block text-truncate flex-grow-1 flex-shrink-0"
            >{{ item.CreatedAt | formatDate }}</span
          >
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-if="selectedVolume" v-model="deleteDialog" max-width="290">
      <v-card>
        <v-card-title class="headline" style="word-break: break-all;">
          Delete the volume?
        </v-card-title>
        <v-card-text>
          Are you sure you want to permanently delete the volume?<br />
          This action cannot be revoked.
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
              deleteVolume(selectedVolume.Name);
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
      selectedVolume: null,
      deleteDialog: false,
      form: {
        name: ""
      },
      createDialog: false,
      search: "",
      headers: [
        {
          text: "Name",
          value: "Name",
          sortable: true
        },
        {
          text: "Project",
          value: "Project",
          sortable: true
        },
        {
          text: "Driver",
          value: "Driver",
          sortable: true
        },
        {
          text: "Created",
          value: "CreatedAt",
          sortable: true
        }
      ]
    };
  },
  methods: {
    ...mapActions({
      readVolumes: "volumes/readVolumes",
      deleteVolume: "volumes/deleteVolume",
      writeVolume: "volumes/writeVolume"
    }),
    handleRowClick(item) {
      this.$router.push({ path: `/resources/volumes/${item.Name}` });
    },
    volumeDetails(volumename) {
      this.$router.push({ path: `/resources/volumes/${volumename}` });
    },
    submit() {
      const data = this.form;
      this.writeVolume(data);
    }
  },
  computed: {
    ...mapState("volumes", ["volumes", "isLoading"])
  },
  mounted() {
    this.readVolumes();
  }
};
</script>

<style lang="css" scoped>
.nametext {
  max-width: 20vw;
}
.idtext {
  max-width: 30vw;
}
.volume-datatable {
  overflow-x: hidden;
}
</style>
