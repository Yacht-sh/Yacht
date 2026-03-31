<template>
  <v-row>
    <v-col xs="12" sm="12" md="6" class="flex-grow-1 flex-shrink-0">
      <v-card
        :class="{
          'mx-4 primary': $vuetify.breakpoint.smAndDown,
          'ml-4 primary flex-shrink-1 flex-grow-0': $vuetify.breakpoint.mdAndUp,
        }"
      >
        <v-card-title>
          {{ app.name }}
          <v-chip small class="ml-3" color="secondary">
            {{ appHostName }}
          </v-chip>
          <v-spacer />
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                size="x-small"
                color="secondary"
                v-bind="attrs"
                v-on="on"
                :href="supportBundleUrl"
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
                @click="$emit('edit')"
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
                color="secondary"
                v-bind="attrs"
                v-on="on"
                @click="$emit('refresh')"
              >
                <v-icon>mdi-refresh</v-icon>
              </v-btn>
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
              <v-list-item @click="$emit('edit')">
                <v-list-item-icon>
                  <v-icon>mdi-file-document-edit-outline</v-icon>
                </v-list-item-icon>
                <v-list-item-title>Edit</v-list-item-title>
              </v-list-item>
              <v-list-item :href="supportBundleUrl" target="_blank" download>
                <v-list-item-icon>
                  <v-icon>mdi-help-circle-outline</v-icon>
                </v-list-item-icon>
                <v-list-item-title>Help</v-list-item-title>
              </v-list-item>
              <v-divider />
              <v-list-item
                v-for="item in mobileActionItems"
                :key="item.action"
                @click="triggerAction(item.action)"
              >
                <v-list-item-icon>
                  <v-icon>{{ item.icon }}</v-icon>
                </v-list-item-icon>
                <v-list-item-title>{{ item.label }}</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
          <v-dialog v-model="removeDialog" max-width="290">
            <v-card>
              <v-card-title class="headline" style="word-break: break-all;">
                Remove {{ app.name }}?
              </v-card-title>
              <v-card-text>
                Are you sure you want to permanently delete the template?<br />
                This action cannot be revoked.
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn text @click="removeDialog = false">Cancel</v-btn>
                <v-btn text color="error" @click="confirmRemove">Delete</v-btn>
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
          'mr-4 primary': $vuetify.breakpoint.mdAndUp,
        }"
      >
        <v-card-title class="d-flex justify-space-between">
          <v-tooltip
            v-for="button in desktopActionButtons"
            :key="button.action"
            bottom
          >
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                color="secondary"
                class="mx-1 my-1"
                v-bind="attrs"
                v-on="on"
                @click="triggerAction(button.action)"
              >
                <span class="hidden-md-and-down">{{ button.label }}</span>
                <v-icon>{{ button.icon }}</v-icon>
              </v-btn>
            </template>
            <span>{{ button.label }}</span>
          </v-tooltip>
        </v-card-title>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
const ACTION_BUTTONS = [
  { action: "start", label: "Start", icon: "mdi-play" },
  { action: "stop", label: "Stop", icon: "mdi-stop" },
  { action: "restart", label: "Restart", icon: "mdi-refresh" },
  { action: "kill", label: "Kill", icon: "mdi-fire" },
  { action: "remove", label: "Remove", icon: "mdi-delete" },
];

export default {
  props: {
    app: {
      type: Object,
      required: true,
    },
    appHostName: {
      type: String,
      required: true,
    },
    supportBundleUrl: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      removeDialog: false,
      desktopActionButtons: ACTION_BUTTONS,
    };
  },
  computed: {
    mobileActionItems() {
      return ACTION_BUTTONS;
    },
  },
  methods: {
    triggerAction(action) {
      if (action === "remove") {
        this.removeDialog = true;
        return;
      }
      this.$emit("action", action);
    },
    confirmRemove() {
      this.removeDialog = false;
      this.$emit("action", "remove");
    },
  },
};
</script>
