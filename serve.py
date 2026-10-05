# Servidor local para rodar o Filtrador PROCV como app instalavel.
#
# Service worker (necessario para instalar/funcionar offline) so funciona em
# contexto seguro: https:// ou http://localhost. Abrir o index.html com
# duplo clique (file://) nao instala.
#
# Uso:  python serve.py [porta]

import functools
import http.server
import os
import socketserver
import sys
import webbrowser

BASE = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

# Durante o desenvolvimento nao queremos cache velho no navegador.
NO_CACHE = ('index.html', 'sw.js', 'manifest.webmanifest')


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = dict(http.server.SimpleHTTPRequestHandler.extensions_map)
    extensions_map.update({
        '.webmanifest': 'application/manifest+json',
        '.js': 'text/javascript',
        '.mjs': 'text/javascript',
        '.json': 'application/json',
        '.css': 'text/css',
        '.svg': 'image/svg+xml',
        '.png': 'image/png',
        '.webp': 'image/webp',
    })

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=BASE, **kw)

    def end_headers(self):
        if self.path.lstrip('/').split('?')[0] in NO_CACHE:
            self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.send_header('Service-Worker-Allowed', '/')
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write('  %s\n' % (fmt % args))


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    url = 'http://localhost:%d/' % PORT
    with Server(('127.0.0.1', PORT), Handler) as httpd:
        print('')
        print('  Filtrador PROCV — app instalavel')
        print('  ---------------------------------------------')
        print('  URL:        %s' % url)
        print('  Instalar:   Chrome/Edge -> icone na barra de URL,')
        print('              ou o botao "Instalar app" no cabecalho.')
        print('  Encerrar:   Ctrl+C')
        print('')
        try:
            webbrowser.open(url)
        except Exception:
            pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\n  Encerrado.')


if __name__ == '__main__':
    main()