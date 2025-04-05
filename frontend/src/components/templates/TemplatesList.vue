<template lang="html">
  <div class="templates-list component">
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
        Templates
        <v-btn class="ml-2" color="secondary" to="/templates/new">
          <v-icon>mdi-plus</v-icon>
        </v-btn>
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
        ></v-text-field>
      </v-card-title>
      <v-data-table
        class="foreground"
        :headers="headers"
        :items="templates"
        :items-per-page="25"
        :footer-props="{
          'items-per-page-options': [15, 25, 50, -1]
        }"
        :search="search"
        @click:row="handleRowClick"
      >
        <template slot="no-data">
          <div>
            No templates available. <a href="/#/templates/new">Add</a> one to
            view information and launch apps from here.
          </div>
        </template>
        <template v-slot:item.title="{ item }">
          <div class="namecell">
            <span class="nametext">{{ item.title }}</span>
            <v-menu close-on-click close-on-content-click offset-y>
              <template v-slot:activator="{ on, attrs }">
                <v-btn icon size="small" v-bind="attrs" v-on="on">
                  <v-icon>mdi-dots-horizontal</v-icon>
                </v-btn>
              </template>
              <v-list color="foreground" dense>
                <v-list-item @click="templateDetails(item.id)">
                  <v-list-item-icon>
                    <v-icon>mdi-eye</v-icon>
                  </v-list-item-icon>
                  <v-list-item-title>View</v-list-item-title>
                </v-list-item>
                <v-list-item @click="updateTemplate(item.id)">
                  <v-list-item-icon>
                    <v-icon>mdi-update</v-icon>
                  </v-list-item-icon>
                  <v-list-item-title>Update</v-list-item-title>
                </v-list-item>
                <v-divider />
                <v-list-item
                  @click="
                    selectedTemplate = item;
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
        <template v-slot:item.created_at="{ item }">
          <span>{{ item.created_at | formatDate }}</span>
        </template>
        <template v-slot:item.updated_at="{ item }">
          <span>{{ item.updated_at | formatDate }}</span>
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-if="selectedTemplate" v-model="deleteDialog" max-width="290">
      <v-card>
        <v-card-title class="headline" style="word-break: break-all;">
          Delete the template?
        </v-card-title>
        <v-card-text>
          Are you sure you want to permanently delete the template?<br />
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
              deleteTemplate(selectedTemplate.id);
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
      selectedTemplate: null,
      deleteDialog: false,
      search: "",
      headers: [
        {
          text: "Title",
          value: "title",
          sortable: true,
          align: "start"
        },
        {
          text: "Created At",
          value: "created_at",
          sortable: true,
          width: "20%"
        },
        {
          text: "Updated At",
          value: "updated_at",
          sortable: true,
          width: "20%"
        }
      ]
    };
  },
  methods: {
    ...mapActions({
      deleteTemplate: "templates/deleteTemplate",
      readTemplates: "templates/readTemplates",
      updateTemplate: "templates/updateTemplate"
    }),
    handleRowClick(value) {
      this.$router.push({ path: `/templates/${value.id}` });
    },
    templateDetails(templateId) {
      this.$router.push({ path: `/templates/${templateId}` });
    }
  },
  computed: {
    ...mapState("templates", ["templates", "isLoading"])
  },
  mounted() {
    this.readTemplates();
  }
};
</script>

<style lang="css" scoped>
.namecell {
  display: flex;
  min-width: 72px;
  align-items: center;
}
.nametext {
  padding: 0px;
  padding-right: 20px;
  flex-grow: 1;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}
</style>
