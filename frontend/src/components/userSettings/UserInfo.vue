<template>
  <v-card color="foreground" class="elevation-12 pb-8">
    <v-toolbar color="primary" dark flat>
      <v-toolbar-title>User Settings</v-toolbar-title>
      <v-spacer></v-spacer>
    </v-toolbar>
    <v-progress-linear indeterminate v-if="isLoading" />
    <v-card-text>
      This is where you can change settings related to your user account.
    </v-card-text>
    <h2 class="font-weight-bold ml-5">
      API Keys
      <v-dialog id="keyModal" v-model="keyDialog" max-width="500">
        <template v-slot:activator="{ on, attrs }">
          <v-btn color="primary" v-bind="attrs" v-on="on">
            <v-icon>mdi-plus</v-icon>
          </v-btn>
        </template>
        <v-card>
          <v-card-title class="primary">
            Generate API Key
          </v-card-title>
          <v-card-text>
            API Keys should be treated as a password and should only be provided
            to applications you trust. Once this box is closed you will be
            unable to retrive this key so be sure to copy it and test your
            application first.
            <br />
            <v-form>
              <v-text-field
                v-if="!newKey"
                v-model="keyForm.key_name"
                label="Name"
              >
              </v-text-field>
            </v-form>
            <v-btn v-if="!newKey" class="primary" @click="generate_api_key()">
              Generate Key</v-btn
            >
            <br v-if="newKey" />
            <span v-if="newKey" class="font-weight-bold">
              Generated API Key:</span
            >
            <v-btn
              @click="
                copykey();
                saved = true;
              "
              icon
              v-if="newKey"
              ><v-icon>mdi-clipboard-text-outline</v-icon></v-btn
            >
            <v-textarea
              @click="
                copykey();
                saved = true;
              "
              shaped
              outlined
              dense
              readonly
              no-resize
              v-if="newKey"
              v-model="newKey"
              id="newapikey"
            ></v-textarea>
            <v-snackbar v-model="saved" bottom color="secondary">
              Copied to clipboard
              <template v-slot:action="{ attrs }">
                <v-btn
                  color="primary"
                  text
                  v-bind="attrs"
                  @click="saved = false"
                >
                  Close
                </v-btn>
              </template>
            </v-snackbar>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn
              @click="
                keyDialog = false;
                newKey = '';
                keyForm.key_name = '';
              "
            >
              Close
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </h2>
    <v-data-table dense :headers="headers" :items="apiKeys" :items-per-page="5">
      <template v-slot:item.key_name="{ item }">
        <v-btn @click="revoke_api_key(item)" icon
          ><v-icon>mdi-trash-can-outline</v-icon></v-btn
        >
        <span class="ml-2"> {{ item.key_name }} </span>
      </template>
      <template v-slot:item.created_at="{ item }">
        <span class="CreatedAt"> {{ item.created_at | formatDate }} </span>
      </template>
    </v-data-table>
  </v-card>
</template>

<script>
import axios from "axios";
export default {
  data() {
    return {
      importFile: null,
      isLoading: false,
      keyDialog: false,
      newKey: null,
      keyForm: {
        key_name: ""
      },
      saved: false,
      apiKeys: [],
      headers: [
        {
          text: "Name",
          value: "key_name",
          sortable: true,
          align: "start"
        },
        {
          text: "Created Time",
          value: "created_at",
          sortable: true
        }
      ]
    };
  },
  methods: {
    async get_api_keys() {
      let url = "/api/auth/api/keys";
      await axios
        .get(url)
        .then(resp => {
          for (let key in resp.data) {
            if (!(resp.data[key] in this.apiKeys)) {
              this.apiKeys.push(resp.data[key]);
            }
          }
        })
        .catch(() => {
          //pass
        });
    },
    copykey() {
      var copytext = document.getElementById("newapikey");
      copytext.select();
      copytext.focus();
      copytext.select();
      document.execCommand("Copy");
    },
    generate_api_key() {
      const payload = { ...this.keyForm };
      let url = "/api/auth/api/keys/new";
      axios.post(url, payload).then(resp => {
        this.newKey = resp.data.token;
        this.apiKeys.push(resp.data);
      });
    },
    revoke_api_key(key) {
      this.isLoading = true;
      axios
        .get(`/api/auth/api/keys/${key.id}`)
        .then(() => {
          let idx = this.apiKeys.findIndex(x => x.id === key.id);
          this.apiKeys.splice(idx, 1);
        })
        .finally(() => {
          this.isLoading = false;
        });
    }
  },
  async created() {
    await this.get_api_keys();
  }
};
</script>
