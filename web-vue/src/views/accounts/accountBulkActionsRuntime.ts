import type { Ref } from 'vue'

import {
  accountsApi,
  type AccountGroup,
  type AccountOperationProgress,
  type AccountSelectionScope,
  type AccountSelectionTarget,
} from '@/api/accounts'
import type { ProxyGroup } from '@/api/proxy'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { useToast } from '@/composables/useToast'
import type { useAccountBulkProgressRuntime } from './accountBulkProgressRuntime'

export type AccountBulkAction = 'sync' | 'refresh-access-token' | 'enable' | 'disable' | 'delete'
type AccountCredentialAction = Extract<AccountBulkAction, 'sync' | 'refresh-access-token'>
type AccountMutationAction = Exclude<AccountBulkAction, AccountCredentialAction>

type AccountSelectionAdapter = {
  selectedIds: Ref<string[]>
  selectedCount: Readonly<Ref<number>>
  scopedSelectionActive: Readonly<Ref<boolean>>
  selectionScope: Readonly<Ref<AccountSelectionScope>>
  clearSelection: () => void
  removeSelectedIds: (ids: readonly string[]) => void
}

type AccountBulkMutationResponse = {
  progress: AccountOperationProgress | null
}

type AccountBulkActionsRuntimeOptions = {
  bulkProgress: ReturnType<typeof useAccountBulkProgressRuntime>
  accountSelection: AccountSelectionAdapter
  accountGroups: Ref<AccountGroup[]>
  proxyGroups: Ref<ProxyGroup[]>
  selectedBindGroupId: Ref<string>
  normalizeErrorMessage: (error: unknown) => string
  setError: (prefix: string, error: unknown, notify?: boolean) => void
  loadData: (options?: { silentErrorToast?: boolean }) => Promise<void>
  reconcileSelection: () => Promise<boolean>
  applyAccountGroupsPayload: (response: { groups?: AccountGroup[]; proxy_groups?: ProxyGroup[] }) => void
}

function uniqueIds(ids: readonly string[]) {
  return Array.from(new Set(ids.map((id) => String(id || '').trim()).filter(Boolean)))
}

function bulkActionMeta(action: AccountMutationAction) {
  return {
    enable: { title: 'Enable accounts', confirmText: 'Confirm enable' },
    disable: { title: 'Disable accounts', confirmText: 'Confirm disable' },
    delete: { title: 'Delete accounts', confirmText: 'Confirm deletion' },
  }[action]
}

function accountLabel(accountId: string, labels?: Readonly<Record<string, string>>) {
  return String(labels?.[accountId] || '').trim() || accountId
}

function credentialActionMeta(action: AccountCredentialAction) {
  return action === 'sync'
    ? { title: 'Batch sync accounts and quotas', verb: 'Sync', kind: 'sync' as const }
    : { title: 'Batch refresh AT', verb: 'Refresh AT', kind: 'credentials' as const }
}

