export type SearchSkillPromptInput = {
  baseUrl: string
}

export type SearchSkillRuntimeInput = {
  getBaseUrl: () => string
  loadRuntimeConfig: () => Promise<unknown>
}

function cleanBaseUrl(value: string) {
  return String(value || '').trim().replace(/\/+$/, '')
}

export function searchSkillEndpoint(baseUrl: string) {
  return `${cleanBaseUrl(baseUrl)}/v1/search`
}

export function buildSearchSkillDocument(input: SearchSkillPromptInput) {
  const endpoint = searchSkillEndpoint(input.baseUrl)

  return `---
name: chatgpt2api-search
description: Use when current web search is needed through this chatgpt2api server. Call the configured HTTP search endpoint with a prompt and return the answer with source URLs.
---

# ChatGPT2API Search

Use this skill when the user asks for current web search, online lookup, recent information, or source-backed answers.

## Request

POST ${endpoint}

Headers:

Authorization: Bearer \${CHATGPT2API_API_KEY}
Content-Type: application/json

JSON body:

{
  "prompt": "<search question>"
}

## Response handling

- Use \`answer\` as the main response.
- Include source URLs from \`sources\` when available.
- If the endpoint returns an error, summarize the error and ask whether to retry.

## Authentication

- Read the API key from the \`CHATGPT2API_API_KEY\` environment variable at request time.
- Never write the real API key into this skill file, prompts, logs, or source control.
- If the environment variable is missing, stop and ask the user to configure it before sending a request.

Set it before starting the client that runs this skill (replace \`<your-api-key>\`):

- PowerShell: \`$env:CHATGPT2API_API_KEY = '<your-api-key>'\`
- Bash / zsh: \`export CHATGPT2API_API_KEY='<your-api-key>'\``
}

export function buildSearchSkillInstallPrompt(input: SearchSkillPromptInput) {
  const document = buildSearchSkillDocument(input)

  return `Please install a local web-search skill on this machine.

Requirements:
1. Install this as a local skill according to the current environment's skill rules.
2. Skill name: chatgpt2api-search
3. File name: SKILL.md
4. Only create or update this skill file.
5. Do not write a real API key into the skill. It must read \`CHATGPT2API_API_KEY\` from the environment at runtime.

SKILL.md content:

\`\`\`markdown
${document}
\`\`\``
}

export async function loadSearchSkillInstallPrompt(input: SearchSkillRuntimeInput) {
  await input.loadRuntimeConfig()
  return buildSearchSkillInstallPrompt({
    baseUrl: input.getBaseUrl(),
  })
}
