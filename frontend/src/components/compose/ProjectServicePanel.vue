<template>
  <v-expansion-panel>
    <v-expansion-panel-header color="secondary">
      <v-row no-gutters style="max-height: 20px">
        <v-col cols="2">{{ serviceName }}</v-col>
        <v-col cols="5" class="text--secondary">
          ({{ service.image || "No Image" }})
        </v-col>
        <v-col cols="2" class="text--secondary">
          {{ status || "not created" }}
        </v-col>
      </v-row>
    </v-expansion-panel-header>
    <v-expansion-panel-content color="foreground">
      <div class="text-center mt-2">
        <v-item-group dense class="v-btn-toggle">
          <v-btn small @click="emitAction('up')">
            <v-icon small>mdi-arrow-up-bold</v-icon>
            up
          </v-btn>
          <v-divider vertical />
          <v-btn small @click="emitAction('start')">
            <v-icon small>mdi-play</v-icon>
            start
          </v-btn>
          <v-btn small @click="emitAction('stop')">
            <v-icon small>mdi-stop</v-icon>
            stop
          </v-btn>
          <v-btn small @click="emitAction('restart')">
            <v-icon small>mdi-refresh</v-icon>
            restart
          </v-btn>
          <v-divider vertical />
          <v-btn small @click="emitAction('pull')">
            <v-icon small>mdi-update</v-icon>
            pull
          </v-btn>
          <v-divider vertical />
          <v-btn small @click="emitAction('kill')">
            <v-icon small>mdi-fire</v-icon>
            kill
          </v-btn>
          <v-btn small @click="emitAction('rm')">
            <v-icon small>mdi-delete</v-icon>
            remove
          </v-btn>
        </v-item-group>
      </div>
      <v-list color="foreground" dense>
        <v-list-item v-if="service.container_name">
          <v-list-item-content> Container Name </v-list-item-content>
          <v-list-item-content>
            {{ service.container_name }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="service.image">
          <v-list-item-content> Image </v-list-item-content>
          <v-list-item-content>
            {{ service.image }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="service.env_file">
          <v-list-item-content> Env File </v-list-item-content>
          <v-list-item-content>
            {{ service.env_file }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="service.depends_on">
          <v-list-item-content> Depends on </v-list-item-content>
          <v-list-item-content>
            {{ service.depends_on.join(", ") }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="service.restart">
          <v-list-item-content> Restart Policy </v-list-item-content>
          <v-list-item-content>
            {{ service.restart }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="service.read_only">
          <v-list-item-content> Read Only </v-list-item-content>
          <v-list-item-content>
            {{ service.read_only }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="Array.isArray(service.networks)">
          <v-list-item-content> Networks </v-list-item-content>
          <v-list-item-content>
            {{ service.networks.join(", ") }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-else-if="isObject(service.networks)">
          <v-list-item-content> Networks </v-list-item-content>
          <v-list-item-content
            v-for="network in networkRows"
            :key="network.name"
          >
            {{ network.name }}, {{ network.value }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="service.ports">
          <v-list-item-content> Ports </v-list-item-content>
          <v-list-item-content>
            {{ service.ports.join(", ") }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="service.volumes">
          <v-list-item-content> Volumes </v-list-item-content>
          <v-list-item-content>
            <v-card outlined tile>
              <v-simple-table class="secondary" dense>
                <thead>
                  <tr>
                    <th>Host</th>
                    <th>Container</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(volume, index) in volumeRows" :key="index">
                    <td>{{ volume.host }}</td>
                    <td>{{ volume.container }}</td>
                  </tr>
                </tbody>
              </v-simple-table>
            </v-card>
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="service.environment">
          <v-list-item-content> Environment </v-list-item-content>
          <v-list-item-content>
            <v-card outlined tile>
              <v-simple-table class="secondary" dense>
                <thead>
                  <tr>
                    <th>Variable</th>
                    <th>Value</th>
                  </tr>
                </thead>
                <tbody v-if="Array.isArray(service.environment)">
                  <tr
                    v-for="(entry, index) in environmentArrayRows"
                    :key="index"
                  >
                    <td>{{ entry.key }}</td>
                    <td>{{ entry.value }}</td>
                  </tr>
                </tbody>
                <tbody v-else-if="isObject(service.environment)">
                  <tr v-for="(value, key) in service.environment" :key="key">
                    <td>{{ key }}</td>
                    <td>{{ value }}</td>
                  </tr>
                </tbody>
              </v-simple-table>
            </v-card>
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="service.labels">
          <v-list-item-content> Labels </v-list-item-content>
          <v-list-item-content>
            <v-card outlined tile>
              <v-simple-table class="secondary" dense>
                <thead>
                  <tr>
                    <th>Label</th>
                    <th>Value</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(entry, index) in labelRows" :key="index">
                    <td>{{ entry.key }}</td>
                    <td>{{ entry.value }}</td>
                  </tr>
                </tbody>
              </v-simple-table>
            </v-card>
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="service.command">
          <v-list-item-content> Command </v-list-item-content>
          <v-list-item-content>
            <v-card outlined tile>
              <v-simple-table class="secondary" dense>
                <tbody>
                  <tr v-for="(command, index) in commandRows" :key="index">
                    <td>{{ command }}</td>
                  </tr>
                </tbody>
              </v-simple-table>
            </v-card>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-expansion-panel-content>
  </v-expansion-panel>
</template>

<script>
export default {
  props: {
    projectName: {
      type: String,
      required: true
    },
    serviceName: {
      type: String,
      required: true
    },
    service: {
      type: Object,
      required: true
    },
    status: {
      type: String,
      default: null
    }
  },
  computed: {
    commandRows() {
      return Array.isArray(this.service.command)
        ? this.service.command
        : [this.service.command];
    },
    environmentArrayRows() {
      return (this.service.environment || []).map(value =>
        this.splitKeyValue(value, "=")
      );
    },
    labelRows() {
      return (this.service.labels || []).map(value =>
        this.splitKeyValue(value, "=")
      );
    },
    networkRows() {
      return Object.entries(this.service.networks || {}).map(
        ([name, content]) => ({
          name,
          value: this.networkValue(content)
        })
      );
    },
    volumeRows() {
      return (this.service.volumes || []).map(value => {
        const [host, ...containerParts] = value.split(":");
        return {
          host,
          container: containerParts.join(":")
        };
      });
    }
  },
  methods: {
    emitAction(action) {
      this.$emit("service-action", {
        Project: this.projectName,
        Name: this.serviceName,
        Action: action
      });
    },
    isObject(val) {
      if (val === null) {
        return false;
      }
      return typeof val === "object";
    },
    networkValue(content) {
      if (!this.isObject(content)) {
        return content;
      }
      const [firstKey] = Object.keys(content);
      return firstKey ? content[firstKey] : "";
    },
    splitKeyValue(value, delimiter) {
      const index = value.indexOf(delimiter);
      if (index === -1) {
        return { key: value, value: "" };
      }
      return {
        key: value.slice(0, index),
        value: value.slice(index + delimiter.length)
      };
    }
  }
};
</script>
