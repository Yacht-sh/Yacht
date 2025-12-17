<template>
  <v-card class="elevation-12">
    <v-toolbar color="primary" dark flat>
      <v-toolbar-title>Two-Factor Authentication</v-toolbar-title>
    </v-toolbar>
    <v-card-text>
      <div v-if="!isEnabled">
        <p>2FA is currently disabled.</p>
        <v-btn color="primary" @click="setup2FA">Setup 2FA</v-btn>
      </div>
      <div v-else>
        <p>2FA is enabled.</p>
        <v-btn color="error" @click="disable2FA">Disable 2FA</v-btn>
      </div>

      <v-dialog v-model="setupDialog" max-width="500px">
        <v-card>
          <v-card-title>Scan QR Code</v-card-title>
          <v-card-text class="text-center">
            <img :src="qrCode" alt="QR Code" v-if="qrCode" style="max-width: 100%;"/>
            <v-text-field
              v-model="token"
              label="Verification Code"
              outlined
              class="mt-4"
            ></v-text-field>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text @click="setupDialog = false">Cancel</v-btn>
            <v-btn color="primary" @click="verifyAndEnable">Verify & Enable</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-card-text>
  </v-card>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      isEnabled: false, // This should be fetched from user profile
      setupDialog: false,
      qrCode: null,
      token: ''
    };
  },
  created() {
    this.checkStatus();
  },
  methods: {
    checkStatus() {
      axios.get('/api/auth/me').then(response => {
        this.isEnabled = response.data.is_2fa_enabled;
      });
    },
    setup2FA() {
      axios.post('/api/auth/2fa/generate').then(response => {
        this.qrCode = response.data.qr_code;
        this.setupDialog = true;
      }).catch(err => {
        this.$emit('notify', { message: 'Error generating 2FA: ' + err.response.data.detail, color: 'error' });
      });
    },
    verifyAndEnable() {
      axios.post('/api/auth/2fa/enable', { token: this.token }).then(() => {
        this.isEnabled = true;
        this.setupDialog = false;
        this.$emit('notify', { message: '2FA Enabled', color: 'success' });
      }).catch(err => {
        this.$emit('notify', { message: 'Verification failed: ' + err.response.data.detail, color: 'error' });
      });
    },
    disable2FA() {
      if (confirm('Are you sure you want to disable 2FA?')) {
        axios.post('/api/auth/2fa/disable').then(() => {
          this.isEnabled = false;
          this.$emit('notify', { message: '2FA Disabled', color: 'success' });
        });
      }
    }
  }
};
</script>
