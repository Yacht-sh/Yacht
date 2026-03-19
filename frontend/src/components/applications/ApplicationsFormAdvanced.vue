<template>
  <v-card color="primary" class="mt-5">
    <v-card-title>
      Advanced
    </v-card-title>
    <v-expansion-panels flat accordion multiple focusable>
      <v-expansion-panel>
        <v-expansion-panel-header color="foreground">
          <v-row no-gutters>
            <v-col cols="2">Command</v-col>
            <v-col cols="4" class="text--secondary">
              (Container Commands)
            </v-col>
          </v-row>
        </v-expansion-panel-header>
        <v-expansion-panel-content color="foreground" class="mt-5">
          <form>
            <transition-group
              name="slide"
              enter-active-class="animated fadeInLeft fast-anim"
              leave-active-class="animated fadeOutLeft fast-anim"
            >
              <v-row v-for="(item, index) in form.command" :key="index">
                <v-col>
                  <ValidationProvider
                    name="Command"
                    rules="required"
                    v-slot="{ errors, valid }"
                  >
                    <v-text-field
                      :label="'Command ' + index + ':'"
                      v-model="form.command[index]"
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
                    @click="removeCommand(index)"
                  >
                    <v-icon>mdi-minus</v-icon>
                  </v-btn>
                </v-col>
              </v-row>
            </transition-group>
            <v-row>
              <v-col cols="12" class="d-flex justify-end">
                <v-btn icon class="align-self-center" @click="addCommand">
                  <v-icon>mdi-plus</v-icon>
                </v-btn>
              </v-col>
            </v-row>
          </form>
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-header color="foreground">
          <v-row no-gutters>
            <v-col cols="2">Devices</v-col>
            <v-col cols="4" class="text--secondary">
              (Passthrough Devices)
            </v-col>
          </v-row>
        </v-expansion-panel-header>
        <v-expansion-panel-content color="foreground">
          <form>
            <transition-group
              name="slide"
              enter-active-class="animated fadeInLeft fast-anim"
              leave-active-class="animated fadeOutLeft fast-anim"
            >
              <v-row v-for="(item, index) in form.devices" :key="index">
                <v-col>
                  <ValidationProvider
                    name="Container"
                    rules="required"
                    v-slot="{ errors, valid }"
                  >
                    <v-text-field
                      label="Container"
                      v-model="item['container']"
                      :error-messages="errors"
                      :success="valid"
                      required
                    ></v-text-field>
                  </ValidationProvider>
                </v-col>
                <v-col>
                  <ValidationProvider
                    name="Host"
                    rules="required"
                    v-slot="{ errors, valid }"
                  >
                    <v-text-field
                      label="Host"
                      v-model="item['host']"
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
                    @click="removeDevices(index)"
                  >
                    <v-icon>mdi-minus</v-icon>
                  </v-btn>
                </v-col>
              </v-row>
            </transition-group>
            <v-row>
              <v-col cols="12" class="d-flex justify-end">
                <v-btn icon class="align-self-center" @click="addDevices">
                  <v-icon>mdi-plus</v-icon>
                </v-btn>
              </v-col>
            </v-row>
          </form>
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-header color="foreground">
          <v-row no-gutters>
            <v-col cols="2">Labels</v-col>
            <v-col cols="4" class="text--secondary">
              (Container Labels)
            </v-col>
          </v-row>
        </v-expansion-panel-header>
        <v-expansion-panel-content color="foreground">
          <form>
            <transition-group
              name="slide"
              enter-active-class="animated fadeInLeft fast-anim"
              leave-active-class="animated fadeOutLeft fast-anim"
            >
              <v-row v-for="(item, index) in form.labels" :key="index">
                <v-col>
                  <ValidationProvider
                    name="Label"
                    rules="required"
                    v-slot="{ errors, valid }"
                  >
                    <v-text-field
                      label="Label"
                      v-model="item['label']"
                      :error-messages="errors"
                      :success="valid"
                      required
                    ></v-text-field>
                  </ValidationProvider>
                </v-col>
                <v-col>
                  <ValidationProvider
                    name="Value"
                    rules=""
                    v-slot="{ errors, valid }"
                  >
                    <v-text-field
                      label="Value"
                      v-model="item['value']"
                      :error-messages="errors"
                      :success="valid"
                    ></v-text-field>
                  </ValidationProvider>
                </v-col>
                <v-col class="d-flex justify-end" cols="1">
                  <v-btn
                    icon
                    class="align-self-center"
                    @click="removeLabels(index)"
                  >
                    <v-icon>mdi-minus</v-icon>
                  </v-btn>
                </v-col>
              </v-row>
            </transition-group>
            <v-row>
              <v-col cols="12" class="d-flex justify-end">
                <v-btn icon class="align-self-center" @click="addLabels">
                  <v-icon>mdi-plus</v-icon>
                </v-btn>
              </v-col>
            </v-row>
          </form>
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-header color="foreground">
          <v-row no-gutters>
            <v-col cols="2">Sysctls</v-col>
            <v-col cols="4" class="text--secondary"> (Kernel Options) </v-col>
          </v-row>
        </v-expansion-panel-header>
        <v-expansion-panel-content color="foreground">
          <form>
            <transition-group
              name="slide"
              enter-active-class="animated fadeInLeft fast-anim"
              leave-active-class="animated fadeOutLeft fast-anim"
            >
              <v-row v-for="(item, index) in form.sysctls" :key="index">
                <v-col>
                  <ValidationProvider
                    name="Name"
                    rules="required"
                    v-slot="{ errors, valid }"
                  >
                    <v-text-field
                      label="Name"
                      v-model="item['name']"
                      :error-messages="errors"
                      :success="valid"
                      required
                    ></v-text-field>
                  </ValidationProvider>
                </v-col>
                <v-col>
                  <ValidationProvider
                    name="Value"
                    rules="required"
                    v-slot="{ errors, valid }"
                  >
                    <v-text-field
                      label="Value"
                      v-model="item['value']"
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
                    @click="removeSysctls(index)"
                  >
                    <v-icon>mdi-minus</v-icon>
                  </v-btn>
                </v-col>
              </v-row>
            </transition-group>
            <v-row>
              <v-col cols="12" class="d-flex justify-end">
                <v-btn icon class="align-self-center" @click="addSysctls">
                  <v-icon>mdi-plus</v-icon>
                </v-btn>
              </v-col>
            </v-row>
          </form>
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-header color="foreground">
          <v-row no-gutters>
            <v-col cols="2">Capabilities</v-col>
            <v-col cols="4" class="text--secondary">
              (Special Permissions/Capabilities)
            </v-col>
          </v-row></v-expansion-panel-header
        >
        <v-expansion-panel-content color="foreground">
          <form>
            <v-select
              v-model="form['cap_add']"
              :items="capOptions"
              label="Add Capabilities"
              multiple
              hide-selected
              clearable
              chips
              deletable-chips
            />
          </form>
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-header color="foreground">
          <v-row no-gutters>
            <v-col cols="2">Runtime</v-col>
            <v-col cols="4" class="text--secondary">
              (CPU/MEM Limits)
            </v-col>
          </v-row></v-expansion-panel-header
        >
        <v-expansion-panel-content color="foreground">
          <form>
            <v-text-field
              v-model="form['cpus']"
              label="CPU Cores:"
              clearable
            />
            <v-text-field
              v-model="form['mem_limit']"
              label="Memory Limit:"
              placeholder="(1000b,100k,10m,1g)"
              clearable
            />
          </form>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-card>
</template>

<script>
import { ValidationProvider } from "vee-validate";

export default {
  name: "ApplicationsFormAdvanced",
  components: {
    ValidationProvider
  },
  props: {
    form: {
      type: Object,
      required: true
    },
    capOptions: {
      type: Array,
      required: true
    }
  },
  methods: {
    addCommand() {
      this.form.command.push("");
    },
    removeCommand(index) {
      this.form.command.splice(index, 1);
    },
    addDevices() {
      this.form.devices.push({ container: "", host: "" });
    },
    removeDevices(index) {
      this.form.devices.splice(index, 1);
    },
    addLabels() {
      this.form.labels.push({ label: "", value: "" });
    },
    removeLabels(index) {
      this.form.labels.splice(index, 1);
    },
    addSysctls() {
      this.form.sysctls.push({ name: "", value: "" });
    },
    removeSysctls(index) {
      this.form.sysctls.splice(index, 1);
    }
  }
};
</script>
