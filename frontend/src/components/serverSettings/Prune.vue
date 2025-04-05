<template>
  <v-card color="foreground">
    <v-fade-transition>
      <v-progress-linear
        indeterminate
        v-if="isLoading"
        color="primary"
        bottom
      />
    </v-fade-transition>
    <v-card-title class="subheading warning font-weight-bold"
      >Prune</v-card-title
    >
    <v-card-text class="mt-2"
      >Delete unused images, volumes, networks, and containers.</v-card-text
    >
    <v-btn
      class="mx-5 mb-5"
      color="warning"
      @click="prune((resource = 'images'))"
    >
      Prune Images
    </v-btn>
    <v-btn
      class="mx-5 mb-5"
      color="warning"
      @click="prune((resource = 'networks'))"
    >
      Prune Networks
    </v-btn>
    <v-btn
      class="mx-5 mb-5"
      color="warning"
      @click="prune((resource = 'volumes'))"
    >
      Prune Volumes
    </v-btn>
    <v-dialog max-width="290" v-model="containerDialog">
      <template v-slot:activator="{ on, attrs }">
        <v-btn class="mx-5 mb-5" color="warning" v-bind="attrs" v-on="on">
          Prune Containers
        </v-btn>
      </template>
      <v-card>
        <v-card-title>
          Prune Containers
        </v-card-title>
        <v-card-text>
          This will remove all stopped containers. Please make sure this is what
          you want to do before continuing.
        </v-card-text>
        <v-card-actions color="background">
          <v-spacer></v-spacer>
          <v-btn @click="containerDialog = false">Cancel</v-btn>
          <v-btn
            color="red"
            @click="
              containerDialog = false;
              prune((resource = 'containers'));
            "
            >Continue</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import axios from "axios";
import { mapMutations } from "vuex";
export default {
  data() {
    return {
      containerDialog: false,
      isLoading: false
    };
  },
  methods: {
    ...mapMutations({
      setMessage: "snackbar/setMessage",
      setErr: "snackbar/setErr"
    }),
    formatBytes(bytes) {
      if (bytes === 0) return "0 Bytes";
      const decimals = 2;
      const k = 1024;
      const dm = decimals < 0 ? 0 : decimals;
      const sizes = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];

      const i = Math.floor(Math.log(bytes) / Math.log(k));

      return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
    },
    prune(resource) {
      this.isLoading = true;
      axios({
        url: "/api/settings/prune/" + resource,
        method: "GET",
        responseType: "text/json"
      })
        .then(response => {
          let action = Object.keys(response.data)[0];
          if (response.data[action] != null) {
            var deletedNumber = response.data[action].length;
          } else {
            deletedNumber = "0";
          }
          this.setMessage(
            deletedNumber +
              " " +
              action +
              ". Space Reclaimed: " +
              this.formatBytes(response.data.SpaceReclaimed)
          );
          this.isLoading = false;
        })
        .catch(err => {
          this.setErr(err);
          this.isLoading = false;
        });
    }
  }
};
</script>
