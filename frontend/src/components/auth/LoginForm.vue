<template>
  <ValidationObserver ref="obs1" v-slot="{ invalid, validated }">
    <v-container class="fill-height" fluid>
      <img class="mx-auto mt-12 main-logo" alt="Vue logo" :src="themeLogo()" />
      <v-row align="center" justify="center" class="mt-12">
        <v-col cols="12" sm="8" md="4">
          <v-card color="foreground" class="elevation-12 pb-8">
            <v-toolbar color="primary" dark flat>
              <v-toolbar-title>Login</v-toolbar-title>
              <v-spacer></v-spacer>
            </v-toolbar>
            <v-card-text>
              <div v-if="!requires2FA">
                <v-form @keyup.native.enter="onSubmit()">
                  <ValidationProvider
                    name="username"
                    rules="required"
                    v-slot="{ errors, valid }"
                  >
                    <v-text-field
                      label="Email"
                      v-model="username"
                      :error-messages="errors"
                      :success="valid"
                      required
                    />
                  </ValidationProvider>

                  <ValidationProvider
                    name="password"
                    rules="required"
                    v-slot="{ errors, valid }"
                  >
                    <v-text-field
                      label="Password"
                      v-model="password"
                      :error-messages="errors"
                      :success="valid"
                      :type="show ? 'text' : 'password'"
                      :append-icon="show ? 'mdi-eye' : 'mdi-eye-off'"
                      clearable
                      required
                      @click:append="show = !show"
                    />
                  </ValidationProvider>
                  <v-btn
                    class="float-right"
                    @click="onSubmit()"
                    color="primary"
                    :disabled="invalid || !validated"
                    >Login</v-btn
                  >
                </v-form>
              </div>
              <div v-else>
                <p>Please enter your 2FA code.</p>
                <v-form @keyup.native.enter="onSubmit2FA()">
                  <v-text-field
                    label="2FA Code"
                    v-model="otpToken"
                    required
                    outlined
                    autofocus
                  />
                  <v-btn class="float-right" @click="onSubmit2FA()" color="primary">Verify</v-btn>
                </v-form>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <v-snackbar v-model="errorSnackbar" color="error">
        {{ errorMessage }}
      </v-snackbar>
    </v-container>
  </ValidationObserver>
</template>

<script>
import lightLogo from "@/assets/logo-light.svg";
import darkLogo from "@/assets/logo.svg";
import { ValidationObserver, ValidationProvider } from "vee-validate";
import { mapActions } from "vuex";
import { themeLogo } from "../../config.js";
import axios from 'axios';

export default {
  components: {
    ValidationProvider,
    ValidationObserver
  },
  data() {
    return {
      username: "",
      password: "",
      show: false,
      requires2FA: false,
      otpToken: '',
      errorSnackbar: false,
      errorMessage: ''
    };
  },
  methods: {
    ...mapActions({
      loginAction: "auth/AUTH_REQUEST",
      authCheck: "auth/AUTH_CHECK"
    }),

    async onSubmit() {
      // We will handle the login request manually here to intercept 2FA requirement
      try {
        const response = await axios.post('/api/auth/login_cookie', {
          username: this.username,
          password: this.password
        });

        if (response.data.login === '2fa_required') {
          this.requires2FA = true;
        } else if (response.data.login === 'successful') {
           // Dispatch action to update state, but we already called API
           // So we might need to adjust the Vuex action or just commit directly
           // Assuming AUTH_REQUEST does the API call usually.
           // Let's manually trigger the success path in Vuex or reload
           this.$store.commit("auth/AUTH_SUCCESS", response.data);
           this.$router.push("/");
        }
      } catch (err) {
        this.errorMessage = err.response ? err.response.data.detail : "Login failed";
        this.errorSnackbar = true;
        this.$store.commit("auth/AUTH_ERROR");
      }
    },

    async onSubmit2FA() {
       try {
        const response = await axios.post('/api/auth/login_cookie', {
          username: this.username,
          password: this.password,
          otp_token: this.otpToken
        });

        if (response.data.login === 'successful') {
           this.$store.commit("auth/AUTH_SUCCESS", response.data);
           this.$router.push("/");
        }
      } catch (err) {
        this.errorMessage = err.response ? err.response.data.detail : "Verification failed";
        this.errorSnackbar = true;
      }
    },

    themeLogo() {
      if (themeLogo) {
        return themeLogo;
      } else if (this.$vuetify.theme.dark == true) {
        return darkLogo;
      } else if (this.$vuetify.theme.dark == false) {
        return lightLogo;
      }
    }
  },
  mounted() {
    this.authCheck();
  }
};
</script>

<style lang="css" scope>
.main-logo {
  max-width: 107px;
  max-height: 72px;
}
</style>
