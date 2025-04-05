<template lang="html">
  <div class="apps-form component">
    <h1>
      Deploy {{ form.name }}
      <v-btn
        v-if="!this.$route.params.appId && !this.$route.params.appName"
        tile
        :to="{ name: 'Deploy from Template' }"
        class="primary float-right"
      >
        <v-icon>mdi-plus</v-icon> From Template
      </v-btn>
    </h1>
    <v-card v-if="notes" color="blue-grey darken-2" class="mb-2">
      <v-card-title>Note:</v-card-title>
      <v-card-text v-html="notes"></v-card-text>
    </v-card>
    <v-stepper class="foreground" v-model="deployStep" alt-labels non-linear>
      <v-fade-transition>
        <v-progress-linear
          indeterminate
          v-if="isLoading"
          color="primary"
          bottom
        />
      </v-fade-transition>
      <v-stepper-header>
        <v-stepper-step
          step="1"
          editable
          edit-icon="mdi-check"
          :complete="deployStep > 1"
        >
          General
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step
          step="2"
          editable
          edit-icon="mdi-check"
          :complete="deployStep > 2"
        >
          Networking
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step
          step="3"
          editable
          edit-icon="mdi-check"
          :complete="deployStep > 3"
        >
          Volumes
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step
          step="4"
          editable
          edit-icon="mdi-check"
          :complete="deployStep > 4"
        >
          Environment
        </v-stepper-step>
      </v-stepper-header>

      <v-stepper-items>
        <v-stepper-content step="1">
          <ValidationObserver ref="obs1" v-slot="{ invalid }">
            <form>
              <ValidationProvider
                name="Name"
                rules="required"
                v-slot="{ errors, valid }"
              >
                <v-text-field
                  label="Name"
                  placeholder="My Container"
                  v-model="form.name"
                  :error-messages="errors"
                  :success="valid"
                  required
                ></v-text-field>
              </ValidationProvider>
              <ValidationProvider
                name="Image"
                rules="required"
                v-slot="{ errors, valid }"
              >
                <v-text-field
                  label="Image"
                  placeholder="image:my-image"
                  v-model="form.image"
                  :error-messages="errors"
                  :success="valid"
                  required
                ></v-text-field>
              </ValidationProvider>
              <ValidationProvider
                name="Restart Policy"
                rules="required"
                v-slot="{ errors, valid }"
              >
                <v-select
                  :items="['always', 'on-failure', 'unless-stopped', 'none']"
                  label="Restart Policy"
                  v-model="form['restart_policy']"
                  :error-messages="errors"
                  :success="valid"
                  required
                ></v-select>
              </ValidationProvider>
            </form>
            <v-btn
              color="primary"
              @click="deployStep = 2"
              :disabled="invalid"
              class="float-right"
            >
              Continue
            </v-btn>
          </ValidationObserver>
        </v-stepper-content>

        <v-stepper-content step="2">
          <ValidationObserver ref="obs2" v-slot="{ invalid }">
            <form>
              <v-row>
                <v-col>
                  <v-select
                    :items="networks"
                    label="Network"
                    clearable
                    v-model="form.network"
                    :disabled="
                      form.network_mode !== undefined &&
                        form.network_mode !== ''
                    "
                  />
                </v-col>
                <v-col>
                  <v-select
                    :items="network_modes"
                    label="Network Mode"
                    clearable
                    v-model="form.network_mode"
                    :disabled="
                      form.network !== undefined && form.network !== ''
                    "
                  />
                </v-col>
              </v-row>
              <transition-group
                v-if="form.network_mode !== 'host' && form.network !== 'host'"
                name="slide"
                enter-active-class="animated fadeInLeft fast-anim"
                leave-active-class="animated fadeOutLeft fast-anim"
                >item
                <v-row v-for="(item, index) in form.ports" :key="index">
                  <v-col>
                    <ValidationProvider
                      name="Label"
                      rules=""
                      v-slot="{ errors, valid }"
                    >
                      <v-text-field
                        type="string"
                        label="Label"
                        placeholder="webui"
                        v-model="item['label']"
                        :error-messages="errors"
                        :success="valid"
                      ></v-text-field>
                    </ValidationProvider>
                  </v-col>
                  <v-col>
                    <ValidationProvider
                      name="Host"
                      rules=""
                      v-slot="{ errors, valid }"
                    >
                      <v-text-field
                        type="number"
                        label="Host"
                        placeholder="80"
                        min="0"
                        max="65535"
                        v-model="item['hport']"
                        :error-messages="errors"
                        :success="valid"
                      ></v-text-field>
                    </ValidationProvider>
                  </v-col>
                  <v-col>
                    <ValidationProvider
                      name="Container"
                      rules="required"
                      v-slot="{ errors, valid }"
                    >
                      <v-text-field
                        type="number"
                        label="Container"
                        placeholder="80"
                        min="0"
                        max="65535"
                        v-model="item['cport']"
                        :error-messages="errors"
                        :success="valid"
                        required
                      ></v-text-field>
                    </ValidationProvider>
                  </v-col>
                  <v-col>
                    <ValidationProvider
                      name="Protocol"
                      rules="required"
                      v-slot="{ errors, valid }"
                    >
                      <v-select
                        :items="['tcp', 'udp']"
                        label="Protocol"
                        v-model="item['proto']"
                        :error-messages="errors"
                        :success="valid"
                        required
                      ></v-select>
                    </ValidationProvider>
                  </v-col>

                  <v-col class="d-flex justify-end" cols="1">
                    <v-btn
                      icon
                      class="align-self-center"
                      @click="removePort(index)"
                    >
                      <v-icon>mdi-minus</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </transition-group>
              <v-row>
                <v-col cols="12" class="d-flex justify-end">
                  <v-btn
                    v-if="
                      form.network_mode !== 'host' && form.network !== 'host'
                    "
                    icon
                    class="align-self-center"
                    @click="addPort"
                  >
                    <v-icon>mdi-plus</v-icon>
                  </v-btn>
                </v-col>
              </v-row>
            </form>
            <v-btn
              color="primary"
              @click="deployStep = 3"
              :disabled="invalid"
              class="float-right"
            >
              Continue
            </v-btn>
            <v-btn
              color="secondary"
              @click="deployStep = 1"
              class="mx-2 float-right primary--text"
            >
              Back
            </v-btn>
          </ValidationObserver>
        </v-stepper-content>

        <v-stepper-content step="3">
          <ValidationObserver ref="obs3" v-slot="{ invalid }">
            <form>
              <transition-group
                name="slide"
                enter-active-class="animated fadeInLeft fast-anim"
                leave-active-class="animated fadeOutLeft fast-anim"
              >
                <v-row v-for="(item, index) in form.volumes" :key="index">
                  <v-col>
                    <ValidationProvider
                      name="Host"
                      rules="required"
                      v-slot="{ errors, valid }"
                    >
                      <v-text-field
                        label="Host"
                        placeholder="/yacht/image/share"
                        v-model="item['bind']"
                        :error-messages="errors"
                        :success="valid"
                        required
                      ></v-text-field>
                    </ValidationProvider>
                  </v-col>
                  <v-col>
                    <ValidationProvider
                      name="Container"
                      rules="required"
                      v-slot="{ errors, valid }"
                    >
                      <v-text-field
                        label="Container"
                        placeholder="/share"
                        v-model="item['container']"
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
                      @click="removeVolume(index)"
                    >
                      <v-icon>mdi-minus</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </transition-group>
              <v-row>
                <v-col cols="12" class="d-flex justify-end">
                  <v-btn icon class="align-self-center" @click="addVolume">
                    <v-icon>mdi-plus</v-icon>
                  </v-btn>
                </v-col>
              </v-row>
            </form>
            <v-btn
              color="primary"
              @click="deployStep = 4"
              :disabled="invalid"
              class="float-right"
            >
              Continue
            </v-btn>
            <v-btn
              color="secondary"
              @click="deployStep = 2"
              class="mx-2 float-right primary--text"
            >
              Back
            </v-btn>
          </ValidationObserver>
        </v-stepper-content>

        <v-stepper-content step="4">
          <ValidationObserver ref="obs4" v-slot="{ invalid }">
            <form>
              <transition-group
                name="slide"
                enter-active-class="animated fadeInLeft fast-anim"
                leave-active-class="animated fadeOutLeft fast-anim"
              >
                <v-row v-for="(item, index) in form.env" :key="index">
                  <v-col>
                    <ValidationProvider
                      name="Name"
                      rules="required"
                      v-slot="{ errors, valid }"
                    >
                      <v-text-field
                        :label="item['label']"
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
                        v-model="item['default']"
                        :error-messages="errors"
                        :success="valid"
                        :messages="item.description"
                        required
                      ></v-text-field>
                    </ValidationProvider>
                  </v-col>
                  <v-col class="d-flex justify-end" cols="1">
                    <v-btn
                      icon
                      class="align-self-center"
                      @click="removeEnv(index)"
                    >
                      <v-icon>mdi-minus</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </transition-group>
              <v-row>
                <v-col cols="12" class="d-flex justify-end">
                  <v-btn icon class="align-self-center" @click="addEnv">
                    <v-icon>mdi-plus</v-icon>
                  </v-btn>
                </v-col>
              </v-row>
            </form>
            <v-btn
              v-if="form.edit == true"
              color="primary"
              @click="editDialog = true"
              :disabled="invalid"
              class="float-right"
            >
              <div v-if="isLoading">
                Deploying
                <v-progress-circular
                  indeterminate
                  color="white"
                  size="15"
                  width="2"
                />
              </div>
              <div v-else>Deploy</div>
            </v-btn>
            <v-btn
              v-else
              color="primary"
              @click="nextStep(4)"
              :disabled="invalid"
              class="float-right"
            >
              <div v-if="isLoading">
                Deploying
                <v-progress-circular
                  indeterminate
                  color="white"
                  size="15"
                  width="2"
                />
              </div>
              <div v-else>Deploy</div>
            </v-btn>
            <v-btn
              color="secondary"
              @click="deployStep = 3"
              class="mx-2 float-right primary--text"
            >
              Back
            </v-btn>
          </ValidationObserver>
        </v-stepper-content>
      </v-stepper-items>
    </v-stepper>
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
                :items="cap_options"
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
    <v-dialog v-model="editDialog" max-width="290">
      <v-card>
        <v-card-title class="headline" style="word-break: break-all;">
          Are you sure you want to edit this container?
        </v-card-title>
        <v-card-text>
          This will remove the currently running container and deploy a new one
          with the settings in this form. Please make sure your container data
          is persistant or backed up.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="editDialog = false">
            Cancel
          </v-btn>
          <v-btn
            text
            color="yellow"
            @click="
              nextStep(4);
              editDialog = false;
            "
          >
            Edit
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from "axios";
import { mapActions, mapMutations, mapState } from "vuex";
import { ValidationObserver, ValidationProvider } from "vee-validate";

