<script setup lang="ts">
import login from 'api/auth/request/login';
import refresh from 'api/auth/request/refresh';
import { Notify } from 'quasar';
import { useCsrfStore } from 'stores/csrf';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const csrf = useCsrfStore();

function navigateToPreviousPage() {
  if (window.history.state.back === null) {
    router.push('/');
  } else {
    router.back();
  }
}

if (csrf.refreshToken()) {
  refresh().then(() => {
    Notify.create({
      message: 'Refresh',
      color: 'green',
      position: 'top',
    });
    navigateToPreviousPage();
  });
}

const username = ref<string>('');
const password = ref<string>('');

function onLogin() {
  login({ username: username.value, password: password.value }).then(() => {
    navigateToPreviousPage();
  });
}
</script>

<template>
  <q-layout view="lHh Lpr lFf" class="flex flex-center bg-grey-4">
    <q-header elevated>
      <q-toolbar>
        <q-toolbar-title> Services Entrance </q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-card style="width: 350px">
      <q-card-section class="bg-blue-4 text-bold q-pa-md">
        Administrator
      </q-card-section>
      <q-separator></q-separator>
      <q-card-section class="bg-blue-1 q-pa-sm row">
        <div class="flex flex-center col-3">Username</div>
        <q-input
          v-model="username"
          outlined
          bg-color="white"
          class="col-8"
        ></q-input>
      </q-card-section>
      <q-card-section class="bg-blue-1 q-pa-sm row">
        <div class="flex flex-center col-3">Password</div>
        <q-input
          v-model="password"
          type="password"
          outlined
          bg-color="white"
          class="col-8"
        ></q-input>
      </q-card-section>
      <q-separator></q-separator>
      <q-card-actions align="center" class="bg-blue-1 q-pa-md">
        <q-btn class="bg-blue-4 col-5" @click="onLogin"> Login </q-btn>
      </q-card-actions>
    </q-card>
  </q-layout>
</template>
