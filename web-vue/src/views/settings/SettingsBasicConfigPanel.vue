<template>
  <div class="space-y-4">
    <FormSection title="Basic configuration">
      <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
        <FormField label="Background maintenance interval">
          <template #label-extra>
            <HelpTip text="Minutes. Controls how often pending accounts, rate-limited accounts, and expiring ATs are processed in the background." />
          </template>
          <SettingsNumberInput :field="refreshAccountIntervalField" />
        </FormField>

        <FormField label="Image URL">
          <template #label-extra>
            <HelpTip text="URL prefix for image results." />
          </template>
          <Input
            v-model.trim="settings.base_url"
            block
            :disabled="fieldReadOnly('base_url')"
            placeholder="https://example.com"
          />
        </FormField>

        <FormField label="Automatic image cleanup">
          <template #label-extra>
            <HelpTip text="Automatically delete local images older than this many hours." />
          </template>
          <SettingsNumberInput :field="imageRetentionHoursField" />
        </FormField>

        <FormField label="Automatic log cleanup">
          <template #label-extra>
            <HelpTip text="Automatically delete console API call logs older than this many hours." />
          </template>
          <SettingsNumberInput :field="logRetentionHoursField" />
        </FormField>

        <FormField label="Per-account image concurrency">
          <template #label-extra>
            <HelpTip text="Limit the number of concurrent image requests per account. Default: 1; range: 1–3." />
          </template>
          <SettingsNumberInput :field="imageAccountConcurrencyField" />
        </FormField>

        <FormField label="Account batch task concurrency">
          <template #label-extra>
            <HelpTip text="Maximum concurrency for account batch tasks. Refreshing ATs, syncing account data and quotas, validating imports, and background checks use one slot per account. Enabling, disabling, resetting, deleting, and saving a batch use one slot per batch. Default: 30; range: 1–100. Image generation has a separate concurrency limit." />
          </template>
          <SettingsNumberInput :field="accountProcessingConcurrencyField" />
        </FormField>
      </div>
    </FormSection>

    <FormSection title="Requests and tasks">
      <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
        <FormField label="Console request timeout">
          <template #label-extra>
            <HelpTip text="Seconds. Maximum time console requests for logs, images, accounts, and settings wait for a backend response." />
          </template>
          <SettingsNumberInput :field="consoleRequestTimeoutField" />
        </FormField>

      </div>
    </FormSection>

    <FormSection title="Image generation">
      <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
        <FormField label="Image stream timeout limit">
          <template #label-extra>
            <HelpTip text="Seconds. Maximum wait time for the ChatGPT image generation SSE stream." />
          </template>
          <SettingsNumberInput :field="imageStreamTimeoutField" />
        </FormField>

        <FormField label="Image result timeout limit">
          <template #label-extra>
            <HelpTip text="Seconds. Maximum time to wait for the upstream image result after the SSE stream ends." />
          </template>
          <SettingsNumberInput :field="imagePollTimeoutField" />
        </FormField>

        <FormField label="Initial image polling delay">
          <template #label-extra>
            <HelpTip text="Seconds. Time to wait before the first image result poll." />
          </template>
          <SettingsNumberInput :field="imagePollInitialWaitField" />
        </FormField>

        <FormField label="Image polling interval">
          <template #label-extra>
            <HelpTip text="Seconds. Time to wait between image result polls." />
          </template>
          <SettingsNumberInput :field="imagePollIntervalField" />
        </FormField>
      </div>
    </FormSection>
  </div>
</template>

<script setup lang="ts">
import { FormField, FormSection, HelpTip, Input } from 'nanocat-ui'
import type { Settings } from '@/types/api'
import SettingsNumberInput from '@/views/settings/SettingsNumberInput.vue'
import { settingsFieldReadOnly, type SettingsFields } from '@/views/settings/settingsView'
import type { NumberSettingField } from '@/views/settings/useNumberSettingField'

const props = defineProps<{
  settings: Settings
  fields: SettingsFields
  refreshAccountIntervalField: NumberSettingField
  imageRetentionHoursField: NumberSettingField
  logRetentionHoursField: NumberSettingField
  consoleRequestTimeoutField: NumberSettingField
  imagePollTimeoutField: NumberSettingField
  imageStreamTimeoutField: NumberSettingField
  imagePollInitialWaitField: NumberSettingField
  imagePollIntervalField: NumberSettingField
  imageAccountConcurrencyField: NumberSettingField
  accountProcessingConcurrencyField: NumberSettingField
}>()

const fieldReadOnly = (path: string) => settingsFieldReadOnly(props.fields, path)
</script>
