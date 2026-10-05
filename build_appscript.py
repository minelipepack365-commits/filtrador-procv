# Gera app_script/index.html (versão leve para Google Apps Script).
#
# Diferente da versão standalone (que usa <script src="xlsx.full.min.js">),
# a versão do Apps Script:
#   - remove a tag <script src=...> (CSP do Apps Script bloqueia CDNs);
#   - injeta um carregador que busca a biblioteca SheetJS no Google Drive
#     via google.script.run antes de interagir com planilhas.
#   - remove os blocos PWA (manifest, service worker e botão instalar):
#     o HtmlService serve a página num iframe sandboxed, onde service worker
#     não é permitido e manifest/ícones não podem ser hospedados.
#
# Requisitos em tempo real:
#   - Upload de "xlsx.full.min.js" na raiz do Google Drive.
#
# Uso:  python build_appscript.py

import os
import re

base = os.path.dirname(os.path.abspath(__file__))

# Marcadores usados no index.html para o bloco ser removido com segurança.
PWA_BLOCKS = [
    ('<!-- PWA:HEAD:START -->', '<!-- PWA:HEAD:END -->'),
    ('/* PWA:CSS:START */', '/* PWA:CSS:END */'),
    ('<!-- PWA:BODY:START -->', '<!-- PWA:BODY:END -->'),
    ('// PWA:JS:START', '// PWA:JS:END'),
]

def read(name):
    with open(os.path.join(base, name), encoding='utf-8') as f:
        return f.read()

def write(name, content):
    with open(os.path.join(base, name), 'w', encoding='utf-8') as f:
        f.write(content)

def strip_pwa(h):
    for start, end in PWA_BLOCKS:
        pattern = re.escape(start) + r'.*?' + re.escape(end) + r'\n?'
        h, n = re.subn(pattern, '', h, flags=re.S)
        if n:
            print('   remove %-24s (%d bloco)' % (start.strip('<!--*/ '), n))

    # <link rel="manifest"> e <link rel="icon"> não têm o que hospedar lá.
    h = re.sub(r'<link rel="(manifest|icon|apple-touch-icon)"[^>]*>\n?', '', h)
    return h

h = read('index.html')

# 0. Remove blocos PWA
h = strip_pwa(h)

# 1. Remove o script externo do SheetJS
ext = '<script src="xlsx.full.min.js"></script>'
assert ext in h, 'tag externa nao encontrada'
h = h.replace(ext, '')

# 2. Injeta o carregador dinâmico (busca no Drive quando hospedado)
loader = r"""<script>
  function loadSheetJSLib(cb) {
    if (window.XLSX) { cb(); return; }
    if (typeof google === 'undefined' || !google.script || !google.script.run) { cb(); return; }
    google.script.run
      .withSuccessHandler(function (src) {
        try {
          var s = document.createElement('script');
          s.textContent = src;
          document.head.appendChild(s);
        } catch (e) {}
        cb();
      })
      .withFailureHandler(function (e) {
        toast('⚠ ' + e.message, true);
      })
      .getSheetJSSource();
  }
</script>"""
head_close = '</head>'
assert head_close in h
h = h.replace(head_close, loader + '\n' + head_close, 1)

# 3. Bloqueia interação antes da biblioteca estar pronta (abrir arquivos)
old_file_open = "$('fileInput').addEventListener('change', async (e) => {"
new_file_open = ("$('fileInput').addEventListener('change', async (e) => {\n"
                 "  if (!window.XLSX) { toast('Aguarde a biblioteca carregar…', true); e.target.value = ''; return; }")
assert old_file_open in h
h = h.replace(old_file_open, new_file_open, 1)

# 4. Bloqueia exportação antes da biblioteca pronta
old_exp = "function exportResult(fmt) {\n  if (!state.result) { toast('Execute o processo antes de exportar.', true); return; }"
new_exp = ("function exportResult(fmt) {\n"
           "  if (!window.XLSX) { toast('Aguarde a biblioteca carregar…', true); return; }\n"
           "  if (!state.result) { toast('Execute o processo antes de exportar.', true); return; }")
assert old_exp in h
h = h.replace(old_exp, new_exp, 1)

# 5. Gatilho de inicialização
old_boot = "\nrenderFiles();\nrenderSteps();\nrenderProcessList();\nloadProcsFromServer();"
new_boot = """
function bootApp() {
  renderFiles();
  renderSteps();
  renderProcessList();
  loadProcsFromServer();
  toast(window.XLSX ? '✔ Pronto! Abra suas planilhas.' : '✔ Pronto!');
}
loadSheetJSLib(bootApp);"""
assert old_boot in h
h = h.replace(old_boot, new_boot, 1)

write(os.path.join('app_script', 'index.html'), h)
print('OK — app_script/index.html gerado: %.0f KB' % (len(h.encode('utf-8')) / 1024))