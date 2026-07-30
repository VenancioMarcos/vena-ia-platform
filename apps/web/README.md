# Vena_IA Web

Frontend da Vena_IA Platform.

## Stack

* Next.js
* React
* TypeScript
* Tailwind CSS

## Desenvolvimento

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm run dev
```

## Porta

```text
http://localhost:3000
```

## Sessão

O login em `/login` usa cookie HttpOnly emitido pela API. O frontend envia
`credentials: "include"` e trata respostas `401` e `403`; identidade e papel
continuam validados exclusivamente no backend.
