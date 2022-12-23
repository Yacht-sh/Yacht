<template>
  <v-card class="foreground" elevation="0">
    <v-row>
      <v-col sm="12" md="6">
        <v-card
          :class="{
            'mx-4 foreground': $vuetify.breakpoint.smAndDown,
            'ml-4 flex-grow-1 flex-shrink-0 foreground':
              $vuetify.breakpoint.mdAndUp
          }"
        >
          <v-card-title class="primary">
            {{ app.Config.Image.split(":")[0] }}
          </v-card-title>
          <v-simple-table class="foreground">
            <template v-slot:default>
              <tbody>
                <tr>
                  <td class="text-left">Name</td>
                  <td>{{ app.name }}</td>
                </tr>
                <tr>
                  <td>Image</td>
                  <td>{{ app.Config.Image.split(":")[0] }}</td>
                </tr>
                <tr>
                  <td>ID</td>
                  <td>{{ app.short_id }}</td>
                </tr>
                <tr>
                  <td>Status</td>
                  <td>{{ app.State.Status }}</td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-card>
      </v-col>
      <v-col>
        <v-card
          :class="{
            'mx-4 foreground': $vuetify.breakpoint.smAndDown,
            'mr-4 flex-grow-0 flex-shrink-1 foreground':
              $vuetify.breakpoint.mdAndUp
          }"
        >
          <v-card-title class="primary"> Networking </v-card-title>
          <v-tabs
            background-color="tabs"
            :show-arrows="$vuetify.breakpoint.smAndDown"
            show-arrows-on-hover
            v-model="network_tab"
          >
            <v-tab> Ports </v-tab>
            <v-tab> Networks </v-tab>
          </v-tabs>
          <v-tabs-items class="foreground" v-model="network_tab">
            <v-tab-item>
              <v-card-text
                v-if="app.State.Status != 'running'"
                class="foreground text-center px-5 py-5"
              >
                Start the app to view ports
              </v-card-text>
              <v-simple-table v-else class="foreground px-0 text-center">
                <template v-slot:default>
                  <thead>
                    <tr>
                      <th
                        v-for="(label, index) in network_labels"
                        :key="index"
                        class="text-center"
                      >
                        {{ label }}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="(port, index) in convPorts(app.ports)"
                      :key="index"
                    >
                      <td v-if="network_labels.includes('Label')">
                        {{
                          app.Config.Labels[`local.yacht.port.${port.hport}`]
                        }}
                      </td>
                      <td>{{ port.cport }}</td>
                      <td>{{ port.hip }}</td>
                      <td>
                        <v-chip
                          v-if="port.hip == '0.0.0.0'"
                          color="primary"
                          label
                          :href="'http://' + host_ip + ':' + port.hport"
                          target="_blank"
                          ><v-icon small class="mr-1">mdi-link-variant</v-icon
                          >{{ port.hport }}</v-chip
                        ><v-chip
                          v-else
                          color="primary"
                          label
                          :href="'http://' + port.hip + ':' + port.hport"
                          target="_blank"
                          ><v-icon small class="mr-1">mdi-link-variant</v-icon
                          >{{ port.hport }}</v-chip
                        >
                      </td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-tab-item>
            <v-tab-item>
              <v-simple-table class="foreground px-0 text-center">
                <template v-slot:default>
                  <thead>
                    <tr>
                      <th class="text-center">Name</th>
                      <th
                        class="text-center"
                        v-if="app.State.Status == 'running'"
                      >
                        IP
                      </th>
                      <th
                        class="text-center"
                        v-if="app.State.Status == 'running'"
                      >
                        Gateway
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="(network, index) in app.NetworkSettings.Networks"
                      :key="index"
                    >
                      <td
                        @click="
                          $router.push({
                            name: 'Network Details',
                            params: { networkid: network.NetworkID }
                          })
                        "
                      >
                        <a>{{ index }}</a>
                      </td>
                      <td v-if="app.State.Status == 'running'">
                        {{ network.IPAddress }}
                      </td>
                      <td v-if="app.State.Status == 'running'">
                        {{ network.Gateway }}
                      </td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-tab-item>
          </v-tabs-items>
        </v-card>
      </v-col>
      <v-col sm="12" md="6">
        <v-card
          v-if="app.Config.Env"
          :class="{
            'mx-4 foreground': $vuetify.breakpoint.smAndDown,
            'ml-4 flex-grow-1 flex-shrink-0 foreground':
              $vuetify.breakpoint.mdAndUp
          }"
        >
          <v-card-title class="primary"> Environment </v-card-title>
          <v-simple-table
            style="max-height: 500px;overflow-y: auto;"
            class="foreground px-0 text-center"
          >
            <template v-slot:default>
              <thead>
                <tr>
                  <th class="text-center">Variable</th>
                  <th class="text-center">Value</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(env, index) in splitEnv(app.Config.Env)"
                  :key="index"
                >
                  <td>{{ env[0] }}</td>
                  <td>{{ env[1] }}</td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-card>
      </v-col>
      <v-col sm="12" md="6">
        <v-card
          :class="{
            'mx-4 foreground': $vuetify.breakpoint.smAndDown,
            'mr-4 flex-grow-0 flex-shrink-1 foreground':
              $vuetify.breakpoint.mdAndUp
          }"
        >
          <v-card-title class="primary"> Storage </v-card-title>
          <v-tabs background-color="tabs" show-arrows v-model="storage_tab">
            <v-tab v-for="(mount, index) in app.Mounts" :key="index">
              {{ mount.Destination }}
            </v-tab>
          </v-tabs>
          <v-tabs-items
            class="foreground"
            v-model="storage_tab"
            :show-arrows="$vuetify.breakpoint.smAndDown"
            show-arrows-on-hover
          >
            <v-tab-item v-for="(mount, index) in app.Mounts" :key="index">
              <v-simple-table id="storage_table" class="foreground">
                <template v-slot:default>
                  <tbody>
                    <tr v-for="(property, pindex) in mount" :key="pindex">
                      <td v-if="property">
                        {{ pindex }}
                      </td>
                      <td v-if="property">
                        {{ property }}
                      </td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-tab-item>
          </v-tabs-items>
        </v-card>
      </v-col>
      <v-col cols="12">
        <v-card
          :class="{
            'mx-4 foreground': $vuetify.breakpoint.smAndDown,
            'mx-4 flex-grow-0 flex-shrink-1 foreground':
              $vuetify.breakpoint.mdAndUp
          }"
        >
          <v-card-title class="primary">
            Labels
          </v-card-title>
          <v-simple-table class="foreground px-0 text-center">
            <template v-slot:default>
              <thead>
                <tr>
                  <th class="text-center">Label</th>
                  <th class="text-center">Value</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(label, index) in Object.entries(app.Config.Labels)"
                  :key="index"
                >
                  <td>{{ label[0] }}</td>
                  <td>{{ label[1] }}</td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-card>
      </v-col>
      <v-col
        md="6"
        xs="12"
        v-if="
          app.Args.length ||
            (app.HostConfig.Devices && app.HostConfig.Devices.length) ||
            app.HostConfig.CapAdd
        "
      >
        <v-card
          :class="{
            'mx-4': $vuetify.breakpoint.smAndDown,
            'mr-4 flex-grow-0 flex-shrink-1': $vuetify.breakpoint.mdAndUp
          }"
        >
          <v-card-title class="primary"> Advanced </v-card-title>
          <v-tabs background-color="tabs" v-model="advanced_tab">
            <v-tab v-if="Array.isArray(app.Args) && app.Args.length"
              >Command</v-tab
            >
            <v-tab
              v-if="
                app.HostConfig.Devices &&
                  Array.isArray(app.HostConfig.Devices) &&
                  app.HostConfig.Devices.length
              "
              >Devices</v-tab
            >
            <v-tab v-if="app.HostConfig.Sysctls">Sysctls</v-tab>
            <v-tab v-if="app.HostConfig.CapAdd">Capabilities</v-tab>
          </v-tabs>
          <v-tabs-items class="foreground" v-model="advanced_tab">
            <v-tab-item v-if="Array.isArray(app.Args) && app.Args.length">
              <v-list class="foreground">
                <v-list-item v-for="(arg, index) in app.Args" :key="index">
                  <v-list-item-content>
                    {{ arg }}
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-tab-item>
            <v-tab-item
              v-if="
                app.HostConfig.Devices &&
                  Array.isArray(app.HostConfig.Devices) &&
                  app.HostConfig.Devices.length
              "
            >
              {{ app.HostConfig.Devices }}
            </v-tab-item>
            <v-tab-item v-if="app.HostConfig.Sysctls">
              <v-simple-table class="foreground">
                <template v-slot:default>
                  <thead>
                    <tr>
                      <th>Sysctl</th>
                      <th>Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="(sysctl, index) in Object.keys(
                        app.HostConfig.Sysctls
                      )"
                      :key="index"
                    >
                      <td>
                        {{ sysctl }}
                      </td>
                      <td>
                        {{ app.HostConfig.Sysctls[sysctl] }}
                      </td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-tab-item>
            <v-tab-item v-if="app.HostConfig.CapAdd">
              <v-list class="foreground">
                <v-list-item
                  v-for="(item, index) in app.HostConfig.CapAdd"
                  :key="index"
                >
                  <v-list-item-content>
                    {{ item }}
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-tab-item>
          </v-tabs-items>
        </v-card>
      </v-col>
    </v-row>
  </v-card>