export function useAccountBulkActionsRuntime(options: AccountBulkActionsRuntimeOptions) {
  const toast = useToast()
  const confirmDialog = useConfirmDialog()

  async function runCredentialActionWithProgress(
    action: AccountCredentialAction,
    target: AccountSelectionTarget,
    targetCount: number,
    useSelectionScope: boolean,
  ) {
    const meta = credentialActionMeta(action)
    const confirmed = await confirmDialog.ask({
      title: meta.title,
      message: useSelectionScope
        ? `About to ${meta.verb} selected under the current filters${targetCount} accounts. Continue?`
        : `About to ${meta.verb} ${targetCount} accounts. The backend will process them with the account batch concurrency limit. Continue?`,
      confirmText: `Start${meta.verb}`,
      cancelText: 'Cancel',
    })
    if (!confirmed) return

    await options.bulkProgress.start(meta.title, targetCount, meta.kind)

    try {
      const request = action === 'sync'
        ? accountsApi.syncAccountsWithProgress
        : accountsApi.refreshAccessTokensWithProgress
      const result = await request(target, (progress) => {
        options.bulkProgress.update({
          ...progress,
          total: Number(progress.total || targetCount),
          processed: Math.min(targetCount, Number(progress.processed || 0)),
          done: false,
        })
      }, targetCount)

      const progress = result.progress
      const operationResult = progress?.result
      const updatedIds = uniqueIds(operationResult?.updated_ids || [])
      const removedIds = uniqueIds(operationResult?.removed_ids || [])
      if (!progress) throw new Error('Account action response is missing its progress projection.')
      options.bulkProgress.finish({
        ...progress,
        total: Number(progress?.total || targetCount),
        processed: Number(progress?.processed || progress?.total || targetCount),
      })
      const completedIds = uniqueIds([...updatedIds, ...removedIds])
      if (useSelectionScope) options.accountSelection.clearSelection()
      else options.accountSelection.removeSelectedIds(completedIds)
      await options.loadData({ silentErrorToast: true })
    } catch (error) {
      options.bulkProgress.fail(
        targetCount,
        Number(options.bulkProgress.refreshProgress.value?.processed || 0),
        options.normalizeErrorMessage(error),
      )
      options.setError(`${meta.title}Failed`, error, false)
      await options.loadData({ silentErrorToast: true })
    } finally {
      options.bulkProgress.end()
    }
  }

  async function runBulkAction(
    action: AccountBulkAction,
    ids?: readonly string[],
    labels?: Readonly<Record<string, string>>,
  ) {
    const useSelectionScope = !ids && options.accountSelection.scopedSelectionActive.value
    if (useSelectionScope && !await options.reconcileSelection()) return
    const targetIds = uniqueIds(ids || options.accountSelection.selectedIds.value)
    const targetCount = useSelectionScope ? options.accountSelection.selectedCount.value : targetIds.length
    const target: AccountSelectionTarget = useSelectionScope
      ? options.accountSelection.selectionScope.value
      : targetIds
    if (!targetCount) {
      toast.warning('Select an account first.')
      return
    }

    if (action === 'sync' || action === 'refresh-access-token') {
      await runCredentialActionWithProgress(action, target, targetCount, useSelectionScope)
      return
    }

    const actionMeta = bulkActionMeta(action)
    const isSingleDelete = action === 'delete' && !useSelectionScope && targetCount === 1
    const confirmed = await confirmDialog.ask({
      title: isSingleDelete ? 'Delete account' : actionMeta.title,
      message: isSingleDelete
        ? `Confirm deletion of account ${accountLabel(targetIds[0], labels)}? This action cannot be undone.`
        : `Confirm this action for the selected ${targetCount} accounts?`,
      confirmText: actionMeta.confirmText,
      cancelText: 'Cancel',
    })
    if (!confirmed) return

    await options.bulkProgress.start(isSingleDelete ? 'Delete account' : actionMeta.title, targetCount, 'mutation')
    try {
      const request = action === 'disable'
        ? accountsApi.bulkDisable
        : action === 'delete'
          ? accountsApi.bulkDelete
          : accountsApi.bulkEnable
      const response: AccountBulkMutationResponse = await request(
        target,
        (progress) => options.bulkProgress.update(progress),
        targetCount,
      )
      const progress = response.progress
      const operationResult = progress?.result
      const updatedIds = uniqueIds(operationResult?.updated_ids || [])
      const removedIds = uniqueIds(operationResult?.removed_ids || [])
      const completedIds = uniqueIds([...updatedIds, ...removedIds])
      if (!progress) throw new Error('Account action response is missing its progress projection.')
      options.bulkProgress.finish(progress)
      if (useSelectionScope) options.accountSelection.clearSelection()
      else options.accountSelection.removeSelectedIds(completedIds)
      await options.loadData({ silentErrorToast: true })
    } catch (error) {
      options.bulkProgress.fail(
        targetCount,
        Number(options.bulkProgress.refreshProgress.value?.processed || 0),
        options.normalizeErrorMessage(error),
      )
      options.setError(`${actionMeta.title}Failed`, error, false)
      await options.loadData({ silentErrorToast: true })
    } finally {
      options.bulkProgress.end()
    }
  }

  async function bindSelectedAccountsToGroup() {
    const useSelectionScope = options.accountSelection.scopedSelectionActive.value
    if (useSelectionScope && !await options.reconcileSelection()) return
    const targetIds = uniqueIds(options.accountSelection.selectedIds.value)
    const targetCount = useSelectionScope ? options.accountSelection.selectedCount.value : targetIds.length
    const target: AccountSelectionTarget = useSelectionScope
      ? options.accountSelection.selectionScope.value
      : targetIds
    if (!targetCount) {
      toast.warning('Select an account first.')
      return
    }
    const nextGroupId = options.selectedBindGroupId.value === '__ungrouped__' ? '' : options.selectedBindGroupId.value.trim()
    if (options.selectedBindGroupId.value !== '__ungrouped__' && !nextGroupId) {
      toast.warning('Select an account group to bind first.')
      return
    }
    const groupName = nextGroupId
      ? options.accountGroups.value.find((group) => group.id === nextGroupId)?.name || nextGroupId
      : 'Ungrouped'
    const confirmed = await confirmDialog.ask({
      title: 'Batch bind account group',
      message: `Bind the selected ${targetCount} accounts to ${groupName}?`,
      confirmText: 'Confirm binding',
      cancelText: 'Cancel',
    })
    if (!confirmed) return

    await options.bulkProgress.start('Batch bind account group', targetCount, 'mutation')
    try {
      const result = await accountsApi.bindGroup(target, nextGroupId)
      const updatedIds = uniqueIds(result.updated_ids || [])
      const removedIds = uniqueIds(result.removed_ids || [])
      const completedIds = uniqueIds([...updatedIds, ...removedIds])
      options.applyAccountGroupsPayload({ groups: result.groups, proxy_groups: options.proxyGroups.value })
      if (!result.progress) throw new Error('Account action response is missing its progress projection.')
      options.bulkProgress.finish(result.progress)
      if (useSelectionScope) options.accountSelection.clearSelection()
      else options.accountSelection.removeSelectedIds(completedIds)
      await options.loadData({ silentErrorToast: true })
    } catch (error) {
      options.bulkProgress.fail(targetCount, 0, options.normalizeErrorMessage(error))
      options.setError('Batch account group binding failed.', error, false)
    } finally {
      options.bulkProgress.end()
    }
  }

  function requestStopRefreshProgress() {
    options.bulkProgress.requestStop()
  }

  return {
    requestStopRefreshProgress,
    runBulkAction,
    bindSelectedAccountsToGroup,
  }
}
