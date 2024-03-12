<template>
  <q-separator v-if="separate"></q-separator>
  <q-item
    :clickable="clickable"
    tag="a"
    target="_blank"
    dense
    @click="$router.push({ path: link })"
  >
    <q-item-section avatar :style="{ 'margin-left': level * 2 + 'em' }">
      <q-icon v-if="icon" :name="icon" />
    </q-item-section>

    <q-item-section>
      <q-item-label>{{ title }}</q-item-label>
      <q-item-label caption>{{ caption }}</q-item-label>
    </q-item-section>
  </q-item>
</template>

<script setup lang="ts">
export interface EssentialLinkProps {
  title: string;
  caption?: string;
  link?: string;
  icon?: string;
  level: number;
  clickable?: boolean;
  separate?: boolean;
}
withDefaults(defineProps<EssentialLinkProps>(), {
  caption: '',
  link: '#',
  icon: '',
  clickable: true,
});
</script>
