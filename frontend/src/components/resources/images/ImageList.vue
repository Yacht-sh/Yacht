<template lang="html">
  <div class="images-list component" style="max-width: 90%">
    <v-card color="foreground">
      <v-fade-transition>
        <v-progress-linear
          indeterminate
          v-if="isLoading"
          color="primary"
          bottom
        />
      </v-fade-transition>
      <v-card-title class="primary font-weight-bold">
        Images
        <v-dialog v-model="pullDialog" max-width="290">
          <template v-slot:activator="{ on, attrs }">
            <v-btn class="ml-2" color="secondary" v-bind="attrs" v-on="on">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </template>
          <v-card color="foreground">
            <v-card-title class="headline" style="word-break: break-all;">
              Pull Image
            </v-card-title>
            <v-card-text>
              Pull an image.
            </v-card-text>
            <form ref="form" @submit.prevent="submit">
              <v-text-field
                label="Image"
                class="mx-5"
                placeholder="yacht-sh/yacht:latest"
                required
                v-model="form.image"
              >
              </v-text-field>
            </form>
            <v-card-actions>
              <v-spacer />
              <v-btn text @click="pullDialog = false">
                Cancel
              </v-btn>
              <v-btn
                text
                color="primary"
                @click="
                  submit();
                  pullDialog = false;
                "
              >
                Pull
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
        <v-spacer />
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
        ></v-text-field>
      </v-card-title>

      <v-data-table
        style="max-width: 99%;"
        class="mx-auto image-datatable foreground"
        :headers="headers"
        :items="images"
        :items-per-page="25"
        :footer-props="{
          'items-per-page-options': [15, 25, 50, -1]
        }"
        :search="search"
        @click:row="handleRowClick"
      >
        <template slot="no-data">
          <div>
            No Images available.
          </div>
        </template>
        <template v-slot:item.RepoTags="{ item }">
          <div class="d-flex">
            <span class="align-streatch text-truncate nametext mt-2">{{
              item.RepoTags[0] || handleDigests(item) || ""
            }}</span>
            <v-spacer />

            <v-chip
              outlined
              small
              color="orange lighten-1"
              class="align-center mt-1"
              label
              v-if="item.inUse == false"
              >Unused</v-chip
            >
            <v-menu close-on-click close-on-content-click offset-y>
              <template v-slot:activator="{ on, attrs }">
                <v-btn
                  icon
                  class="align-streatch"
                  size="small"
                  v-bind="attrs"
                  v-on="on"
                >
                  <v-icon>mdi-dots-horizontal</v-icon>
                </v-btn>
              </template>
              <v-list color="foreground" dense>
                <v-list-item @click="imageDetails(item.Id)">
                  <v-list-item-icon>
                    <v-icon>mdi-eye</v-icon>
                  </v-list-item-icon>
                  <v-list-item-title>View</v-list-item-title>
                </v-list-item>
                <v-list-item
                  v-if="item.RepoTags[0]"
                  @click="updateImage(item.Id)"
                >
                  <v-list-item-icon>
                    <v-icon>mdi-update</v-icon>
                  </v-list-item-icon>
                  <v-list-item-title>Pull</v-list-item-title>
                </v-list-item>
                <v-divider />
                <v-list-item
                  @click="
                    selectedImage = item;
                    deleteDialog = true;
                  "
                >
                  <v-list-item-icon>
                    <v-icon>mdi-delete</v-icon>
                  </v-list-item-icon>
                  <v-list-item-title>Delete</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
        </template>
        <template v-slot:item.Id="{ item }" class="idcell">
          <div class="idcell">
            <span class="d-inline-block text-truncate idtext">
              {{ item.Id }}
            </span>
          </div>
        </template>
        <template v-slot:item.Created="{ item }">
          <span
            class="d-inline-block text-truncate flex-grow-1 flex-shrink-0"
            >{{ item.Created | formatDate }}</span
          >
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-if="selectedImage" v-model="deleteDialog" max-width="290">
      <v-card>
        <v-card-title class="headline" style="word-break: break-all;">
          Delete the image?
        </v-card-title>
        <v-card-text>
          Are you sure you want to permanently delete the image?<br />
          This action cannot be revoked.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="deleteDialog = false">
            Cancel
          </v-btn>
          <v-btn
            text
            color="error"
            @click="
              deleteImage(selectedImage.Id);
              deleteDialog = false;
            "
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapActions, mapState } from "vuex";
export default {
  data() {
    return {
      selectedImage: null,
      deleteDialog: false,
      form: {
        image: ""
      },
      pullDialog: false,
      search: "",
      headers: [
        {
          text: "Tag",
          value: "RepoTags",
          sortable: true
        },
        {
          text: "ID",
          value: "Id",
          sortable: true
        },
        {
          text: "Created",
          value: "Created",
          sortable: true
        }
      ]
    };
  },
  methods: {
    ...mapActions({
      readImages: "images/readImages",
      updateImage: "images/updateImage",
      deleteImage: "images/deleteImage",
      writeImage: "images/writeImage"
    }),
    handleRowClick(item) {
      this.$router.push({ path: `/resources/images/${item.Id}` });
    },
    imageDetails(imageid) {
      this.$router.push({ path: `/resources/images/${imageid}` });
    },
    submit() {
      const data = this.form;
      this.writeImage(data);
    },
    handleDigests(item) {
      if (item.RepoDigests[0]) {
        let _digest = item.RepoDigests[0].split("@")[0];
        return _digest;
      } else {
        let _shortid = item.Id.split(":")[1].substring(0, 10);
        return _shortid;
      }
    }
  },
  computed: {
    ...mapState("images", ["images", "isLoading"])
  },
  mounted() {
    this.readImages();
  }
};
</script>

<style lang="css" scoped>
.nametext {
  max-width: 20vw;
}
.idtext {
  max-width: 30vw;
}
.image-datatable {
  overflow-x: hidden;
}
</style>
