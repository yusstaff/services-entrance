<script setup lang="ts">
import { ref } from 'vue';
import Domain from 'api/certbot/data/domain';
import getDomains from 'api/certbot/request/get_domains';
import addDomains from 'api/certbot/request/add_domains';
import deleteDomains from 'api/certbot/request/delete_domains';
import getAccount from 'api/certbot/request/get_account';
import modifyAccount from 'api/certbot/request/modify_account';
import { Notify } from 'quasar';

// --------------------------------------------------
// table
type ColumnType = {
  name: string;
  required?: boolean;
  label: string;
  align?: 'left' | 'right' | 'center';
  field: string;
};

const columnDefination: ColumnType[] = [
  {
    name: 'domain',
    required: true,
    label: 'Domain',
    align: 'left',
    field: 'domain',
  },
  {
    name: 'hasCertificate',
    required: true,
    label: 'State',
    align: 'center',
    field: 'hasCertificate',
  },
];

const pagination = ref({
  rowsPerPage: 0,
});

const selected = ref<Domain[]>([]);
const domains = ref<Domain[]>([]);

getDomains().then((res) => {
  domains.value = res.data.domains;
});

const isAccountDialogOpen = ref(false);
const curEmailOfAccount = ref('');
const newEmailOfAccount = ref('');
const newApiKeyOfAccount = ref('');

getAccount().then((res) => {
  curEmailOfAccount.value = res.data.email;
});

function updateAccount() {
  modifyAccount({
    email: newEmailOfAccount.value,
    api_key: newApiKeyOfAccount.value,
  }).then((res) => {
    curEmailOfAccount.value = res.data.email;
    Notify.create({
      message: 'Save succeeded',
      color: 'green',
      position: 'top',
    });
  });
}

function openAccountDialog() {
  isAccountDialogOpen.value = true;
  newEmailOfAccount.value = '';
  newApiKeyOfAccount.value = '';
}

const isAddDialogOpen = ref(false);
const newDomain = ref('');

function openAddDialog() {
  isAddDialogOpen.value = true;
  newDomain.value = '';
}

function onAddDomain() {
  addDomains({ domains: [newDomain.value] }).then((res) => {
    domains.value = domains.value.concat(res.data.domains);
  });
}

function onDeleteDomain() {
  deleteDomains({ domains: selected.value }).then((res) => {
    selected.value = [];
    domains.value = domains.value.filter(
      (d) => !res.data.domains.some((rd) => rd.domain === d.domain)
    );
  });
}
</script>

<template>
  <q-table
    :columns="columnDefination"
    :rows="domains"
    :rows-per-page-options="[0]"
    row-key="domain"
    title="Certbot"
    selection="multiple"
    virtual-scroll
    v-model:pagination="pagination"
    v-model:selected="selected"
  >
    <template #top-right>
      <q-tr>
        <q-td>
          <div class="text-bold q-pa-sm">Current Cloudflare Account:</div>
        </q-td>
        <q-td>
          <q-btn
            color="blue"
            style="text-transform: none !important"
            @click="openAccountDialog"
          >
            {{ curEmailOfAccount === '' ? 'None' : curEmailOfAccount }}
          </q-btn>
        </q-td>
        <q-td style="width: 20px"></q-td>
        <q-td>
          <q-btn
            :disable="curEmailOfAccount === ''"
            :color="curEmailOfAccount === '' ? 'grey' : 'green'"
            style="width: 140px; text-transform: none !important"
            @click="openAddDialog"
          >
            Add New Domain
          </q-btn>
        </q-td>
        <q-td style="width: 20px"></q-td>
        <q-td>
          <q-btn
            :disable="selected.length == 0 || curEmailOfAccount === ''"
            :color="curEmailOfAccount === '' ? 'grey' : 'red'"
            style="width: 80px; text-transform: none !important"
            @click="onDeleteDomain"
          >
            Delete
          </q-btn>
        </q-td>
      </q-tr>
    </template>

    <template #body-cell-hasCertificate="props">
      <q-td
        v-if="props.value === true"
        :style="{
          'background-color': 'lightgreen',
          'text-align': props.col.align,
        }"
      >
        Certified
      </q-td>
      <q-td
        v-if="props.value !== true"
        :style="{
          'background-color': 'lightpink',
          'text-align': props.col.align,
        }"
      >
        Not Ready
      </q-td>
    </template>
  </q-table>

  <q-dialog v-model="isAddDialogOpen">
    <q-card style="width: 300px">
      <q-card-section class="text-h6">
        Add
        <q-input v-model:model-value="newDomain" label="Domain" />
      </q-card-section>

      <q-card-actions align="right">
        <q-btn
          :disable="newDomain === ''"
          flat
          label="Confirm"
          color="primary"
          v-close-popup
          @click="onAddDomain"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>

  <q-dialog v-model="isAccountDialogOpen">
    <q-card style="width: 600px">
      <q-card-section class="text-h6">
        Cloudflare Account
        <div class="row">
          <q-input
            v-model:model-value="newEmailOfAccount"
            label="Email"
            class="full-width"
          />
        </div>
        <div class="row">
          <q-input
            v-model:model-value="newApiKeyOfAccount"
            label="API Key"
            class="full-width"
          />
        </div>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn
          :disable="newEmailOfAccount === '' || newApiKeyOfAccount === ''"
          flat
          label="Confirm"
          color="primary"
          v-close-popup
          @click="updateAccount"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>
