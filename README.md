# ⚡ Filtrador PROCV

App de automação de planilhas: abra arquivos `.xlsx`/`.xls`/`.csv`, monte um
pipeline de passos (filtrar, PROCV, ordenar, remover duplicados, escolher
colunas, coluna calculada, juntar abas) e exporte o resultado em Excel ou CSV.

Instalável como PWA — funciona offline.

## Como usar

| Ação | Passo |
|---|---|
| Abrir planilhas | botão **📂 Abrir planilhas** no cabeçalho |
| Criar um passo | **➕ Novo passo** → escolha o tipo e configure |
| Executar | **▶ Executar** |
| Exportar | **⬇ Excel** ou **⬇ CSV** |
| Salvar o processo | **💾 Criar processo** (sincroniza entre máquinas via `localStorage`/Apps Script) |

## Rodar localmente

Service worker exige contexto seguro (`https://` ou `http://localhost`).
Abrir o `index.html` com duplo clique (`file://`) **não** instala.

```bash
python serve.py
# abre http://localhost:8000/
```

## Instalar como app

1. Abra a URL do app no Chrome, Edge ou Safari.
2. **Chrome/Edge:** ícone de instalar na barra de URL, ou o botão
   **⬇ Instalar app** no cabeçalho do app.
3. **Safari (iOS):** Compartilhar → *Adicionar à Tela de Início*.

## Publicar no GitHub Pages

```bash
git init
git add .
git commit -m "Filtrador PROCV como PWA"
git branch -M main
git remote add origin https://github.com/<usuario>/<repo>.git
git push -u origin main
```

Depois, no repo: **Settings → Pages → Source: `main` / `/ (root)`**.
O app fica em `https://<usuario>.github.io/<repo>/`.

### Depois de publicar

- **Atualizar o app:** incremente `CACHE_VERSION` em `sw.js` e faça commit.
  Sem isso, quem já instalou pode continuar vendo a versão antiga.
- O arquivo `.nojekyll` evita que o Jekyll interfira no service worker.

## Estrutura

| Arquivo | Papel |
|---|---|
| `index.html` | app completo (fonte da verdade) |
| `sw.js` | service worker: precache + offline |
| `manifest.webmanifest` | metadados do PWA, ícones e atalhos |
| `icons/` | ícones 32/180/192/512 + maskable |
| `xlsx.full.min.js` | SheetJS (leitura/escrita de `.xlsx`) |
| `serve.py` | servidor local para desenvolvimento |
| `gen_icons.py` | regenera os ícones PNG |
| `build_appscript.py` | gera a versão para Google Apps Script |
| `app_script/` | versão Apps Script (`Code.gs` + `index.html`) |

### Google Apps Script

O `app_script/` é a variante que roda hospedado no Apps Script. Ela lê e grava
os processos no Google Drive, então precisa de `xlsx.full.min.js` enviado para
a raiz do Drive. `build_appscript.py` gera os arquivos a partir do
`index.html` da raiz, removendo o que não funciona lá (service worker e
manifest — o HtmlService serve num iframe sandboxed).

```bash
python build_appscript.py
```