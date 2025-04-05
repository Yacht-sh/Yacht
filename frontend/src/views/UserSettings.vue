<template lang="html">
  <v-card class="d-flex mx-auto page">
    <v-container fluid class="component">
      <Nav />
      <v-card tile>
        <v-row>
          <v-col class="flex-grow-1 flex-shrink-0">
            <v-card-title>
              {{ username }}
            </v-card-title>
            <v-card-subtitle> Manage {{ username }} </v-card-subtitle>
            <v-card-text>
              <transition
                name="slide"
                enter-active-class="animated fadeIn delay"
                leave-active-class="animated fadeOut"
                mode="out-in"
              >
                <router-view :currentUsername="username" />
              </transition>
            </v-card-text>
          </v-col>
        </v-row>
      </v-card>
    </v-container>
  </v-card>
</template>

<script>
import { mapState } from "vuex";
import UserSettingsNav from "../components/userSettings/UserSettingsNav";
export default {
  components: {
    Nav: UserSettingsNav
  },
  computed: {
    ...mapState("auth", ["username"])
  }
};
</script>

<style></style>
