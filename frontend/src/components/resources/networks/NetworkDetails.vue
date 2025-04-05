<template>
  <div class="page">
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
        <v-menu close-on-click close-on-content-click offset-y>
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon size="small" v-bind="attrs" v-on="on">
              <v-icon>mdi-chevron-down</v-icon>
            </v-btn>
          </template>
          <v-list color="foreground" dense>
            <v-list-item
              @click="
                deleteNetwork(network.Name);
                router.push({ name: 'Networks' });
              "
            >
              <v-list-item-icon
                ><v-icon>mdi-trash-can-outline</v-icon></v-list-item-icon
              >
              <v-list-item-title>Delete Network</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
        {{ network.Name }}
      </v-card-title>
      <v-card-subtitle>
        <v-chip
          outlined
          small
          color="orange lighten-1"
          class="align-center mt-1"
          label
          v-if="network.inUse == false"
          >Unused</v-chip
        >
        {{ network.Id }}
      </v-card-subtitle>
    </v-card>
    <v-card color="foreground" class="mt-2">
      <v-card-title>
        Network Information
      </v-card-title>
      <v-list color="foreground" dense>
        <v-list-item>
          <v-list-item-content>
            Name
          </v-list-item-content>
          <v-list-item-content>
            {{ network.Name }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            ID
          </v-list-item-content>
          <v-list-item-content>
            {{ network.Id }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            Driver
          </v-list-item-content>
          <v-list-item-content>
            {{ network.Driver }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            Scope
          </v-list-item-content>
          <v-list-item-content>
            {{ network.Scope }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            Attachable
          </v-list-item-content>
          <v-list-item-content>
            {{ network.Attachable }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            Internal
          </v-list-item-content>
          <v-list-item-content>
            {{ network.Internal }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            IPV6 Enabled
          </v-list-item-content>
          <v-list-item-content>
            {{ network.EnableIPv6 }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            Created
          </v-list-item-content>
          <v-list-item-content>
            {{ network.Created | formatDate }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="Object.keys(network.Labels).length > 1">
          <v-list-item-content>
            Labels
          </v-list-item-content>
          <v-list-item-content>
            <v-card outlined tile>
              <v-simple-table class="foreground" dense>
                <tbody>
                  <tr
                    v-for="(value, key, index) in network.Labels"
                    :key="index"
                  >
                    <td style="min-width:20%;" class="align-self-center">
                      {{ key }}
                    </td>
                    <td
                      class="text-truncate align-self-center"
                      style="width:100%"
                    >
                      {{ value }}
                    </td>
                  </tr>
                </tbody>
              </v-simple-table>
            </v-card>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>

    <v-card color="foreground" class="mt-2">
      <v-card-title>
        Network Details
      </v-card-title>
      <v-list color="foreground" dense>
        <v-list-item>
          <v-list-item-content style="max-width: 30%">
            IPV4 Subnet
          </v-list-item-content>
          <v-list-item-content v-if="network.IPAM.Config[0]">
            {{ network.IPAM.Config[0].Subnet || "-" }}
          </v-list-item-content>
          <v-list-item-content v-else>
            -
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content style="max-width: 30%">
            IPV4 Gateway
          </v-list-item-content>
          <v-list-item-content v-if="network.IPAM.Config[0]">
            {{ network.IPAM.Config[0].Gateway || "-" }}
          </v-list-item-content>
          <v-list-item-content v-else>
            -
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content style="max-width: 30%">
            IPV6 Subnet
          </v-list-item-content>
          <v-list-item-content>
            -
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content style="max-width: 30%">
            IPv6 Gateway
          </v-list-item-content>
          <v-list-item-content>
            -
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="Object.keys(network.Options).length > 0">
          <v-list-item-content style="max-width: 30%">
            Options
          </v-list-item-content>
          <v-list-item-content>
            <v-card outlined tile>
              <v-simple-table dense>
                <tbody>
                  <tr
                    v-for="(value, key, index) in network.Options"
                    :key="index"
                  >
                    <td style="min-width:20%;" class="align-self-center">
                      {{ key }}
                    </td>
                    <td
                      class="text-truncate align-self-center"
                      style="width:100%"
                    >
                      {{ value }}
                    </td>
                  </tr>
                </tbody>
              </v-simple-table>
            </v-card>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>

    <v-card color="foreground" class="mt-2">
      <v-card-title>
        Attached Containers
      </v-card-title>
      <v-data-table
        style="max-width: 99%;"
        class="mx-auto network-datatable foreground"
        :headers="headers"
        :items="conv2array(network.Containers)"
        @click:row="handleRowClick"
      >
        <template slot="no-data">
          <div>
            No Networks available.
          </div>
        </template>
        <template v-slot:item.Name="{ item }">
          <div class="d-flex">
            <span class="align-streatch text-truncate nametext mt-2">
              {{ item.Name }}</span
            >
          </div>
        </template>
        <template v-slot:item.ipv4="{ item }">
          <div class="projectcell">
            <span class="d-inline-block text-truncate idtext">
              {{ item.IPv4Address || "-" }}
            </span>
          </div>
        </template>
        <template v-slot:item.ipv6="{ item }" class="idcell">
          <div class="idcell">
            <span class="d-inline-block text-truncate idtext">
              {{ item.IPv6Address || "-" }}
            </span>
          </div>
        </template>
        <template v-slot:item.macaddress="{ item }" class="idcell">
          <div class="idcell">
            <span class="d-inline-block text-truncate idtext">
              {{ item.MacAddress }}
            </span>
          </div>
        </template>
        <template v-slot:item.ID="{ item }">
          <span
            class="d-inline-block text-truncate flex-grow-1 flex-shrink-0"
            >{{ item.EndpointID }}</span
          >
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script>
import { mapActions, mapGetters, mapState } from "vuex";

export default {
  data() {
    return {
      headers: [
        {
          text: "Name",
          value: "Name",
          sortable: true
        },
        {
          text: "IPv4",
          value: "ipv4",
          sortable: true
        },
        {
          text: "IPv6",
          value: "ipv6",
          sortable: true
        },
        {
          text: "MacAddress",
          value: "macaddress",
          sortable: true
        },
        {
          text: "ID",
          value: "ID",
          sortable: true
        }
      ]
    };
  },
  computed: {
    ...mapState("networks", ["network", "network", "isLoading"]),
    ...mapGetters({
      getNetworkById: "networks/getNetworkById"
    }),
    network() {
      const networkid = this.$route.params.networkid;
      return this.getNetworkById(networkid);
    }
  },
  methods: {
    ...mapActions({
      readNetwork: "networks/readNetwork",
      deleteNetwork: "networks/deleteNetwork"
    }),
    conv2array(containers) {
      var container_list = Object.values(containers);

      return container_list;
    },
    handleRowClick(app) {
      this.$router.push({ path: `/apps/${app.Name}/info` });
    }
  },
  created() {
    const networkid = this.$route.params.networkid;
    this.readNetwork(networkid);
  }
};
</script>

<style scoped></style>
