<script setup lang="ts">
import { computed, ref } from 'vue';
import getProxy from 'api/envoy/request/get_proxy';
import Config, { Cluster, Endpoint, Route } from 'api/envoy/data/config';
import modifyProxy from 'api/envoy/request/modify_proxy';
import { Notify } from 'quasar';

const config = ref<Config>();
const protocols = ref<string[]>(['HTTP/1.1', 'HTTPS/1.1', 'HTTP/2']);
const clustersBeingUsed = computed(() => {
  if (config.value) {
    const clusters: string[] = [];
    config.value.static_resources.filter_chains.forEach((chain) => {
      chain.filters.forEach((filter) => {
        filter.virtual_hosts.forEach((virtual_host) => {
          virtual_host.routes.forEach((route) => {
            clusters.push(route.cluster);
          });
        });
      });
    });
    return clusters;
  } else {
    return [];
  }
});
const clusterRouteMap = new Map<Cluster, Route[]>();

function fetchData() {
  getProxy().then((res) => {
    config.value = res.data.config;

    config.value.static_resources.filter_chains.forEach((chain) => {
      chain.filters.forEach((filter) => {
        filter.virtual_hosts.forEach((virtual_host) => {
          virtual_host.routes.forEach((route) => {
            const cluster = config.value?.static_resources.clusters.find(
              (c) => c.name === route.cluster
            );
            if (cluster) {
              const routes = clusterRouteMap.get(cluster);
              if (routes) {
                routes.push(route);
              } else {
                clusterRouteMap.set(cluster, [route]);
              }
            }
          });
        });
      });
    });
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

function addCluster() {
  const cluster = {
    name: '',
    endpoints: [],
    protocol: 'HTTP/2',
  };
  addEndpoint(cluster);
  config.value?.static_resources.clusters.unshift(cluster);
}

function deleteCluster(idx: number) {
  config.value?.static_resources.clusters.splice(idx, 1);
}

function addEndpoint(cluster: Cluster) {
  const endpoint = {
    lb_endpoints: [],
  };
  addLbEndpoint(endpoint);
  cluster.endpoints.unshift(endpoint);
}

function deleteEndpoint(cluster: Cluster, idx: number) {
  cluster.endpoints.splice(idx, 1);
}

function addLbEndpoint(endpoint: Endpoint) {
  endpoint.lb_endpoints.unshift({
    address: 'localhost',
    port_value: 443,
  });
}

function deleteLbEndpoint(endpoint: Endpoint, idx: number) {
  endpoint.lb_endpoints.splice(idx, 1);
}

function onClusterNameUpdated(val: string | undefined, cluster: Cluster) {
  if (val && config.value) {
    const routes = clusterRouteMap.get(cluster);
    if (routes) {
      routes.forEach((route) => {
        route.cluster = val;
      });
    }
    cluster.name = val;
  }
}
</script>

<template>
  <q-card class="q-flex">
    <q-card-section class="row" style="font-size: 20px">
      <div class="text-bold text-center flex flex-center">Envoy Clusters</div>

      <q-space></q-space>

      <q-btn
        icon="add_box"
        class="bg-green-5 col-2"
        style="text-transform: none !important"
        @click="addCluster"
      >
        Add Cluster
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

    <!-- Clusters -->
    <q-card-section
      v-for="(cluster, cIdx) in config?.static_resources.clusters"
      :key="cIdx"
    >
      <q-card>
        <q-card-section class="bg-blue-3 q-pt-xs q-pb-xs row">
          <div class="text-bold text-center flex flex-center q-ma-sm">
            Cluster
          </div>
          <q-input
            :model-value="cluster.name"
            label="Name"
            outlined
            borderless
            dense
            bg-color="white"
            style="min-width: 220px"
            @update:model-value="
              onClusterNameUpdated($event?.toString(), cluster)
            "
          ></q-input>
          <q-select
            v-model="cluster.protocol"
            :options="protocols"
            outlined
            borderless
            dense
            bg-color="white"
          ></q-select>

          <q-space></q-space>

          <q-btn
            v-if="false"
            icon="playlist_add"
            class="bg-green-5 col-2"
            style="text-transform: none !important"
            @click="addEndpoint(cluster)"
          >
            Add Endpoint
          </q-btn>
          <div style="width: 20px"></div>
          <q-btn
            icon="delete_forever"
            :disable="clustersBeingUsed.includes(cluster.name)"
            class="bg-red-5 col-2"
            style="text-transform: none !important"
            @click="deleteCluster(cIdx)"
          >
            {{
              clustersBeingUsed.includes(cluster.name)
                ? 'In Using'
                : 'Delete Cluster'
            }}
          </q-btn>
        </q-card-section>

        <q-separator></q-separator>

        <!-- Endpoints -->
        <q-card-section class="bg-blue-1">
          <q-card
            v-for="(endpoint, eIdx) in cluster.endpoints"
            :key="eIdx"
            class="q-mb-sm"
          >
            <q-card-section class="bg-orange-2 q-pt-sm q-pb-xs row">
              <div class="text-bold text-center flex flex-center q-ma-sm">
                Endpoint {{ eIdx }}
              </div>
              <q-space></q-space>
              <q-btn
                v-if="false"
                icon="delete_forever"
                class="bg-red-5 col-1"
                style="text-transform: none !important"
                @click="deleteEndpoint(cluster, eIdx)"
              ></q-btn>
            </q-card-section>

            <q-card-section class="bg-orange-1 q-pt-xs q-pb-xs row">
              <div class="text-bold text-center flex flex-center q-ml-md">
                LB Endpoints
              </div>
              <q-space></q-space>
              <q-btn
                v-if="false"
                icon="add"
                class="bg-green-4 col-1"
                @click="addLbEndpoint(endpoint)"
              ></q-btn>
            </q-card-section>

            <!-- Lb Endpoints -->
            <template
              v-for="(lbEndpoint, leIdx) in endpoint.lb_endpoints"
              :key="leIdx"
            >
              <q-separator></q-separator>
              <q-card-section class="bg-grey-2 q-pt-xs q-pb-xs row">
                <q-input
                  v-model:model-value="lbEndpoint.address"
                  label="Address"
                  dense
                  outlined
                  bgColor="white"
                  class="q-pl-sm q-pr-sm col-5"
                ></q-input>

                <q-space></q-space>
                <q-input
                  v-model:model-value="lbEndpoint.port_value"
                  type="number"
                  label="Port"
                  dense
                  outlined
                  bgColor="white"
                  class="q-pl-sm q-pr-sm col-5"
                ></q-input>
                <q-space></q-space>
                <q-btn
                  v-if="false"
                  icon="clear"
                  class="bg-red-4 col-1"
                  style="text-transform: none !important"
                  @click="deleteLbEndpoint(endpoint, leIdx)"
                ></q-btn>
              </q-card-section>
            </template>
          </q-card>
        </q-card-section>
      </q-card>
    </q-card-section>
  </q-card>
</template>
