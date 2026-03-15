<template>
  <v-card color="foreground" class="mx-4 mt-2" raised>
    <v-card-title class="primary font-weight-bold"> Logs</v-card-title>
    <v-card-text
      v-if="app.State.Status != 'running'"
      class="foreground text-center px-5 py-5"
    >
      Start the app to view logs
    </v-card-text>
    <v-virtual-scroll
      v-chat-scroll="scrollOptions"
      v-else
      :bench="20"
      :items="logs"
      height="600"
      item-height="20"
      class="keep-whitespace"
      id="logcontainer"
    >
      <template v-slot="{ item }">
        <p id="logtext">
          {{ item }}
        </p>
      </template>
    </v-virtual-scroll>
  </v-card>
</template>

<script>
// import axios from "axios";
export default {
  props: ["app", "logs"],
  data() {
    return {
      scrollOptions: {
        enable: true,
        always: false,
        smooth: false,
        notSmoothOnInit: true,
      },
    };
  },
};
</script>

<style>
#logtext {
  font: 1rem Inconsolata, monospace;
}
#logcontainer {
  background-color: var(--v-background-base) !important;
}
.keep-whitespace {
  white-space: pre;
}
</style>
