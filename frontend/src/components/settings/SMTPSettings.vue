<template>
  <v-card class="elevation-12">
    <v-toolbar color="primary" dark flat>
      <v-toolbar-title>SMTP Settings</v-toolbar-title>
    </v-toolbar>
    <v-card-text>
      <v-form ref="form" v-model="valid">
        <v-text-field
          v-model="settings.server"
          label="SMTP Server"
          required
          outlined
        ></v-text-field>
        <v-text-field
          v-model="settings.port"
          label="Port"
          type="number"
          required
          outlined
        ></v-text-field>
        <v-text-field
          v-model="settings.username"
          label="Username"
          outlined
        ></v-text-field>
        <v-text-field
          v-model="settings.password"
          label="Password"
          type="password"
          outlined
        ></v-text-field>
        <v-text-field
          v-model="settings.sender_email"
          label="Sender Email"
          required
          outlined
        ></v-text-field>
        <v-checkbox
          v-model="settings.use_tls"
          label="Use TLS"
        ></v-checkbox>
      </v-form>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="secondary" @click="testEmail">Send Test Email</v-btn>
      <v-btn color="primary" @click="saveSettings">Save</v-btn>
    </v-card-actions>

    <v-dialog v-model="testDialog" max-width="500px">
      <v-card>
        <v-card-title>Send Test Email</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="testRecipient"
            label="Recipient Email"
            outlined
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="testDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="sendTest">Send</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      valid: false,
      settings: {
        server: '',
        port: 587,
        username: '',
        password: '',
        sender_email: '',
        use_tls: true
      },
      testDialog: false,
      testRecipient: ''
    };
  },
  created() {
    this.fetchSettings();
  },
  methods: {
    fetchSettings() {
      axios.get('/api/settings/smtp/').then(response => {
        this.settings = response.data;
      }).catch(err => {
        console.error(err);
      });
    },
    saveSettings() {
      axios.post('/api/settings/smtp/', this.settings).then(() => {
        this.$emit('notify', { message: 'SMTP Settings Saved', color: 'success' });
      }).catch(err => {
        this.$emit('notify', { message: 'Error saving settings: ' + err.response.data.detail, color: 'error' });
      });
    },
    testEmail() {
      this.testDialog = true;
    },
    sendTest() {
      axios.post('/api/settings/smtp/test', { recipient: this.testRecipient }).then(() => {
        this.$emit('notify', { message: 'Test email sent', color: 'success' });
        this.testDialog = false;
      }).catch(err => {
        this.$emit('notify', { message: 'Error sending email: ' + err.response.data.detail, color: 'error' });
      });
    }
  }
};
</script>
