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
            <v-list-item @click="deleteVolume(volume.Name)">
              <v-list-item-icon
                ><v-icon>mdi-trash-can-outline</v-icon></v-list-item-icon
              >
              <v-list-item-title>Delete Volume</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
        {{ volume.Name }}
      </v-card-title>
      <v-card-subtitle>
        <v-chip
          outlined
          small
          color="orange lighten-1"
          class="align-center mt-1"
          label
          v-if="volume.inUse == false"
          >Unused</v-chip
        >
      </v-card-subtitle>
    </v-card>
    <v-card color="foreground" class="mt-2">
      <v-card-title>
        Volume Details
      </v-card-title>
      <v-list color="foreground" dense>
        <v-list-item>
          <v-list-item-content>
            Name
          </v-list-item-content>
          <v-list-item-content>
            {{ volume.Name }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            Driver
          </v-list-item-content>
          <v-list-item-content>
            {{ volume.Driver }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            Mountpoint
          </v-list-item-content>
          <v-list-item-content>
            {{ volume.Mountpoint }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            Scope
          </v-list-item-content>
          <v-list-item-content>
            {{ volume.Scope }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            Created
          </v-list-item-content>
          <v-list-item-content>
            {{ volume.CreatedAt | formatDate }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="volume.Labels">
          <v-list-item-content style="max-width:20%">
            Labels
          </v-list-item-content>
          <v-list-item-content>
            <v-card outlined tile>
              <v-simple-table dense>
                <tbody>
                  <tr v-for="(value, key, index) in volume.Labels" :key="index">
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
  </div>
</template>

<script>
import { mapActions, mapGetters, mapState } from "vuex";

export default {
  data() {
    return {};
  },
  computed: {
    ...mapState("volumes", ["volume", "volumes", "isLoading"]),
    ...mapGetters({
      getVolumeByName: "volumes/getVolumeByName"
    }),
    volume() {
      const volumeName = this.$route.params.volumeName;
      return this.getVolumeByName(volumeName);
    }
  },
  methods: {
    ...mapActions({
      readVolume: "volumes/readVolume",
      deleteVolume: "volumes/deleteVolume"
    })
  },
  created() {
    const volumeName = this.$route.params.volumeName;
    this.readVolume(volumeName);
  }
};
</script>

<style scoped></style>
