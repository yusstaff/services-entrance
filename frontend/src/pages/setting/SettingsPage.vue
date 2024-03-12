<script setup lang="ts">
import unregister from 'src/api/auth/request/unregister';
import { useRouter } from 'vue-router';

const router = useRouter();

function onUnregister() {
  unregister().then(() => {
    router.push('/login');
  });
}
</script>

<template>
  <q-page class="bg-grey-6 row items-center justify-evenly">
    <q-btn icon="warning" color="red-5" class="q-pa-lg" @click="onUnregister">
      Admin Unregister
    </q-btn>
  </q-page>
</template>
