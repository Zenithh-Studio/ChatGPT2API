<template>
  <FormSection title="Dashboard">
    <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
      <FormField label="Default reporting period">
        <template #label-extra>
          <HelpTip text="This period is selected by default for charts when you open the Overview. You can still change it on the page." />
        </template>
        <GroupedSelectMenu
          :model-value="defaultTimeRange"
          :options="DASHBOARD_TIME_RANGE_OPTIONS"
          selected-indicator="none"
          aria-label="Default reporting period for Overview"
          block
          @update:model-value="setDefaultTimeRange"
        />
      </FormField>

      <FormField label="Auto-refresh interval (seconds)">
        <template #label-extra>
          <HelpTip text="Default: 10 seconds; range 5–300 seconds. Changes are saved in this browser and are not written to backend settings." />
        </template>
        <Input
          :model-value="refreshIntervalDraft"
          type="number"
          min="5"
          max="300"
          step="1"
          block
          @update:model-value="refreshIntervalDraft = $event"
          @blur="commitRefreshInterval"
          @keyup.enter="commitRefreshInterval"
        />
      </FormField>
    </div>
  </FormSection>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { FormField, FormSection, GroupedSelectMenu, HelpTip, Input } from 'nanocat-ui'
import { DASHBOARD_TIME_RANGE_OPTIONS } from '@/lib/timeRanges'
import {
  readDashboardDefaultTimeRange,
  readDashboardRefreshIntervalSeconds,
  writeDashboardDefaultTimeRange,
  writeDashboardRefreshIntervalSeconds,
} from '@/views/dashboard/dashboardPreferences'

const defaultTimeRange = ref(readDashboardDefaultTimeRange())
const refreshIntervalDraft = ref(String(readDashboardRefreshIntervalSeconds()))

function setDefaultTimeRange(value: string | string[]) {
  defaultTimeRange.value = writeDashboardDefaultTimeRange(value)
}

function commitRefreshInterval() {
  const seconds = writeDashboardRefreshIntervalSeconds(refreshIntervalDraft.value)
  refreshIntervalDraft.value = String(seconds)
}
</script>
