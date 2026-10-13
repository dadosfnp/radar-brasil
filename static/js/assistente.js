/* Assistente Radar Brasil: widget de chat (templates/assistente/_widget.html).
   Conversa guardada no sessionStorage para sobreviver a troca de pagina. */
(function () {
    'use strict';

    var raiz = document.getElementById('as-root');
    if (!raiz) return;

    var botao = document.getElementById('as-botao');
    var painel = document.getElementById('as-painel');
    var lista = document.getElementById('as-mensagens');
    var vazio = document.getElementById('as-vazio');
    var form = document.getElementById('as-form');
    var entrada = document.getElementById('as-entrada');
    var enviar = form.querySelector('.as-enviar');
    var csrf = raiz.querySelector('[name=csrfmiddlewaretoken]').value;
    var CHAVE = 'as-conversa';
    var conversa = [];   /* [{papel: 'usuario'|'assistente', texto, fontes?}] */
    var ocupado = false;

    try { conversa = JSON.parse(sessionStorage.getItem(CHAVE)) || []; } catch (e) { conversa = []; }

    function salvar() {
        try { sessionStorage.setItem(CHAVE, JSON.stringify(conversa)); } catch (e) { /* modo privado */ }
    }

    function escapar(s) {
        return String(s).replace(/[&<>"']/g, function (c) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
        });
    }

    function urlSegura(u) {
        return typeof u === 'string' && (/^https?:\/\//.test(u) || /^\/[^/]/.test(u)) ? u : null;
    }

    /* Texto do modelo -> HTML seguro: escapa tudo, depois aplica negrito, listas "- ",
       paragrafos e troca [ID] por numero da fonte. */
    function formatar(texto, fontes) {
        var numero = {};
        (fontes || []).forEach(function (f, i) { numero[f.id] = i + 1; });
        var html = '', emLista = false;
        escapar(texto).split('\n').forEach(function (linha) {
            linha = linha.trim();
            linha = linha.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
            linha = linha.replace(/\[([PFL]\d+|MAPA)\]/g, function (m, id) {
                return numero[id] ? '<a class="as-cita" href="#" data-fonte="' + numero[id] + '">' + numero[id] + '</a>' : '';
            });
            if (/^[-*] /.test(linha)) {
                if (!emLista) { html += '<ul>'; emLista = true; }
                html += '<li>' + linha.slice(2) + '</li>';
                return;
            }
            if (emLista) { html += '</ul>'; emLista = false; }
            if (linha) html += '<p>' + linha + '</p>';
        });
        return html + (emLista ? '</ul>' : '');
    }

    function htmlFontes(fontes) {
        if (!fontes || !fontes.length) return '';
        var itens = fontes.map(function (f, i) {
            var url = urlSegura(f.url);
            var titulo = escapar(f.titulo);
            var externo = url && url.charAt(0) !== '/';
            var link = url
                ? '<a href="' + escapar(url) + '"' + (externo ? ' target="_blank" rel="noopener"' : '') + '>' + titulo + '</a>'
                : titulo;
            return '<li data-fonte="' + (i + 1) + '">' + link + ' <span class="as-fonte-eixo">(' + escapar(f.eixo) + ')</span></li>';
        }).join('');
        return '<div class="as-fontes"><p class="as-fontes-titulo">' + escapar(raiz.dataset.txtFontes) + '</p><ol>' + itens + '</ol></div>';
    }

    function adicionar(msg) {
        vazio.hidden = true;
        var el = document.createElement('div');
        if (msg.papel === 'usuario') {
            el.className = 'as-msg as-msg-usuario';
            el.textContent = msg.texto;
        } else if (msg.papel === 'erro') {
            el.className = 'as-msg as-msg-erro';
            el.textContent = msg.texto;
        } else {
            el.className = 'as-msg as-msg-assistente';
            el.innerHTML = formatar(msg.texto, msg.fontes) + htmlFontes(msg.fontes);
        }
        lista.appendChild(el);
        lista.scrollTop = lista.scrollHeight;
        return el;
    }

    function renderizar() {
        Array.prototype.slice.call(lista.querySelectorAll('.as-msg, .as-digitando')).forEach(function (n) { n.remove(); });
        vazio.hidden = conversa.length > 0;
        conversa.forEach(adicionar);
    }

    function abrir(aberto) {
        painel.hidden = !aberto;
        botao.setAttribute('aria-expanded', aberto);
        botao.setAttribute('aria-label', aberto ? botao.dataset.labelAberto : botao.dataset.labelFechado);
        if (aberto) { lista.scrollTop = lista.scrollHeight; entrada.focus(); } else { botao.focus(); }
    }

    function perguntar(texto) {
        texto = texto.trim();
        if (!texto || ocupado) return;
        ocupado = true;
        enviar.disabled = true;
        var historico = conversa.slice(-6).map(function (m) { return { papel: m.papel, texto: m.texto }; });
        conversa.push({ papel: 'usuario', texto: texto });
        salvar();
        adicionar(conversa[conversa.length - 1]);

        var aguarde = document.createElement('div');
        aguarde.className = 'as-digitando';
        aguarde.innerHTML = '<span class="as-pontos"><i></i><i></i><i></i></span>' + escapar(raiz.dataset.txtPensando);
        lista.appendChild(aguarde);
        lista.scrollTop = lista.scrollHeight;

        fetch(raiz.dataset.url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
            body: JSON.stringify({ pergunta: texto, historico: historico })
        })
            .then(function (r) { return r.json().catch(function () { return {}; }); })
            .then(function (dados) {
                if (dados.resposta) {
                    conversa.push({ papel: 'assistente', texto: dados.resposta, fontes: dados.fontes || [] });
                    salvar();
                    adicionar(conversa[conversa.length - 1]);
                } else {
                    adicionar({ papel: 'erro', texto: dados.erro || raiz.dataset.txtErro });
                }
            })
            .catch(function () { adicionar({ papel: 'erro', texto: raiz.dataset.txtErro }); })
            .then(function () {
                aguarde.remove();
                ocupado = false;
                enviar.disabled = false;
                entrada.focus();
            });
    }

    botao.addEventListener('click', function () { abrir(painel.hidden); });

    painel.addEventListener('click', function (e) {
        var acao = e.target.closest('[data-acao]');
        if (acao) {
            if (acao.dataset.acao === 'fechar') abrir(false);
            if (acao.dataset.acao === 'limpar') { conversa = []; salvar(); renderizar(); entrada.focus(); }
            if (acao.dataset.acao === 'expandir') {
                var exp = painel.classList.toggle('as-expandido');
                acao.setAttribute('aria-pressed', exp);
            }
            return;
        }
        var sugestao = e.target.closest('.as-sugestao');
        if (sugestao) { perguntar(sugestao.textContent); return; }
        var cita = e.target.closest('.as-cita');
        if (cita) {
            e.preventDefault();
            var item = cita.closest('.as-msg').querySelector('.as-fontes li[data-fonte="' + cita.dataset.fonte + '"]');
            if (item) item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    });

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        var texto = entrada.value;
        entrada.value = '';
        perguntar(texto);
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && !painel.hidden) abrir(false);
    });

    renderizar();
})();
