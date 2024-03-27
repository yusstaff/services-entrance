<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue';
import getDomains from 'api/certbot/request/get_domains';
import getProxy from 'api/envoy/request/get_proxy';
import Config, { FilterChain, VirtualHost } from 'api/envoy/data/config';
import modifyProxy from 'api/envoy/request/modify_proxy';
import { Notify, QCardSection } from 'quasar';

const config = ref<Config>();
const domains = ref<string[]>();
const allClusters = computed(() => {
  if (config.value) {
    const clusters: string[] = [];
    config.value.static_resources.clusters.forEach((cluster) => {
      clusters.push(cluster.name);
    });
    return clusters;
  } else {
    return [];
  }
});

// fetch and save data
function fetchData() {
  getDomains().then((res) => {
    domains.value = res.data.domains
      .filter((d) => d.hasCertificate)
      .map((d) => d.domain);
  });
  getProxy().then((res) => {
    config.value = res.data.config;
  });
}
fetchData();

function save() {
  if (config.value === undefined) {
    return;
  }
  modifyProxy({ config: config.value }).then(() => {
    Notify.create({
      message: 'Save succeeded',
      color: 'green',
      position: 'top',
    });
  });
}

// listener
function addListener() {
  if (config.value) {
    const filterChain = {
      server_names: [],
      domain: '',
      filters: [
        {
          virtual_hosts: [],
          max_request_bytes: '16K',
        },
      ],
    };
    addServerName(filterChain);
    addVirtualHost(filterChain);
    config.value.static_resources.filter_chains.unshift(filterChain);
  }
}

function deleteListener(fcIdx: number) {
  config.value?.static_resources.filter_chains.splice(fcIdx, 1);
}

// server name
function addServerName(filter_chian: FilterChain) {
  filter_chian.server_names.unshift('');
}

function deleteServerName(filter_chian: FilterChain, snIdx: number) {
  filter_chian.server_names.splice(snIdx, 1);
}

// virtual host
function addVirtualHost(filterChain: FilterChain) {
  const virtual_host = {
    name: '',
    domains: [''],
    routes: [],
  };
  addRoute(virtual_host);
  filterChain.filters[0].virtual_hosts.unshift(virtual_host);
}

function deleteVirtualHost(filterChain: FilterChain, vhIdx: number) {
  filterChain.filters[0].virtual_hosts.splice(vhIdx, 1);
}

// domain
function addDomain(virtualHost: VirtualHost) {
  virtualHost.domains.unshift('');
}

function deleteDomain(virtualHost: VirtualHost, vhIdx: number) {
  virtualHost.domains.splice(vhIdx, 1);
}

// route
function addRoute(virtualHost: VirtualHost) {
  virtualHost.routes.unshift({
    prefix: '/',
    cluster: '',
    host_rewrite_literal: '',
  });
}

function deleteRoute(virtualHost: VirtualHost, rIdx: number) {
  virtualHost.routes.splice(rIdx, 1);
}

// draggable element refs ---------------------------------------------
// draggable chain
function onEnterChain(fcIdx: number) {
  targetChainIdx.value = fcIdx;
}

function setChainRef(chain: object | null, fcIdx: number) {
  if (chain) {
    (chain as QCardSection).$el.addEventListener('mouseenter', () => {
      onEnterChain(fcIdx);
    });
  }
}

// draggable virtual host
function onEnterVirtualHost(vhIdx: number) {
  targetVirtualHostIdx.value = vhIdx;
}

function setVirtualHostRef(virtualHost: object | null, vhIdx: number) {
  if (virtualHost) {
    (virtualHost as QCardSection).$el.addEventListener('mouseenter', () => {
      onEnterVirtualHost(vhIdx);
    });
  }
}

// drag chain ---------------------------------------------------
const isDraggingChain = ref(false);
const draggedChainIdx = ref(0);
const targetChainIdx = ref(0);

function onDragChainBegin(fcIdx: number) {
  isDraggingChain.value = true;
  draggedChainIdx.value = fcIdx;
  document.body.classList.add('dragging');
}

