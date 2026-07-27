<template>
  <v-card color="foreground" class="elevation-12">
    <v-toolbar color="primary" dark flat>
      <v-toolbar-title>Hosts</v-toolbar-title>
    </v-toolbar>
    <v-card-text>
      Add remote Docker API hosts here and switch between them from the top bar.
      Agent-managed hosts register themselves automatically from remote Docker
      servers running `yacht-agent`.
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
      <template v-slot:item.docker_host="{ item }">
        <span v-if="item.connection_type === 'docker_api'">
          {{ item.docker_host }}
        </span>
        <span v-else-if="item.connection_type === 'agent'"> Agent-managed </span>
        <span v-else> Local socket </span>
      </template>
      <template v-slot:item.agent_status="{ item }">
        <span v-if="item.connection_type !== 'agent'">-</span>
        <v-chip
          v-else-if="agent && (agent.last_heartbeat || item.last_seen)"
          x-small
          :color="isAgentHealthy(agent) ? 'primary' : 'warning'"
        >
          {{ isAgentHealthy(agent) ? 'Online' : 'Stale' }}
        </v-chip>
        <v-chip v-else x-small color="secondary"> Unknown </v-chip>
      </template>
      <template v-slot:item.actions="{ item }">
        <div v-if="item.connection_type === 'agent'">
          <v-select
            v-model="composeForm[item.id].action"
            :items="composeActions"
            label="Action"
            dense
            hide-details
            style="min-width: 100px"
          />
          <v-text-field
            v-model="composeForm[item.id].project"
            label="Project"
            dense
            hide-details
            style="min-width: 180px"
          />
          <v-btn
            icon
            small
            color="primary"
            :disabled="!canQueueCompose(composeForm[item.id])"
            @click="queueComposeAction(item, composeForm[item.id])"
          >
            <v-icon small>mdi-play</v-icon>
          </v-btn>
        </div>
        <span v-else>-</span>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import { mapActions, mapState, mapGetters } from "vuex";

const DEFAULT_COMPOSE_FORM = () => ({ action: "up", project: "", workingDir: "" });

export default {
  data() {
    return {
      form: {
        name: "",
        connection_type: "docker_api",
        docker_host: "",
        is_default: false
      },
      composeActions: ["up", "down", "pull"],
      composeForm: {},
      headers: [
        { text: "Name", value: "name" },
        { text: "Type", value: "connection_type" },
        { text: "Docker Host", value: "docker_host" },
        { text: "Default", value: "is_default" },
        { text: "Active", value: "is_active" },
        { text: "Agent", value: "agent_status" },
        { text: "Compose", value: "actions", sortable: false }
      ]
    };
  },
  computed: {
    ...mapState("hosts", ["hosts", "isLoading", "agentMap"]),
    agent() {
      const hostId = this.selectedHost && this.selectedHost.id;
      return hostId != null ? this.agentMap[hostId] || null : null;
    }
  },
  methods: {
    ...mapActions({
      createHost: "hosts/createHost",
      readHosts: "hosts/readHosts",
      queueComposeAction: "hosts/queueComposeAction"
    }),
    isAgentHealthy(agent) {
      if (!agent || !agent.last_heartbeat) {
        return false;
      }
      const cutoff = Date.now() - 1000 * 60 * 5;
      const last = new Date(agent.last_heartbeat).getTime();
      return Number.isFinite(last) && last >= cutoff;
    },
    canQueueCompose(form) {
      return form && form.action && form.project;
    },
    async queueComposeAction(host, form) {
      if (!host || !host.id) {
        return;
      }
      const payload = {
        hostId: host.id,
        project: form.project,
        action: form.action,
        workingDir: form.workingDir || undefined
      };
      try {
        await this.queueComposeAction(payload);
        this.$set(this.composeForm, host.id, DEFAULT_COMPOSE_FORM());
      } catch (err) {
        // snackbar handled by store
      }
    }
  },
  created() {
    this.readHosts();
  }
};
</script>
