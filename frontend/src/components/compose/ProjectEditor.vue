<template lang="html">
  <div class="template-form component">
    <v-card>
      <!-- <v-fade-transition>
        <v-progress-linear
          indeterminate
          v-if="isLoading"
          color="primary"
          bottom
        />
      </v-fade-transition> -->
      <v-form>
        <div class="d-flex">
          <v-row>
            <v-col class="flex-grow-1 flex-shrink-0">
              <v-card-title v-if="!this.existing" class="mt-1">
                New Compose Template
              </v-card-title>
              <v-card-title v-if="this.existing" class="mt-1">
                Edit {{ this.form.name }} Project
              </v-card-title>
            </v-col>
            <v-col class="flex-grow-1 flex-shrink-0">
              <v-text-field
                v-if="!this.existing"
                class="mr-3"
                v-model="form.name"
                label="Template Name"
                required
              >
              </v-text-field>
            </v-col>
            <v-col class="flex-grow-0 flex-shrink-1">
              <v-btn @click="submitCompose()" color="primary" class="mr-2 mt-3"
                >submit</v-btn
              >
            </v-col>
          </v-row>
        </div>
        <editor
          v-model="form.content"
          @init="editorInit"
          lang="yaml"
          :theme="editorTheming()"
          :height="windowHeight"
          :width="windowWidth"
          class="editor"
        ></editor>
      </v-form>
    </v-card>
  </div>
</template>

<script>
import { mapActions, mapMutations } from "vuex";
import axios from "axios";
export default {
  data() {
    return {
      existing: false,
      form: {
        name: "",
        content: null
      },
      windowHeight: window.innerHeight - 205,
      windowWidth: window.innerWidth - 80
    };
  },
  components: {
    editor: require("vue2-ace-editor")
  },
  methods: {
    ...mapMutations({
      setErr: "snackbar/setErr"
    }),
    ...mapActions({
      readProject: "projects/readProject"
    }),
    editorInit() {
      require("brace/mode/yaml");
      require("brace/theme/twilight");
      require("brace/theme/textmate");
    },
    editorTheming() {
      if (this.$vuetify.theme.dark == false) {
        return "textmate";
      } else {
        return "twilight";
      }
    },
    submitCompose() {
      let url = `/api/compose/${this.form.name}/edit`;
      axios
        .post(url, this.form, {})
        .then(response => {
          this.$router.push({ path: `/projects/${response.data.name}` });
        })
        .catch(err => {
          this.setErr(err);
        });
    },
    async populateForm() {
      const projectName = this.$route.params.projectName;
      if (projectName != "_" && projectName != null) {
        const project = await this.readProject(projectName);
        this.form = {
          name: project.name || "",
          content: project.content || ""
        };
        this.existing = true;
      }
    }
  },
  async created() {
    await this.populateForm();
  }
};
</script>

<style lang="css">
.ace_gutter {
  z-index: 1;
}
.ace_gutter-active-line {
  z-index: 1;
}
.ace_editor {
  z-index: 1;
}
</style>