function onDragChainEnd() {
  if (!isDraggingChain.value) {
    return;
  }
  isDraggingChain.value = false;
  document.body.classList.remove('dragging');

  if (targetChainIdx.value !== draggedChainIdx.value) {
    const arr = config.value?.static_resources.filter_chains;
    if (arr) {
      const chain = arr[draggedChainIdx.value];
      if (targetChainIdx.value < draggedChainIdx.value) {
        arr.splice(draggedChainIdx.value, 1);
        arr.splice(targetChainIdx.value, 0, chain);
      } else {
        arr.splice(targetChainIdx.value, 0, chain);
        arr.splice(draggedChainIdx.value, 1);
      }
    }
  }
}

// drag virtual host ---------------------------------------------------
const isDraggingVirtualHost = ref(false);
const draggedVirtualHostIdx = ref(0);
const targetVirtualHostIdx = ref(0);

function onDragVirtualHostBegin(fcIdx: number, vhIdx: number) {
  isDraggingVirtualHost.value = true;
  draggedChainIdx.value = fcIdx;
  draggedVirtualHostIdx.value = vhIdx;
  document.body.classList.add('dragging');
}

function onDragVirtualHostEnd() {
  if (!isDraggingVirtualHost.value) {
    return;
  }
  isDraggingVirtualHost.value = false;
  document.body.classList.remove('dragging');

  if (
    targetChainIdx.value === draggedChainIdx.value &&
    targetVirtualHostIdx.value !== draggedVirtualHostIdx.value
  ) {
    const arr =
      config.value?.static_resources.filter_chains[targetChainIdx.value]
        .filters[0].virtual_hosts;
    if (arr) {
      const virtualHost = arr[draggedVirtualHostIdx.value];
      if (targetVirtualHostIdx.value < draggedVirtualHostIdx.value) {
        arr.splice(draggedVirtualHostIdx.value, 1);
        arr.splice(targetVirtualHostIdx.value, 0, virtualHost);
      } else {
        arr.splice(targetVirtualHostIdx.value, 0, virtualHost);
        arr.splice(draggedVirtualHostIdx.value, 1);
      }
    }
  }
}

// drop
function onMouseUp() {
  onDragChainEnd();
  onDragVirtualHostEnd();
}

onMounted(() => {
  document.addEventListener('mouseup', onMouseUp);
});

onUnmounted(() => {
  document.removeEventListener('mouseup', onMouseUp);
});
</script>

