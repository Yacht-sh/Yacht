<template lang="html">
  <div class="d-flex templates-details page">
    <v-container
      fluid
      v-if="template"
      class="templateDetailsContainer component"
    >
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
          {{ template.title }}
        </v-card-title>
        <v-card-subtitle>
          {{ template.url }}
        </v-card-subtitle>
      </v-card>
      <v-text-field label="Search" v-model="search"></v-text-field>
      <v-row dense class="mt-3">
        <v-col
          v-for="item in sortByTitle(filteredTemplateItems)"
          :key="item.id"
          cols="12"
          xl="2"
          md="3"
          sm="4"
          xs="12"
          class="d-flex"
          style="flex-direction:column"
        >
          <v-card color="foreground" class="flex-grow-1">
            <v-img
              :src="item.logo"
              contain
              class="white--text align-end"
              gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
              aspect-ratio="1"
              height="200px"
            >
              <v-card-title v-text="item.title"></v-card-title>
            </v-img>
            <v-card-text style="overflow-y: auto; height:168px">
              <!--
                Back link required!
                Perhaps display the description scrollable and add an action
                "Deploy"
                {{ item.description ? item.description : "" | truncate(200) }}
              -->
              {{ item.description ? item.description : "" | truncate(120) }}
            </v-card-text>

            <v-card-actions>
              <v-btn
                text
                @click="
                  selectedApp = item;
                  appDetailsDialog = true;
                "
              >
                View
              </v-btn>
              <v-spacer></v-spacer>
              <v-btn
                text
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
    <v-dialog
      v-model="appDetailsDialog"
      scrollable
      class="mt-20"
      max-width="90%"
      v-if="selectedApp"
    >
      <v-card color="foreground" raised shaped>
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
                    <a
                      :href="
                        'https://' +
                          'hub.docker.com/r/' +
                          selectedApp.image.split(':')[0]
                      "
                      >{{ selectedApp.image }}</a
                    >
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
              <v-divider v-if="selectedApp.command" />
              <v-list-item v-if="selectedApp.command">
                <v-list-item-content>
                  <v-list-item-title
                    class="px-5 text-centered font-weight-bold"
                  >
                    Command
                  </v-list-item-title>
                </v-list-item-content>
                <v-list-item-content>
                  <v-list-item-title v-if="Array.isArray(selectedApp.command)">
                    <p
                      v-for="(item, index) in selectedApp.command"
                      :key="index"
                    >
                      {{ item }}
                    </p>
                  </v-list-item-title>
                  <v-list-item-title v-else>
                    {{ selectedApp.command }}
                  </v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card>
          <v-card v-if="selectedApp.ports" tile>
            <v-card-title class="subheading indigo darken-2 font-weight-bold">
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
                  <v-list-item-title class="px-5 text-centered font-weight-bold"
                    >Container Port/Proto</v-list-item-title
                  ></v-list-item-content
                >
              </v-list-item>
              <v-divider />
              <v-list-item v-for="port in selectedApp.ports" :key="port.hport">
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
            <v-card-title class="subheading amber darken-2 font-weight-bold">
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
                  <v-list-item-title class="px-5 text-centered font-weight-bold"
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
            <v-card-title class="subheading green darken-3 font-weight-bold">
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
              <v-list-item v-for="env in selectedApp.env" :key="env.label">
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
</template>

<script>
import { mapActions, mapState, mapGetters } from "vuex";
export default {
  data() {
    return {
      appDetailsDialog: false,
      selectedApp: null,
      search: ""
    };
  },
  computed: {
    ...mapGetters({
      getTemplateById: "templates/getTemplateById"
    }),
    ...mapState("templates", ["isLoading"]),
    template() {
      const templateId = this.$route.params.templateId;
      return this.getTemplateById(templateId);
    },
    filteredTemplateItems() {
      const templ = this.template;
      if (!templ) {
        return [];
      }
      if (this.search.length === "") {
        return this.items;
      }
      return templ.items.filter(this.filterByTitle);
    }
  },
  methods: {
    ...mapActions({
      readTemplate: "templates/readTemplate"
    }),
    sortByTitle(arr) {
      // Set slice() to avoid to generate an infinite loop!
      return arr.slice().sort(function(a, b) {
        return a.title.localeCompare(b.title);
      });
    },
    filterByTitle(item) {
      if (!("title" in item)) {
        return false;
      }
      const regex = new RegExp(this.search, "i");
      return regex.test(item.title);
      // return item.title.includes(this.search);
    }
  },
  created() {
    const templateId = this.$route.params.templateId;
    this.readTemplate(templateId);
  }
};
</script>

<style lang="css">
/* .templateDetailsContainer{
  width:98%
} */
</style>
