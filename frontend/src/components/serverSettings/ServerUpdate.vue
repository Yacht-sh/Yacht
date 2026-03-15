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
    <v-card-title class="subheading primary font-weight-bold"
      >Update</v-card-title
    >
    <v-card-text class="mt-2"
      >Update Yacht to the latest version. <br />
      Note: This will spin up a run-once watchtower instance and update Yacht.
      In the process Yacht will be restarted and you will be logged
      out.</v-card-text
    >
    <v-btn
      class="mx-5 mb-5"
      color="primary"
      @click="checkUpdate()"
      :disabled="checkedUpdate"
      >
      Check For Updates
    </v-btn>
    <v-btn
      class="mx-5 mb-5"
      color="primary"
      @click="update()"
      :disabled="!updatable"
    >
      Update Yacht
    </v-btn>
  </v-card>
</template>

<script>
import axios from "axios";
import { mapMutations, mapActions, mapState } from "vuex";
export default {
  data() {
    return {
      containerDialog: false,
      isLoading: false,
      checkedUpdate: false,
      updatable: false
    };
  },
  methods: {
    ...mapMutations({
      setMessage: "snackbar/setMessage",
      setErr: "snackbar/setErr"
    }),
    ...mapState({
      authDisabled: "auth/authDisabled"
    }),
    ...mapActions({
      logout: "auth/AUTH_LOGOUT"
    }),
    checkUpdate() {
      this.checkedUpdate = true
      this.isLoading = true;
      axios({
        url: "/api/settings/check/update",
        method: "GET",
        responseType: "text/json"
      })
        .then(response => {
          this.isLoading = false;
          if (response.data == false){
            this.setErr("No update found.")
          }
          this.updatable = response.data;
        })
        .catch(err => {
          this.isLoading = false;
          this.setErr(err);
        });
    },
    update() {
      this.isLoading = true;
      axios({
        url: "/api/settings/update",
        method: "GET",
        responseType: "text/json"
      })
        .then(response => {
          this.isLoading = false;
          console.log(response.data);
          this.setMessage(
            "Yacht is updating now. You will be logged out to complete the update."
          );
        })
        .finally(() => {
          this.isLoading = true;
          const sleep = delay =>
            new Promise(resolve => setTimeout(resolve, delay));
          sleep(5000);
          if (this.authDisabled == true) {
            this.$forceUpdate();
          } else {
            this.logout();
            this.$forceUpdate();
          }
        })
        .catch(err => {
          this.isLoading = false;
          this.setErr(err);
        });
    }
  }
};
</script>
