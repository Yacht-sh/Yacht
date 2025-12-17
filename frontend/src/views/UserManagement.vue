<template>
  <v-card color="foreground" class="d-flex mx-auto page">
    <v-container fluid class="component">
      <Nav class="mb-3" />
      <v-card color="foreground" tile>
        <v-toolbar color="primary" dark flat>
          <v-toolbar-title>User Management</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn icon @click="loadUsers">
            <v-icon>mdi-refresh</v-icon>
          </v-btn>
          <v-btn color="secondary" @click="openCreateDialog">
            <v-icon left>mdi-plus</v-icon> Add User
          </v-btn>
        </v-toolbar>

        <v-data-table
          :headers="headers"
          :items="users"
          :loading="loading"
          class="elevation-1"
        >
          <template v-slot:item.is_superuser="{ item }">
            <v-icon v-if="item.is_superuser" color="success">mdi-check</v-icon>
            <v-icon v-else color="error">mdi-close</v-icon>
          </template>
          <template v-slot:item.is_active="{ item }">
            <v-icon v-if="item.is_active" color="success">mdi-check</v-icon>
            <v-icon v-else color="error">mdi-close</v-icon>
          </template>
           <template v-slot:item.is_2fa_enabled="{ item }">
            <v-icon v-if="item.is_2fa_enabled" color="success">mdi-shield-check</v-icon>
            <v-icon v-else color="grey">mdi-shield-off</v-icon>
          </template>
          <template v-slot:item.actions="{ item }">
            <v-icon small class="mr-2" @click="editUser(item)">mdi-pencil</v-icon>
            <v-icon small @click="deleteUser(item)">mdi-delete</v-icon>
          </template>
        </v-data-table>
      </v-card>

      <!-- User Dialog -->
      <v-dialog v-model="dialog" max-width="600px">
        <v-card>
          <v-card-title>
            <span class="headline">{{ formTitle }}</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12">
                  <v-text-field v-model="editedItem.username" label="Username (Email)" required></v-text-field>
                </v-col>
                <v-col cols="12">
                  <v-text-field v-model="editedItem.password" label="Password" type="password" :required="editedIndex === -1"></v-text-field>
                </v-col>
                <v-col cols="12" sm="6">
                   <v-checkbox v-model="editedItem.is_active" label="Active"></v-checkbox>
                </v-col>
                <v-col cols="12" sm="6">
                   <v-checkbox v-model="editedItem.is_superuser" label="Administrator"></v-checkbox>
                </v-col>

                <v-col cols="12">
                  <h3>Permissions</h3>
                </v-col>
                <v-col cols="6">
                  <v-checkbox v-model="editedItem.perm_start" label="Start Containers"></v-checkbox>
                </v-col>
                <v-col cols="6">
                  <v-checkbox v-model="editedItem.perm_stop" label="Stop Containers"></v-checkbox>
                </v-col>
                <v-col cols="6">
                  <v-checkbox v-model="editedItem.perm_restart" label="Restart Containers"></v-checkbox>
                </v-col>
                <v-col cols="6">
                  <v-checkbox v-model="editedItem.perm_delete" label="Remove Containers"></v-checkbox>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" text @click="close">Cancel</v-btn>
            <v-btn color="blue darken-1" text @click="save">Save</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
        {{ snackbar.message }}
      </v-snackbar>
    </v-container>
  </v-card>
</template>

<script>
import axios from 'axios';
import Nav from "../components/Nav";

export default {
  components: {
    Nav
  },
  data: () => ({
    dialog: false,
    loading: false,
    headers: [
      { text: 'Username', value: 'username' },
      { text: 'Admin', value: 'is_superuser' },
      { text: 'Active', value: 'is_active' },
      { text: '2FA', value: 'is_2fa_enabled' },
      { text: 'Actions', value: 'actions', sortable: false },
    ],
    users: [],
    editedIndex: -1,
    editedItem: {
      username: '',
      password: '',
      is_active: true,
      is_superuser: false,
      perm_start: false,
      perm_stop: false,
      perm_restart: false,
      perm_delete: false,
    },
    defaultItem: {
      username: '',
      password: '',
      is_active: true,
      is_superuser: false,
      perm_start: false,
      perm_stop: false,
      perm_restart: false,
      perm_delete: false,
    },
    snackbar: {
        show: false,
        message: '',
        color: 'info'
    }
  }),

  computed: {
    formTitle () {
      return this.editedIndex === -1 ? 'New User' : 'Edit User'
    },
  },

  watch: {
    dialog (val) {
      val || this.close()
    },
  },

  created () {
    this.loadUsers()
  },

  methods: {
    loadUsers () {
      this.loading = true
      // Need to implement backend endpoint for getting all users.
      // Currently backend/api/routers/users.py has get_user (me) but not list all for admin.
      // Wait, crud.get_users exists but is not exposed in router explicitly?
      // Let's check backend/api/routers/users.py again.
      // It doesn't seem to have a GET /users endpoint. I need to add it.
      // For now I will mock or fail, but I must add the endpoint in backend.

      axios.get('/api/auth/users').then(response => {
          this.users = response.data;
          this.loading = false
      }).catch(err => {
          console.log("Error loading users or endpoint missing", err);
          this.loading = false
      })
    },

    editUser (item) {
      this.editedIndex = this.users.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialog = true
    },

    deleteUser (item) {
      if(confirm('Are you sure you want to delete this user?')) {
          axios.delete(`/api/auth/users/${item.id}`).then(() => {
              this.loadUsers();
              this.notify('User deleted', 'success');
          });
      }
    },

    close () {
      this.dialog = false
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.editedIndex = -1
      })
    },

    save () {
      if (this.editedIndex > -1) {
        // Edit
        axios.put(`/api/auth/users/${this.editedItem.id}`, this.editedItem).then(() => {
            this.loadUsers();
            this.notify('User updated', 'success');
            this.close();
        }).catch(err => {
            this.notify('Error updating user: ' + err.response.data.detail, 'error');
        });
      } else {
        // Create
        axios.post('/api/auth/create', this.editedItem).then(() => {
            this.loadUsers();
            this.notify('User created', 'success');
            this.close();
        }).catch(err => {
            this.notify('Error creating user: ' + err.response.data.detail, 'error');
        });
      }
    },

    notify(msg, color) {
        this.snackbar.message = msg;
        this.snackbar.color = color;
        this.snackbar.show = true;
    },

    openCreateDialog() {
        this.editedItem = Object.assign({}, this.defaultItem);
        this.editedIndex = -1;
        this.dialog = true;
    }
  },
}
</script>
