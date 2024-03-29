<script setup lang="ts">
import { ref } from 'vue';
import Peer from 'api/wireguard/data/peer';
import getPeers from 'api/wireguard/request/get_peers';
import addPeers from 'api/wireguard/request/add_peers';
import deletePeers from 'api/wireguard/request/delete_peers';
import download_peer from 'api/wireguard/request/download_peer';
import Subnet from 'api/data/subnet';
import getSubnets from 'api/wireguard/request/get_subnets';
import modifySubnets from 'api/wireguard/request/modify_subnets';
import { Notify } from 'quasar';

// --------------------------------------------------
// peer table
type ColumnType = {
  name: string;
  required?: boolean;
  label: string;
  align?: 'left' | 'right' | 'center';
  field: string;
};

const columnDefination: ColumnType[] = [
  {
    name: 'name',
    required: true,
    label: 'Peer',
    align: 'left',
    field: 'name',
  },
  {
    name: 'address',
    required: true,
    label: 'Address',
    align: 'left',
    field: 'address',
  },
  {
    name: 'public_key',
    required: true,
    label: 'Public Key',
    align: 'left',
    field: 'public_key',
  },
  {
    name: 'download',
    required: true,
    label: 'Download',
    align: 'left',
    field: 'download',
  },
];

const pagination = ref({
  rowsPerPage: 0,
});

const selected = ref<Peer[]>([]);
const peers = ref<Peer[]>([]);

function fetchPeers() {
  getPeers().then((res) => {
    peers.value = res.data.peers;
  });
}
fetchPeers();

// --------------------------------------------------
// add
const isAddDialogOpen = ref(false);
const newPeerName = ref('');

function openAddDialog() {
  isAddDialogOpen.value = true;
  newPeerName.value = '';
}

function onAddPeer() {
  addPeers({ peers: [newPeerName.value] }).then((res) => {
    peers.value = peers.value.concat(res.data.peers);
  });
}

// --------------------------------------------------
// delete
function onDeletePeer() {
  deletePeers({ peers: selected.value }).then((res) => {
    selected.value = [];
    peers.value = peers.value.filter(
      (p) => !res.data.peers.some((rd) => rd.name === p.name)
    );
  });
}

// --------------------------------------------------
// download
function onDownloadPeer(peer: Peer) {
  download_peer({ peer: peer.name }).then((res) => {
    const blob = new Blob([res.data.peer], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = peer.name + '.conf';
    document.body.appendChild(a);
    a.click();

    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  });
}

const subnets = ref<Subnet[]>([]);

function fetchSubnets() {
  getSubnets().then((res) => {
    subnets.value = res.data.subnets;
  });
}
fetchSubnets();

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
  <q-table
    :columns="columnDefination"
    :rows="peers"
    :rows-per-page-options="[0]"
    row-key="name"
    title="Wireguard"
    selection="multiple"
    virtual-scroll
    v-model:pagination="pagination"
    v-model:selected="selected"
  >
    <template #body-cell-download="props">
      <q-td :props="props">
        <q-btn
          :icon="props.row.address === '' ? 'pending' : 'download'"
          :color="props.row.address === '' ? 'grey' : 'blue'"
          :disable="props.row.address === ''"
          style="width: 140px; text-transform: none !important"
          @click="onDownloadPeer(props.row)"
        >
          {{ props.row.address === '' ? 'Need Restart' : 'Download' }}
        </q-btn>
      </q-td>
    </template>
    <template #top-left>
      <div class="text-bold text-h6 text-center flex flex-center">
        Wireguard
      </div>
    </template>
    <template #top-right>
      <q-tr>
        <q-td>
          <q-btn
            icon="add_to_queue"
            color="green"
            style="width: 160px; text-transform: none !important"
            @click="openAddDialog"
          >
            Add New Peer
          </q-btn>
        </q-td>
        <q-td style="width: 20px"></q-td>
        <q-td>
          <q-btn
            icon="delete_forever"
            :disable="selected.length == 0"
            color="red"
            style="width: 120px; text-transform: none !important"
            @click="onDeletePeer"
          >
            Delete
          </q-btn>
        </q-td>
      </q-tr>
    </template>
  </q-table>

  <q-card class="q-flex">
    <q-card-section class="row" style="font-size: 20px">
      <div class="text-bold text-center flex flex-center">Subnets</div>

      <q-space></q-space>

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
          dense
          class="col-5"
        ></q-input>
        <q-space></q-space>
        <q-input
          v-model="subnet.cidr"
          label="CIDR"
          type="number"
          dense
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

  <q-dialog v-model="isAddDialogOpen">
    <q-card style="width: 300px">
      <q-card-section class="text-h6">
        Create
        <q-input
          v-model:model-value="newPeerName"
          label="Peer Name"
          maxlength="16"
        />
      </q-card-section>

      <q-card-actions align="right">
        <q-btn
          :disable="newPeerName === ''"
          flat
          label="Confirm"
          color="primary"
          v-close-popup
          @click="onAddPeer"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>
