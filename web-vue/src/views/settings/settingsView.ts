import type { BackupState } from '@/api/settings'
import type { Settings, SettingsFieldMetadata } from '@/types/api'

export type SettingsSelectOption = {
  label: string
  value: string
}

export type SettingsApiDocItem = {
  title: string
  method: string
  path: string
  description: string
  example: string
}

export type NumberSettingOptions = {
  integer?: boolean
  metadata?: () => SettingsFieldMetadata | null | undefined
  enabled?: () => boolean
}

export type SettingsFields = Record<string, SettingsFieldMetadata>

const dateTimeFormatter = new Intl.DateTimeFormat('en-US', {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
})

export const settingsTabs: SettingsSelectOption[] = [
  { value: 'basic', label: 'Basic configuration' },
  { value: 'storage', label: 'Image storage and review' },
  { value: 'prompts', label: 'Prompt sources' },
  { value: 'backup', label: 'R2 backups' },
  { value: 'keys', label: 'User keys' },
  { value: 'api-docs', label: 'API access' },
  { value: 'canvas', label: 'External services' },
  { value: 'cpa', label: 'CPA' },
  { value: 'sub2api', label: 'Sub2API' },
]

const settingsOptionLabels: Record<string, Record<string, string>> = {
  image_upscale_engine: {
    sharp_lanczos3: 'Sharp / Lanczos3',
    pillow_lanczos: 'Pillow / Lanczos',
  },
  'image_storage.mode': {
    local: 'Local only',
    webdav: 'WebDAV only',
    both: 'Local + WebDAV',
  },
  'backup.include': {
    image_tasks: 'Image task records',
    editable_files: 'PPT / PSD files',
    images: 'Image file directory',
  },
}

export function settingsField(
  fields: SettingsFields | null | undefined,
  path: string,
): SettingsFieldMetadata | null {
  return fields?.[path] || null
}

export function settingsFieldReadOnly(
  fields: SettingsFields | null | undefined,
  path: string,
): boolean {
  return Boolean(settingsField(fields, path)?.read_only)
}

export function settingsFieldOptions(
  fields: SettingsFields | null | undefined,
  path: string,
  currentValue?: unknown,
): SettingsSelectOption[] {
  const values = [...(settingsField(fields, path)?.options || [])]
  const currentValues = Array.isArray(currentValue) ? currentValue : [currentValue]
  for (const currentValueItem of currentValues) {
    const current = String(currentValueItem ?? '').trim()
    if (current && !values.includes(current)) values.unshift(current)
  }
  const labels = settingsOptionLabels[path] || {}
  return Array.from(new Set(values)).map((value) => ({
    value,
    label: labels[value] || value,
  }))
}

export function settingsBooleanFieldOptions(
  fields: SettingsFields | null | undefined,
  prefix: string,
  currentValues: Record<string, boolean>,
): SettingsSelectOption[] {
  const values = Object.keys(fields || {})
    .filter((path) => path.startsWith(prefix))
    .map((path) => path.slice(prefix.length))
  for (const value of Object.keys(currentValues)) {
    if (!values.includes(value)) values.push(value)
  }
  const labelGroup = prefix.replace(/\.$/, '')
  const labels = settingsOptionLabels[labelGroup] || {}
  return values.map((value) => ({ value, label: labels[value] || value }))
}

export function backupStatusText(state: BackupState | null | undefined) {
  if (!state) return 'Not loaded'
  if (state.running) return 'Backing up'
  if (state.last_status === 'success') return 'Most recent success'
  if (state.last_status === 'error') return 'Most recent failure'
  return state.last_status || 'Not run'
}

export function formatBytes(value: unknown) {
  const bytes = Number(value) || 0
  if (bytes <= 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex += 1
  }
  return `${size.toFixed(unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`
}

export function formatDateTime(value: unknown) {
  const raw = String(value || '').trim()
  if (!raw) return '-'
  const parsed = new Date(raw)
  if (Number.isNaN(parsed.getTime())) return raw
  return dateTimeFormatter.format(parsed)
}

export function settingsFingerprint(value: Settings | null | undefined): string {
  return value ? JSON.stringify(value) : ''
}

