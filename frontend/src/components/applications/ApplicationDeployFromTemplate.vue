<template lang="html">
  <v-card class="mx-5">
    <v-card-title>
      Select a template to deploy from
    </v-card-title>
    <v-card v-if="templates.length < 1 || templates == undefined">
      <v-card-title>No Templates Found!</v-card-title>
      <v-card-text>
        No templates available. <a href="/#/templates/new">Add</a> one to view
        information and launch apps from here.</v-card-text
      >
    </v-card>
    <v-tabs v-model="tab" grow v-else>
      <v-tab v-for="template in templates" :key="template.id">
        {{ template.title }}
        <small v-if="template.items">({{ template.items.length }})</small>
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab" v-if="templates">
      <v-tab-item v-for="template in templates" :key="template.id">
        <div>
          <v-card color="secondary">
            <v-fade-transition>
              <v-progress-linear
                indeterminate
                v-if="isLoading"
                color="primary"
                bottom
              />
            </v-fade-transition>
            <v-card-title>
              {{ template.title }}
            </v-card-title>
            <v-card-subtitle>
              {{ template.url }}
            </v-card-subtitle>
            <v-text-field label="Search" v-model="search" class="mx-5" />
            <v-container fluid v-if="template">
              <v-row dense>
                <v-col
                  cols="12"
                  xl="2"
                  md="3"
                  sm="4"
                  xs="12"
                  v-for="item in filterAndSortItems(template.items)"
                  :key="item.id"
                  class="d-flex"
                  style="flex-direction:column"
                >
                  <v-card class="flex-grow-1 mt-1">
                    <v-img
                      :src="item.logo"
                      contain
                      aspect
                      ratio="1"
                      height="200px"
                      gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
                      class="white--text align-end"
                    >
                      <v-card-title>
                        {{ item.name }}
                      </v-card-title>
                    </v-img>

                    <v-card-text style="overflow-y: auto; height:168px">
                      {{
                        item.description ? item.description : "" | truncate(120)
                      }}
                    </v-card-text>
                    <v-card-actions>
                      <v-btn
                        @click="
                          selectedApp = item;
                          appDetailsDialog = true;
                        "
                      >
                        View
                      </v-btn>
                      <v-spacer></v-spacer>
                      <v-btn
                        color="primary"
                        :to="{ name: 'Deploy', params: { appId: item.id } }"
                      >
                        Deploy
                      </v-btn>
                    </v-card-actions>
                  </v-card>
                </v-col>
              </v-row>
            </v-container>
          </v-card>
          <v-dialog
            v-model="appDetailsDialog"
            scrollable
            class="mt-20"
            max-width="90%"
            v-if="selectedApp"
          >
            <v-card raised shaped>
              <v-fade-transition>
                <v-progress-linear
                  indeterminate
                  v-if="isLoading"
                  color="primary"
                  bottom
                />
              </v-fade-transition>
              <v-img
                :src="selectedApp.logo"
                contain
                class="white--text align-end"
                gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
                aspect-ratio="1"
                height="200px"
              >
                <v-card-title class="headline" style="word-break: break-all;">
                  {{ selectedApp.title }}
                </v-card-title>
              </v-img>
              <v-card-text class="pt-2">
                {{ selectedApp.description }}
                <h4 v-if="selectedApp.notes" class="pt-2">Notes:</h4>
                <p v-if="selectedApp.notes" v-html="selectedApp.notes" />
                <v-card tile>
                  <v-card-title class="subheading primary font-weight-bold">
                    General
                  </v-card-title>
                  <v-divider />
                  <v-list class="secondary" dense>
                    <v-list-item>
                      <v-list-item-content
                        ><v-list-item-title
                          class="px-5 text-centered font-weight-bold"
                          >Name</v-list-item-title
                        ></v-list-item-content
                      >

                      <v-list-item-content>
                        <v-list-item-title class="px-5 text-centered">
                          {{ selectedApp.name }}
                        </v-list-item-title>
                      </v-list-item-content>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-content
                        ><v-list-item-title
                          class="px-5 text-centered font-weight-bold"
                          >Image</v-list-item-title
                        ></v-list-item-content
                      >
                      <v-list-item-content>
                        <v-list-item-title class="px-5 text-centered">
                          {{ selectedApp.image }}
                        </v-list-item-title>
                      </v-list-item-content>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-content
                        ><v-list-item-title
                          class="px-5 text-centered font-weight-bold"
                          >Platform</v-list-item-title
                        ></v-list-item-content
                      >
                      <v-list-item-content>
                        <v-list-item-title class="px-5 text-centered">
                          {{ selectedApp.platform }}
                        </v-list-item-title>
                      </v-list-item-content>
                    </v-list-item>
                  </v-list>
                </v-card>
                <v-card v-if="selectedApp.ports" tile>
                  <v-card-title
                    class="subheading indigo darken-2 font-weight-bold"
                  >
                    Ports
                  </v-card-title>
                  <v-divider />
                  <v-list dense class="secondary">
                    <v-list-item>
                      <v-list-item-content
                        ><v-list-item-title
                          class="px-5 text-centered font-weight-bold"
                          >Label</v-list-item-title
                        ></v-list-item-content
                      >
                      <v-list-item-content
                        ><v-list-item-title
                          class="px-5 text-centered font-weight-bold"
                          >Host Port</v-list-item-title
                        ></v-list-item-content
                      >
                      <v-list-item-content>
                        <v-list-item-title
                          class="px-5 text-centered font-weight-bold"
                          >Container Port/Proto</v-list-item-title
                        ></v-list-item-content
                      >
                    </v-list-item>
                    <v-divider />
                    <v-list-item
                      v-for="port in selectedApp.ports"
                      :key="port.hport"
                    >
                      <v-list-item-content
                        ><v-list-item-title class="px-5 text-centered">{{
                          port.label || "None"
                        }}</v-list-item-title></v-list-item-content
                      >
                      <v-list-item-content
                        ><v-list-item-title class="px-5 text-centered">{{
                          port.hport
                        }}</v-list-item-title></v-list-item-content
                      >
                      <v-list-item-content>
                        <v-list-item-title class="px-5 text-centered">
                          {{ port.cport }}/{{ port.proto }}
                        </v-list-item-title>
                      </v-list-item-content>
                    </v-list-item>
                  </v-list>
                </v-card>

                <v-card v-if="selectedApp.volumes" tile>
                  <v-card-title
                    class="subheading amber darken-2 font-weight-bold"
                  >
                    Volumes
                  </v-card-title>
                  <v-divider />
                  <v-list dense class="secondary">
                    <v-list-item>
                      <v-list-item-content
                        ><v-list-item-title
                          class="px-5 text-centered font-weight-bold"
                          >Host</v-list-item-title
                        ></v-list-item-content
                      >
                      <v-list-item-content>
                        <v-list-item-title
                          class="px-5 text-centered font-weight-bold"
                          >Container</v-list-item-title
                        ></v-list-item-content
                      >
                    </v-list-item>
                    <v-divider />
                    <v-list-item
                      v-for="volume in selectedApp.volumes"
                      :key="volume.container"
                    >
                      <v-list-item-content
                        ><v-list-item-title class="px-5 text-centered">{{
                          volume.bind
                        }}</v-list-item-title></v-list-item-content
                      >

                      <v-list-item-content
                        ><v-list-item-title class="px-5 text-centered">{{
                          volume.container
                        }}</v-list-item-title></v-list-item-content
                      >
                    </v-list-item>
                  </v-list>
                </v-card>

                <v-card v-if="selectedApp.env" tile>
                  <v-card-title
                    class="subheading green darken-3 font-weight-bold"
                  >
                    Env Variables
                  </v-card-title>
                  <v-divider />
                  <v-list dense class="secondary">
                    <v-list-item>
                      <v-list-item-content
                        ><v-list-item-title
                          class="px-5 text-centered font-weight-bold"
                          >Label</v-list-item-title
                        ></v-list-item-content
                      >
                      <v-list-item-content
                        ><v-list-item-title
                          class="px-5 text-centered font-weight-bold"
                          >Name</v-list-item-title
                        ></v-list-item-content
                      >
                      <v-list-item-content
                        ><v-list-item-title
                          class="px-5 text-centered font-weight-bold"
                          >Default</v-list-item-title
                        ></v-list-item-content
                      >
                    </v-list-item>
                    <v-divider />
                    <v-list-item
                      v-for="env in selectedApp.env"
                      :key="env.label"
                    >
                      <v-list-item-content
                        ><v-list-item-title class="px-5 text-centered">{{
                          env.label
                        }}</v-list-item-title></v-list-item-content
                      >
                      <v-list-item-content
                        ><v-list-item-title class="px-5 text-centered">{{
                          env.name
                        }}</v-list-item-title></v-list-item-content
                      >
                      <v-list-item-content
                        ><v-list-item-title class="px-5 text-centered">{{
                          env.default
                        }}</v-list-item-title></v-list-item-content
                      >
                    </v-list-item>
                  </v-list>
                </v-card>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>

                <v-btn text @click="appDetailsDialog = false">
                  Cancel
                </v-btn>
                <v-btn
                  text
                  color="primary"
                  :to="{ name: 'Deploy', params: { appId: selectedApp.id } }"
                >
                  Deploy
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>
        </div>
      </v-tab-item>
    </v-tabs-items>
  </v-card>
</template>

<script>
import { mapActions, mapState } from "vuex";
export default {
  data() {
    return {
      appDetailsDialog: false,
      selectedApp: null,
      search: "",
      tab: null
    };
  },
  computed: {
    ...mapState("templates", ["templates", "isLoading"])
  },
  methods: {
    ...mapActions({
      readTemplates: "templates/readTemplatesAndItems"
    }),
    filterItems(items) {
      if (!items) {
        return [];
      }
      if (this.search === "") {
        return items;
      }
      let regex = new RegExp(this.search, "i");
      return items.filter(item => {
        return regex.test(item.title);
      });
    },
    filterAndSortItems(items) {
      let result = this.filterItems(items);
      return [...result].sort((a, b) => {
        return a.title.localeCompare(b.title);
      });
    }
  },
  mounted() {
    this.readTemplates();
  }
};
</script>

<style lang="css">
/* .templateDetailsContainer{
  width:98%
} */
</style>
