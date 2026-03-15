<template>
  <v-card color="foreground" class="elevation-12">
    <v-toolbar color="primary" dark flat>
      <v-toolbar-title>Hosts</v-toolbar-title>
    </v-toolbar>
    <v-card-text>
      Add remote Docker API hosts and switch between them from the top bar.
    </v-card-text>
    <v-form class="mx-4 mb-4" @submit.prevent="submit">
      <v-text-field
        v-model="form.name"
        label="Host Name"
        required
      />
      <v-text-field
        v-model="form.docker_host"
        label="Docker Host URL"
        hint="Example: tcp://192.168.1.50:2375"
        persistent-hint
        required
      />
      <v-checkbox
        v-model="form.is_default"
        label="Set as default host"
      />
      <v-btn color="primary" :loading="isLoading" type="submit">
        Add Host
      </v-btn>
    </v-form>
    <v-data-table
      :headers="headers"
      :items="hosts"
      class="mx-4 mb-4"
      dense
      disable-pagination
      hide-default-footer
    >
      <template v-slot:item.is_default="{ item }">
        <v-chip x-small :color="item.is_default ? 'primary' : 'secondary'">
          {{ item.is_default ? "Default" : "Optional" }}
        </v-chip>
      </template>
      <template v-slot:item.is_active="{ item }">
        <v-chip x-small :color="item.is_active ? 'primary' : 'error'">
          {{ item.is_active ? "Active" : "Inactive" }}
        </v-chip>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import { mapActions, mapState } from "vuex";

export default {
  data() {
    return {
      form: {
        name: "",
        connection_type: "docker_api",
        docker_host: "",
        is_default: false
      },
      headers: [
        { text: "Name", value: "name" },
        { text: "Type", value: "connection_type" },
        { text: "Docker Host", value: "docker_host" },
        { text: "Default", value: "is_default" },
        { text: "Active", value: "is_active" }
      ]
    };
  },
  computed: {
    ...mapState("hosts", ["hosts", "isLoading"])
  },
  methods: {
    ...mapActions({
      createHost: "hosts/createHost",
      readHosts: "hosts/readHosts"
    }),
    async submit() {
      await this.createHost(this.form);
      this.form = {
        name: "",
        connection_type: "docker_api",
        docker_host: "",
        is_default: false
      };
    }
  },
  created() {
    this.readHosts();
  }
};
</script>
