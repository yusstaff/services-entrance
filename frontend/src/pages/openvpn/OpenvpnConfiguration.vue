<script setup lang="ts">
import { ref } from 'vue';
import Subnet from 'api/openvpn/data/subnet';
import getSubnets from 'api/openvpn/request/get_subnets';
import modifySubnets from 'api/openvpn/request/modify_subnets';
import { Notify } from 'quasar';

const OPENVPN_AS_ADMIN_PAGE_PORT = 943;

const subnets = ref<Subnet[]>([]);

function fetchSubnets() {
  getSubnets().then((res) => {
    subnets.value = res.data.subnets;
  });
}
fetchSubnets();

function onOpenAdminPage() {
  const hostname = window.location.hostname;

  const adminUrl = `https://${hostname}:${OPENVPN_AS_ADMIN_PAGE_PORT}`;

  window.open(adminUrl, '_blank');
}

function onAddSubnet() {
  subnets.value.push({
    address: '',
    cidr: 20,
  });
}

function onSaveSubnets() {
  modifySubnets({ subnets: subnets.value }).then((res) => {
    subnets.value = res.data.subnets;
    Notify.create({
      message: 'Save succeeded',
      color: 'green',
      position: 'top',
    });
  });
}

function onDeleteSubnet(idx: number) {
  subnets.value.splice(idx, 1);
}
</script>

<template>
  <q-card class="q-flex">
    <q-card-section class="row" style="font-size: 20px">
      <div class="text-bold text-center flex flex-center">Openvpn</div>

      <q-space></q-space>

      <q-btn
        icon="settings_applications"
        class="bg-blue-5 col-2"
        style="text-transform: none !important"
        @click="onOpenAdminPage"
      >
        Go To Openvpn
      </q-btn>
      <div style="width: 20px"></div>
      <q-btn
        icon="add_box"
        class="bg-green-5 col-2"
        style="text-transform: none !important"
        @click="onAddSubnet"
      >
        Add Subnet
      </q-btn>
      <div style="width: 20px"></div>
      <q-btn
        icon="save"
        class="bg-orange-5 col-2"
        style="text-transform: none !important"
        @click="onSaveSubnets"
      >
        Save Config
      </q-btn>
    </q-card-section>

    <template v-for="(subnet, idx) in subnets" :key="idx">
      <q-separator></q-separator>
      <q-card-section class="row">
        <q-input
          v-model="subnet.address"
          label="Address"
          class="col-5"
        ></q-input>
        <q-space></q-space>
        <q-input
          v-model="subnet.cidr"
          label="CIDR"
          type="number"
          class="col-4"
        ></q-input>
        <q-space></q-space>
        <q-btn
          icon="delete_forever"
          dense
          class="bg-red-5 col-2"
          style="text-transform: none !important"
          @click="onDeleteSubnet(idx)"
        >
          Delete
        </q-btn>
      </q-card-section>
    </template>
  </q-card>
</template>
