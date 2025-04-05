<template>
  <v-card color="foreground" class="elevation-12 pb-8">
    <v-toolbar color="primary" dark flat>
      <v-toolbar-title>Server Template Variables</v-toolbar-title>
    </v-toolbar>
    <v-card-text>
      <ValidationObserver v-slot="{ invalid }">
        <form>
          <transition-group
            name="slide"
            enter-active-class="animated fadeInLeft fast-anim"
            leave-active-class="animated fadeOutLeft fast-anim"
          >
            <v-row v-for="(item, index) in form.templateVariables" :key="index">
              <v-col>
                <ValidationProvider
                  name="Variable"
                  rules="required"
                  v-slot="{ errors, valid }"
                >
                  <v-text-field
                    label="Variable"
                    v-model="item['variable']"
                    :error-messages="errors"
                    :success="valid"
                    required
                  ></v-text-field>
                </ValidationProvider>
              </v-col>
              <v-col>
                <ValidationProvider
                  name="Replacement"
                  rules="required"
                  v-slot="{ errors, valid }"
                >
                  <v-text-field
                    label="Replacement"
                    v-model="item['replacement']"
                    :error-messages="errors"
                    :success="valid"
                    required
                  ></v-text-field>
                </ValidationProvider>
              </v-col>
              <v-col class="d-flex justify-end" cols="1">
                <v-btn
                  icon
                  class="align-self-center"
                  @click="removeTemplateVariables(index)"
                >
                  <v-icon>mdi-minus</v-icon>
                </v-btn>
              </v-col>
            </v-row>
          </transition-group>
          <v-row>
            <v-col cols="12" class="d-flex justify-end">
              <v-btn
                icon
                class="align-self-center"
                @click="addTemplateVariables"
              >
                <v-icon>mdi-plus</v-icon>
              </v-btn>
            </v-col>
          </v-row>
          <v-btn
            class="float-right"
            @click="submitFormData()"
            color="primary"
            :disabled="invalid"
            >Save</v-btn
          >
        </form>
      </ValidationObserver>
    </v-card-text>
    <v-snackbar v-model="saved" bottom color="secondary">
      Saved
      <template v-slot:action="{ attrs }">
        <v-btn color="primary" text v-bind="attrs" @click="saved = false">
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </v-card>
</template>

<script>
import { ValidationObserver, ValidationProvider } from "vee-validate";
import { mapActions } from "vuex";
export default {
  components: {
    ValidationProvider,
    ValidationObserver
  },
  data() {
    return {
      form: {
        templateVariables: []
      },
      saved: false
    };
  },
  methods: {
    ...mapActions({
      writeTemplateVariables: "templates/writeTemplateVariables",
      readTemplateVariables: "templates/readTemplateVariables"
    }),
    addTemplateVariables() {
      this.form.templateVariables.push({ variable: "", replacement: "" });
    },
    removeTemplateVariables(index) {
      this.form.templateVariables.splice(index, 1);
    },
    submitFormData() {
      const payload = [...this.form.templateVariables];
      this.writeTemplateVariables(payload);
      this.saved = true;
    },
    async populateForm() {
      try {
        const t_vars = await this.readTemplateVariables();
        this.form = {
          templateVariables: t_vars || []
        };
      } catch (error) {
        console.error(error, error.response);
      }
    }
  },

  async created() {
    await this.populateForm();
    this.saved = false;
  }
};
</script>
