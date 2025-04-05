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
              v-if="image.RepoTags[0]"
              @click="updateImage(image.Id)"
            >
              <v-list-item-icon><v-icon>mdi-update</v-icon></v-list-item-icon>
              <v-list-item-title>Pull Image</v-list-item-title>
            </v-list-item>
            <v-list-item @click="deleteImage(image.Id)">
              <v-list-item-icon
                ><v-icon>mdi-trash-can-outline</v-icon></v-list-item-icon
              >
              <v-list-item-title>Delete Image</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
        {{ image.Id }}
      </v-card-title>
      <v-card-subtitle>
        <v-chip
          outlined
          small
          color="orange lighten-1"
          class="align-center mt-1"
          label
          v-if="image.inUse == false"
          >Unused</v-chip
        >
        {{ image.RepoTags[0] || image.RepoDigests[0] }}
      </v-card-subtitle>
    </v-card>
    <v-card color="foreground" class="mt-2">
      <v-card-title>
        Image Details
      </v-card-title>
      <v-list color="foreground" dense>
        <v-list-item>
          <v-list-item-content>
            Tag
          </v-list-item-content>
          <v-list-item-content>
            {{ image.RepoTags[0] }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            Architecture
          </v-list-item-content>
          <v-list-item-content>
            {{ image.Architecture }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            Platform
          </v-list-item-content>
          <v-list-item-content>
            {{ image.Os }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            Architecture
          </v-list-item-content>
          <v-list-item-content>
            {{ image.Architecture }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            Created
          </v-list-item-content>
          <v-list-item-content>
            {{ image.Created | formatDate }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            Size
          </v-list-item-content>
          <v-list-item-content>
            {{ formatBytes(image.Size) }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            VirtualSize
          </v-list-item-content>
          <v-list-item-content>
            {{ formatBytes(image.VirtualSize) }}
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>

    <v-card class="mt-2" color="foreground">
      <v-card-title>
        Container Details
      </v-card-title>
      <v-list dense color="foreground">
        <v-list-item v-if="getCMD(image.ContainerConfig.Cmd)">
          <v-list-item-content style="max-width:20%">
            Command
          </v-list-item-content>
          <v-list-item-content>
            {{ getCMD(image.ContainerConfig.Cmd) }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="image.ContainerConfig.Entrypoint">
          <v-list-item-content style="max-width:20%">
            Entrypoint
          </v-list-item-content>
          <v-list-item-content>
            {{ image.ContainerConfig.Entrypoint[0] }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="image.ContainerConfig.ExposedPorts">
          <v-list-item-content style="max-width:20%">
            Ports
          </v-list-item-content>
          <v-list-item-content
            v-for="(port, index) in Object.keys(
              image.ContainerConfig.ExposedPorts
            )"
            :key="index"
          >
            {{ port }}
          </v-list-item-content>
        </v-list-item>
        <v-list-item v-if="image.ContainerConfig.Labels">
          <v-list-item-content style="max-width:20%">
            Labels
          </v-list-item-content>
          <v-list-item-content>
            <v-card outlined tile>
              <v-simple-table dense>
                <tbody>
                  <tr
                    v-for="(value, key, index) in image.ContainerConfig.Labels"
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
        <v-list-item v-if="image.ContainerConfig.Env">
          <v-list-item-content style="max-width:20%">
            ENV
          </v-list-item-content>
          <v-list-item-content>
            <v-card outlined tile>
              <v-simple-table>
                <tbody>
                  <tr
                    v-for="(key, index) in image.ContainerConfig.Env"
                    :key="index"
                  >
                    <td
                      style="width:100%;"
                      class="align-self-center text-truncate"
                    >
                      {{ key }}
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
    ...mapState("images", ["image", "images", "isLoading"]),
    ...mapGetters({
      getImageById: "images/getImageById"
    }),
    image() {
      const imageid = this.$route.params.imageid;
      return this.getImageById(imageid);
    }
  },
  methods: {
    ...mapActions({
      readImage: "images/readImage",
      updateImage: "images/updateImage",
      deleteImage: "images/deleteImage"
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
    getCMD(cmd) {
      for (var entry in cmd) {
        if (cmd[entry].includes("CMD")) {
          return cmd[entry];
        } else return null;
      }
    }
  },
  created() {
    const imageid = this.$route.params.imageid;
    this.readImage(imageid);
  }
};
</script>

<style scoped></style>