export function buildApiDocItems(serviceBaseUrl: string, currentApiKey: string): SettingsApiDocItem[] {
  const cleanServiceBaseUrl = String(serviceBaseUrl || '').replace(/\/$/, '')
  const openAIBaseUrl = `${cleanServiceBaseUrl}/v1`
  return [
    {
      title: 'Model list',
      method: 'GET',
      path: '/v1/models',
      description: 'Returns a list of OpenAI-compatible models.',
      example: `curl ${openAIBaseUrl}/models \\\n  -H "Authorization: Bearer ${currentApiKey}"`,
    },
    {
      title: 'Chat completions',
      method: 'POST',
      path: '/v1/chat/completions',
      description: 'OpenAI-compatible chat completions endpoint. Also parses parameters such as n for image-compatible requests.',
      example: `curl ${openAIBaseUrl}/chat/completions \\\n  -H "Content-Type: application/json" \\\n  -H "Authorization: Bearer ${currentApiKey}" \\
  -d '{"model":"gpt-5-mini","messages":[{"role":"user","content":"Hello"}]}'`,
    },
    {
      title: 'Responses',
      method: 'POST',
      path: '/v1/responses',
      description: 'Accepts the compatible Responses input format, including text and tool calls.',
      example: `curl ${openAIBaseUrl}/responses \\\n  -H "Content-Type: application/json" \\\n  -H "Authorization: Bearer ${currentApiKey}" \\
  -d '{"model":"gpt-5-mini","input":"Generate an image of a futuristic city"}'`,
    },
    {
      title: 'Messages',
      method: 'POST',
      path: '/v1/messages',
      description: 'Anthropic Messages-compatible endpoint. Supports Authorization Bearer or x-api-key authentication.',
      example: `curl ${openAIBaseUrl}/messages \\\n  -H "Content-Type: application/json" \\\n  -H "Authorization: Bearer ${currentApiKey}" \\
  -d '{"model":"gpt-5-mini","max_tokens":1024,"messages":[{"role":"user","content":"Hello"}]}'`,
    },
    {
      title: 'Web search',
      method: 'POST',
      path: '/v1/search',
      description: 'Local search-compatible endpoint. Returns answer and sources.',
      example: `curl ${openAIBaseUrl}/search \\\n  -H "Content-Type: application/json" \\\n  -H "Authorization: Bearer ${currentApiKey}" \\
  -d '{"prompt":"Today's OpenAI news"}'`,
    },
    {
      title: 'Image generation',
      method: 'POST',
      path: '/v1/images/generations',
      description: 'Image generation endpoint. Supports prompt, model, n, size, quality, and other parameters.',
      example: `curl ${openAIBaseUrl}/images/generations \\\n  -H "Content-Type: application/json" \\\n  -H "Authorization: Bearer ${currentApiKey}" \\
  -d '{"model":"gpt-image-2","prompt":"A minimalist product poster","n":1}'`,
    },
    {
      title: 'Image editing',
      method: 'POST',
      path: '/v1/images/edits',
      description: 'Image editing endpoint. Supports multipart reference image uploads.',
      example: `curl ${openAIBaseUrl}/images/edits \\\n  -H "Authorization: Bearer ${currentApiKey}" \\
  -F "model=gpt-image-2" \\
  -F "prompt=Turn this into a cyberpunk night scene" \\
  -F "image=@./input.png"`,
    },
    {
      title: 'Create an editable file task',
      method: 'POST',
      path: '/v1/editable-file-tasks',
      description: 'Unified endpoint for creating PPT/PSD file tasks. Set kind to ppt or psd.',
      example: `curl ${openAIBaseUrl}/editable-file-tasks \\\n  -H "Content-Type: application/json" \\\n  -H "Authorization: Bearer ${currentApiKey}" \\
  -d '{"kind":"ppt","prompt":"Create a product launch presentation"}'`,
    },
    {
      title: 'Query an editable file task',
      method: 'GET',
      path: '/v1/editable-file-tasks?ids={taskId1,taskId2}',
      description: 'Check the generation status of a PPT/PSD file task by task ID.',
      example: `curl "${openAIBaseUrl}/editable-file-tasks?ids=task_1,task_2" \\\n  -H "Authorization: Bearer ${currentApiKey}"`,
    },
    {
      title: 'PPT generation task',
      method: 'POST',
      path: '/v1/ppt/generations',
      description: 'Create a PPT generation task directly. Use the returned task ID to check its status.',
      example: `curl ${openAIBaseUrl}/ppt/generations \\\n  -H "Content-Type: application/json" \\\n  -H "Authorization: Bearer ${currentApiKey}" \\
  -d '{"prompt":"Generate a market analysis presentation"}'`,
    },
    {
      title: 'PSD generation task',
      method: 'POST',
      path: '/v1/psd/generations',
      description: 'Create a PSD generation task directly. Use the returned task ID to check its status.',
      example: `curl ${openAIBaseUrl}/psd/generations \\\n  -H "Content-Type: application/json" \\\n  -H "Authorization: Bearer ${currentApiKey}" \\
  -d '{"prompt":"Generate an e-commerce poster PSD"}'`,
    },
    {
      title: 'File download',
      method: 'GET',
      path: '/files/{file_path}',
      description: 'Download files or archives generated by PPT/PSD tasks. No authentication required.',
      example: `curl ${cleanServiceBaseUrl}/files/{file_path}`,
    },
  ]
}