export default {
  components: {
    ValidationProvider,
    ValidationObserver
  },
  data() {
    return {
      deployStep: 1,
      deploySteps: 4,
      notes: "",
      networks: [],
      volumes: [],
      editDialog: false,
      form: {
        name: "",
        image: "",
        restart_policy: "",
        network: undefined,
        network_mode: undefined,
        ports: [],
        volumes: [],
        env: [],
        command: [],
        devices: [],
        labels: [],
        sysctls: [],
        cap_add: [],
        cpus: undefined,
        mem_limit: undefined
      },
      network_modes: ["bridge", "none", "host"],
      isLoading: false,
      cap_options: [
        "SYS_MODULE",
        "SYS_RAWIO",
        "SYS_PACCT",
        "SYS_ADMIN",
        "SYS_NICE",
        "SYS_RESOURCE",
        "SYS_TIME",
        "SYS_TTY_CONFIG",
        "AUDIT_CONTROL",
        "MAC_ADMIN",
        "MAC_OVERRIDE",
        "NET_ADMIN",
        "SYSLOG",
        "DAC_READ_SEARCH",
        "LINUX_IMMUTABLE",
        "NET_BROADCAST",
        "IPC_LOCK",
        "IPC_OWNER",
        "SYS_PTRACE",
        "SYS_BOOT",
        "LEASE",
        "WAKE_ALARM",
        "BLOCK_SUSPEND"
      ]
    };
  },
  calculated: {
    ...mapState("networks", ["networks"]),
    ...mapState("volumes", ["volumes"])
  },
  methods: {
    ...mapActions({
      readTemplateApp: "templates/readTemplateApp",
      readNetworks: "networks/_readNetworks",
      readApp: "apps/readApp"
    }),
    ...mapMutations({
      setErr: "snackbar/setErr"
    }),
    addCommand() {
      this.form.command.push("");
    },
    removeCommand(index) {
      this.form.command.splice(index, 1);
    },
    addPort() {
      this.form.ports.push({ hport: "", cport: "", proto: "tcp" });
    },
    removePort(index) {
      this.form.ports.splice(index, 1);
    },
    addVolume() {
      this.form.volumes.push({ container: "", bind: "" });
    },
    removeVolume(index) {
      this.form.volumes.splice(index, 1);
    },
    addEnv() {
      this.form.env.push({ label: "", default: "" });
    },
    removeEnv(index) {
      this.form.env.splice(index, 1);
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
    },
    addCap_add() {
      this.form.cap_add.push("");
    },
    removeCap_add(index) {
      this.form.cap_add.splice(index, 1);
    },
    transform_ports(ports, app) {
      let portlist = [];
      for (let port in ports) {
        let _port = port.split("/") || "";
        var cport = _port[0] || "";
        if (ports[port]) {
          var hport = ports[port][0].HostPort || "";
        } else {
          continue;
        }
        var proto = _port[1] || "";
        var label = app.Config.Labels[`local.yacht.port.${hport}`] || "";
        let port_entry = {
          cport: cport,
          hport: hport,
          proto: proto,
          label: label
        };
        portlist.push(port_entry);
      }
      return portlist;
    },
    transform_volumes(volumes) {
      let volumelist = [];
      for (let volume in volumes) {
        let container = volumes[volume].Destination || "";
        let bind = volumes[volume].Source || "";
        let volume_entry = {
          bind: bind,
          container: container
        };
        volumelist.push(volume_entry);
      }
      return volumelist;
    },
    transform_env(envs) {
      let envlist = [];
      for (let env in envs) {
        let _env = envs[env].split("=");
        let name = _env[0];
        let value = _env[1];
        let env_entry = {
          label: name,
          name: name,
          default: value
        };
        envlist.push(env_entry);
      }
      return envlist;
    },
    transform_labels(labels) {
      let labellist = [];
      for (let _label in labels) {
        let label = _label;
        let value = labels[label];
        let label_entry = {
          label: label,
          value: value
        };
        labellist.push(label_entry);
      }
      return labellist;
    },
    transform_cpus(_cpus) {
      let cpus = _cpus / 10 ** 9;
      if (cpus != 0) {
        return cpus;
      }
      return undefined;
    },
    transform_mem_limit(bytes) {
      if (bytes != 0) {
        var i = Math.floor(Math.log(bytes) / Math.log(1024)),
          sizes = ["b", "k", "m", "g"];

        return (bytes / Math.pow(1024, i)).toFixed(2) * 1 + sizes[i];
      } else {
        return undefined;
      }
    },
    nextStep(n) {
      if (n === this.deploySteps) {
        // this.deployStep = 1;
        this.submitFormData();
      } else {
        this.deployStep = n + 1;
      }
    },
    submitFormData() {
      const payload = { ...this.form };
      this.isLoading = true;
      const url = `/api/apps/deploy`;
      axios
        .post(url, payload)
        .then(() => {
          this.isLoading = false;
          this.$router.push({ name: "View Applications" });
        })
        .catch(err => {
          this.isLoading = false;
          this.deployStep = 1;
          this.setErr(err);
        });
    },
    async populateNetworks() {
      const networks = await this.readNetworks();
      for (var network in networks) {
        this.networks.push(networks[network]["Name"]);
      }
    },
    async populateForm() {
      if (this.$route.params.appId) {
        const appId = this.$route.params.appId;
        if (appId != null) {
          try {
            const app = await this.readTemplateApp(appId);
            this.form = {
              name: app.name || "",
              image: app.image || "",
              restart_policy: app.restart_policy || "",
              command: app.command || [],
              network: app.network,
              network_mode: app.network_mode,
              ports: app.ports || [],
              volumes: app.volumes || [],
              env: app.env || [],
              devices: app.devices || [],
              labels: app.labels || [],
              sysctls: app.sysctls || [],
              cap_add: app.cap_add || [],
              cpus: app.cpus,
              mem_limit: app.mem_limit
            };
            this.notes = app.notes || null;
          } catch (error) {
            console.error(error, error.response);
            this.setErr(error);
          }
        }
      } else if (this.$route.params.appName) {
        const appName = this.$route.params.appName;
        const app = await this.readApp(appName);
        this.form = {
          name: app.name || "",
          image: app.Config.Image || "",
          restart_policy: app.HostConfig.RestartPolicy.Name || "",
          network: Object.keys(app.NetworkSettings.Networks)[0] || "",
          ports: this.transform_ports(app.ports, app) || [],
          volumes: this.transform_volumes(app.Mounts) || [],
          env: this.transform_env(app.Config.Env) || [],
          devices: [],
          labels: this.transform_labels(app.Config.Labels) || [],
          sysctls: this.transform_labels(app.HostConfig.Sysctls),
          cap_add: app.HostConfig.CapAdd || [],
          cpus: this.transform_cpus(app.HostConfig.NanoCpus),
          mem_limit: this.transform_mem_limit(app.HostConfig.Memory),
          edit: true,
          id: app.Id
        };
      }
    }
  },
  async created() {
    await this.populateForm();
    await this.populateNetworks();
  }
};
</script>

<style lang="css" scoped></style>