</template>

<script>
export default {
  data() {
    return {
      host_ip: location.hostname,
      network_tab: 0,
      storage_tab: 0,
      advanced_tab: 0
    };
  },
  props: ["app"],
  computed: {
    network_labels() {
      for (var port in this.convPorts(this.app.ports)) {
        if (
          this.app.Config.Labels[
            `local.yacht.port.${this.convPorts(this.app.ports)[port].hport}`
          ]
        ) {
          var label_found = true;
          break;
        }
      }
      if (label_found == true) {
        return ["Label", "Container Port", "Host IP", "Host Port"];
      } else {
        return ["Container Port", "Host IP", "Host Port"];
      }
    }
  },
  methods: {
    convPorts(data) {
      let o = [];
      for (var k in data) {
        if (data[k]) {
          o = o.concat(
            data[k].map(function(x) {
              return { cport: k, hip: x.HostIp, hport: x.HostPort };
            })
          );
        }
      }
      return o;
    },
    refresh() {
      const appName = this.$route.params.appName;
      this.readApp(appName);
      this.readAppProcesses(appName);
    },
    splitEnv(data) {
      const env = [];
      for (let index = 0; index < data.length; index++) {
        let _split_pos = data[index].indexOf("=");
        let _name = data[index].substr(
          0,
          _split_pos >= 0 ? _split_pos : data[index].length
        );
        let _value = _split_pos >= 0 ? data[index].substr(_split_pos + 1) : "";
        env.push([_name, _value]);
      }
      return env;
    }
  }
};
</script>

<style scoped>
.AppLabel {
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}
</style>
