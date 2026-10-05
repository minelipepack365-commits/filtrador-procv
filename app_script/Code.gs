/*******************************************************************
 * ⚡ Filtrador PROCV — Backend para Google Apps Script
 *
 * COMO PUBLICAR:
 *   1. Crie um projeto novo em script.google.com.
 *   2. Apague o Code.gs padrão e cole o conteúdo deste arquivo.
 *   3. Crie um arquivo HTML novo, renomeie para "index"
 *      e cole o conteúdo de app_script/index.html.
 *   4. Importante: faça upload do arquivo "xlsx.full.min.js"
 *      (está na pasta do app) para a raiz do seu Google Drive.
 *      O app usa essa biblioteca para ler os Excel/CSV.
 *   5. Deploy → New deployment → Web app
 *      - Execute as: "User accessing the web app"
 *      - Who has access: "Anyone" ou "Anyone with Google account"
 *   6. Use a URL gerada. Pronto!
 *
 * Os processos salvos ficam no servidor (Script Properties) e são
 * compartilhados entre quem usa a mesma URL. Para uso pessoal ok.
 * (Nada é enviado/não fica na sua planilha.)
 *******************************************************************/

function doGet() {
  const html = HtmlService.createHtmlOutputFromFile('index')
    .setTitle('⚡ Filtrador PROCV')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
    .addMetaTag('viewport', 'width=device-width, initial-scale=1.0');
  return html;
}

const SS_KEY = 'filtrador_procv_processos_v1';

/**
 * Retorna o código JS da biblioteca SheetJS (lida do Google Drive).
 * Procura pelo arquivo "xlsx.full.min.js" na raiz do Drive.
 * Dica: dá para acelerar depois salvando o ID do arquivo em
 * Script Properties ("SHEETJS_ID") e trocando a busca.
 */
function getSheetJSSource() {
  var cached = CacheService.getScriptCache().get('sheetjs_src');
  if (cached) return cached;
  var id = PropertiesService.getScriptProperties().getProperty('SHEETJS_ID');
  var file = null;
  if (id) {
    try { file = DriveApp.getFileById(id); } catch (e) {}
  }
  if (!file) {
    var it = DriveApp.getFilesByName('xlsx.full.min.js');
    if (!it.hasNext()) {
      throw new Error('Arquivo "xlsx.full.min.js" não encontrado no seu Drive. Envie-o para a raiz do Drive e recarregue.');
    }
    file = it.next();
  }
  var src = file.getBlob().getDataAsString();
  CacheService.getScriptCache().put('sheetjs_src', src, 21600);
  return src;
}

/**
 * Retorna a lista de processos salvos (JSON string) — ou '[]'.
 */
function listProcesses() {
  return PropertiesService.getScriptProperties().getProperty(SS_KEY) || '[]';
}

/**
 * Substitui toda a lista de processos pelo JSON enviado pelo cliente.
 */
function saveProcessList(jsonList) {
  try {
    const parsed = JSON.parse(jsonList);
    if (!Array.isArray(parsed)) throw new Error('esperado array');
    PropertiesService.getScriptProperties().setProperty(SS_KEY, jsonList);
    return true;
  } catch (e) {
    throw new Error('JSON de processos inválido: ' + e.message);
  }
}

/**
 * (Opcional) força exclusão de um processo pelo nome.
 */
function deleteProcess(nome) {
  let list = [];
  try { list = JSON.parse(listProcesses() || '[]'); } catch (e) {}
  list = list.filter(function (p) { return p.nome !== nome; });
  PropertiesService.getScriptProperties().setProperty(SS_KEY, JSON.stringify(list));
  return true;
}