<template>
  <q-card class="q-flex">
    <q-card-section class="row" style="font-size: 20px">
      <div class="text-bold text-center flex flex-center">Envoy Listeners</div>

      <q-space></q-space>

      <q-btn
        icon="add_box"
        class="bg-green-5 col-2"
        style="text-transform: none !important"
        @click="addListener"
      >
        Add Listener
      </q-btn>
      <div style="width: 20px"></div>
      <q-btn
        icon="save"
        class="bg-orange-5 col-2"
        style="text-transform: none !important"
        @click="save"
      >
        Save Config
      </q-btn>
    </q-card-section>

    <q-separator></q-separator>

    <!-- FilterChains -->
    <q-card-section
      v-for="(filterChain, fcIdx) in config?.static_resources.filter_chains"
      :key="fcIdx"
      :ref="(el: object | null) => setChainRef(el, fcIdx)"
    >
      <q-card
        v-if="
          isDraggingChain &&
          fcIdx === targetChainIdx &&
          fcIdx !== draggedChainIdx
        "
      >
        <q-card-section
          style="height: 100px"
          class="bg-yellow-3 q-mb-sm"
        ></q-card-section>
      </q-card>

      <q-card :dark="isDraggingChain && fcIdx === draggedChainIdx">
        <q-card-section class="bg-blue-3 q-pt-xs q-pb-xs q-pl-xs row">
          <div
            style="cursor: grab"
            class="text-bold text-center flex flex-center q-ma-sm"
            @mousedown.prevent="onDragChainBegin(fcIdx)"
          >
            <q-icon
              name="drag_handle"
              size="sm"
              color="white"
              class="q-mr-xs"
            ></q-icon>
            Certificate
          </div>
          <q-select
            v-model="filterChain.domain"
            :options="domains"
            outlined
            borderless
            rounded
            dense
            bg-color="white"
            style="min-width: 220px"
          ></q-select>

          <q-space></q-space>

          <div style="width: 20px"></div>
          <q-btn
            icon="delete_forever"
            class="bg-red-5 col-2"
            style="text-transform: none !important"
            @click="deleteListener(fcIdx)"
          >
            Delete Listener
          </q-btn>
        </q-card-section>

        <template v-if="filterChain.domain !== ''">
          <q-card-section class="bg-blue-2 q-pt-xs q-pb-xs row">
            <div class="text-bold text-center flex flex-center">
              Server Names
            </div>

            <q-space></q-space>

            <q-btn
              icon="add"
              class="bg-green-5 col-1"
              style="text-transform: none !important"
              @click="addServerName(filterChain)"
            ></q-btn>
          </q-card-section>

          <template
            v-for="(server, snIdx) in filterChain.server_names"
            :key="snIdx"
          >
            <q-separator></q-separator>
            <q-card-section class="bg-blue-1 q-pt-xs q-pb-xs row">
              <q-input
                v-model:model-value="filterChain.server_names[snIdx]"
                dense
                outlined
                bgColor="white"
                class="q-pl-sm q-pr-sm col-11"
              ></q-input>
              <q-btn
                icon="clear"
                dense
                class="bg-red-4 col-1"
                style="text-transform: none !important"
                @click="deleteServerName(filterChain, snIdx)"
              ></q-btn>
            </q-card-section>
          </template>
          <q-card-section
            v-if="filterChain.server_names.length === 0"
            class="bg-blue-1 q-pa-md"
          ></q-card-section>

          <q-card-section class="bg-blue-2 q-pt-xs q-pb-xs row">
            <div class="text-bold text-center flex flex-center">
              Virtual Hosts
            </div>

            <q-space></q-space>

            <q-btn
              icon="add"
              class="bg-green-5 col-1"
              style="text-transform: none !important"
              @click="addVirtualHost(filterChain)"
            ></q-btn>
          </q-card-section>

          <!-- Filter -->
          <q-card-section
            v-for="(filter, fIdx) in filterChain.filters"
            :key="fIdx"
            class="bg-blue-1"
          >
            <!-- params -->
            <q-card class="q-mb-sm">
              <q-card-section class="bg-orange-1 q-pt-sm q-pb-sm row">
                <div class="text-bold text-center flex flex-center">
                  Parameters
                </div>
                <q-space></q-space>
              </q-card-section>
              <q-card-section class="bg-grey-2 q-pt-xs q-pb-xs row">
                <q-input
                  v-model:model-value="filter.max_request_bytes"
                  label="Max Request Size"
                  dense
                  outlined
                  bgColor="white"
                  class="q-pl-sm q-pr-sm col-3"
                ></q-input>
                <div class="flex items-center justify-start q-pa-none col-1">
                  Bytes
                </div>
              </q-card-section>
            </q-card>

            <template v-for="(vh, vhIdx) in filter.virtual_hosts" :key="vhIdx">
              <q-card
                v-if="
                  isDraggingVirtualHost &&
                  fcIdx == targetChainIdx &&
                  vhIdx === targetVirtualHostIdx &&
                  fcIdx === draggedChainIdx &&
                  vhIdx !== draggedVirtualHostIdx
                "
              >
                <q-card-section
                  style="height: 100px"
                  class="bg-yellow-3 q-mb-sm"
                ></q-card-section>
              </q-card>

              <q-card
                :dark="
                  isDraggingVirtualHost &&
                  fcIdx === draggedChainIdx &&
                  vhIdx === draggedVirtualHostIdx
                "
                class="q-mb-sm"
                :ref="(el: object | null) => setVirtualHostRef(el, vhIdx)"
              >
                <q-card-section class="bg-orange-2 q-pt-sm q-pb-xs q-pl-xs row">
                  <div
                    style="cursor: grab"
                    class="text-bold text-center flex flex-center q-ma-sm"
                    @mousedown.prevent="onDragVirtualHostBegin(fcIdx, vhIdx)"
                  >
                    <q-icon
                      name="drag_handle"
                      size="sm"
                      color="white"
                      class="q-mr-xs"
                    ></q-icon>
                    Virtual Host
                  </div>
                  <q-input
                    v-model:model-value="vh.name"
                    label="Name"
                    dense
                    outlined
                    bgColor="white"
                    class="q-pl-sm q-pr-sm"
                  ></q-input>
                  <q-space></q-space>
                  <q-btn
                    icon="delete_forever"
                    dense
                    class="bg-red-5 col-1"
                    style="text-transform: none !important"
                    @click="deleteVirtualHost(filterChain, vhIdx)"
                  ></q-btn>
                </q-card-section>

                <!-- Domains -->
                <q-card-section class="bg-orange-1 q-pt-xs q-pb-xs row">
                  <div class="text-bold text-center flex flex-center">
                    Domains
                  </div>
                  <q-space></q-space>
                  <q-btn
                    icon="add"
                    class="bg-green-4 col-1"
                    @click="addDomain(vh)"
                  ></q-btn>
                </q-card-section>

                <template v-for="(domain, dIdx) in vh.domains" :key="dIdx">
                  <q-separator></q-separator>
                  <q-card-section class="bg-grey-2 q-pt-xs q-pb-xs row">
                    <q-input
                      v-model:model-value="vh.domains[dIdx]"
                      dense
                      outlined
                      bgColor="white"
                      class="q-pl-sm q-pr-sm col-11"
                    ></q-input>
                    <q-btn
                      icon="clear"
                      dense
                      class="bg-red-4 col-1"
                      style="text-transform: none !important"
                      @click="deleteDomain(vh, dIdx)"
                    ></q-btn>
                  </q-card-section>
                </template>

                <!-- Routes -->
                <q-card-section class="bg-orange-1 q-pt-xs q-pb-xs row">
                  <div class="text-bold text-center flex flex-center">
                    Routes
                  </div>
                  <q-space></q-space>
                  <q-btn
                    icon="add"
                    class="bg-green-4 col-1"
                    @click="addRoute(vh)"
                  ></q-btn>
                </q-card-section>
                <template v-for="(route, rIdx) in vh.routes" :key="rIdx">
                  <q-separator></q-separator>
                  <q-card-section class="bg-grey-2 q-pt-xs q-pb-xs row">
                    <!-- Prefix -->
                    <q-input
                      v-model:model-value="route.prefix"
                      label="Prefix"
                      dense
                      outlined
                      bgColor="white"
                      class="q-pl-sm q-pr-sm col-7"
                    ></q-input>

                    <!-- Cluster -->
                    <q-select
                      v-model="route.cluster"
                      :options="allClusters"
                      label="Cluster"
                      outlined
                      borderless
                      rounded
                      dense
                      bg-color="white"
                      class="q-pl-sm q-pr-sm col-4"
                    ></q-select>

                    <q-btn
                      icon="clear"
                      dense
                      class="bg-red-4 col-1"
                      style="text-transform: none !important"
                      @click="deleteRoute(vh, rIdx)"
                    ></q-btn>
                  </q-card-section>
                  <q-card-section class="bg-grey-2 q-pt-xs q-pb-xs row">
                    <!-- Host Rewrite Literal -->
                    <q-input
                      v-model:model-value="route.host_rewrite_literal"
                      label="Host Rewrite Literal"
                      dense
                      outlined
                      bgColor="white"
                      class="q-pl-sm q-pr-sm col-11"
                    ></q-input>

                    <q-space></q-space>
                  </q-card-section>
                </template>
              </q-card>
            </template>
          </q-card-section>
        </template>
      </q-card>
    </q-card-section>
  </q-card>
</template>
