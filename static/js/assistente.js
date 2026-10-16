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

    /* "Esta resposta foi útil?" com 👍/👎; o voto fica em msg.util e no servidor */
    function htmlFeedback(msg) {
        if (!msg.id) return '';
        var d = raiz.dataset;
        var botao = function (util, rotulo, classe) {
            return '<button type="button" class="as-voto ' + classe + '" data-util="' + util + '" aria-pressed="' +
                (msg.util === util) + '" aria-label="' + escapar(rotulo) + '" title="' + escapar(rotulo) + '">' +
                '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 10v11"/><path d="M15 5.9L14 10h5.8a2 2 0 0 1 1.9 2.5l-2.3 8A2 2 0 0 1 17.5 22H7a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.8a2 2 0 0 0 1.8-1.1L15 2a3.1 3.1 0 0 1 0 3.9z"/></svg></button>';
        };
        var texto = msg.util === undefined ? d.txtUtil : d.txtObrigado;
        return '<div class="as-feedback" data-id="' + msg.id + '"><span>' + escapar(texto) + '</span>' +
            botao(true, d.txtSim, 'as-voto-sim') + botao(false, d.txtNao, 'as-voto-nao') + '</div>';
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
            el.innerHTML = formatar(msg.texto, msg.fontes) + htmlFontes(msg.fontes) + htmlFeedback(msg);
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

    /* Mesma condicao do CSS: celular (em pe ou deitado) abre o painel em tela cheia */
    var telaCheia = window.matchMedia('(max-width: 600px), (max-height: 500px) and (pointer: coarse)');

    /* Teclado do celular: o painel acompanha a area visivel para o campo nao ficar escondido */
    function ajustarAoTeclado() {
        var vv = window.visualViewport;
        if (!vv || painel.hidden || !telaCheia.matches) { painel.style.height = painel.style.top = ''; return; }
        painel.style.top = vv.offsetTop + 'px';
        painel.style.height = vv.height + 'px';
    }
    if (window.visualViewport) {
        window.visualViewport.addEventListener('resize', ajustarAoTeclado);
        window.visualViewport.addEventListener('scroll', ajustarAoTeclado);
    }

    function abrir(aberto, peloVoltar) {
        /* Em tela cheia o "voltar" do celular fecha o chat em vez de sair da pagina */
        if (telaCheia.matches && !aberto && !peloVoltar && history.state && history.state.asPainel) {
            history.back();  /* o popstate abaixo fecha o painel */
            return;
        }
        if (telaCheia.matches && aberto && painel.hidden) history.pushState({ asPainel: true }, '');
        painel.hidden = !aberto;
        botao.setAttribute('aria-expanded', aberto);
        botao.setAttribute('aria-label', aberto ? botao.dataset.labelAberto : botao.dataset.labelFechado);
        document.documentElement.classList.toggle('as-travado', aberto && telaCheia.matches);
        ajustarAoTeclado();
        if (aberto) {
            lista.scrollTop = lista.scrollHeight;
            if (!telaCheia.matches) entrada.focus();  /* no celular o teclado so sobe ao tocar no campo */
        } else {
            botao.focus();
        }
    }

    window.addEventListener('popstate', function () { if (!painel.hidden) abrir(false, true); });

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
                    conversa.push({ papel: 'assistente', id: dados.id, texto: dados.resposta, fontes: dados.fontes || [] });
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
                if (!telaCheia.matches) entrada.focus();  /* no celular nao cobre a resposta com o teclado */
            });
    }

    function votar(voto) {
        var caixa = voto.closest('.as-feedback');
        var id = Number(caixa.dataset.id);
        var util = voto.dataset.util === 'true';
        var msg = conversa.filter(function (m) { return m.id === id; })[0];
        fetch(raiz.dataset.urlAvaliar, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
            body: JSON.stringify({ id: id, util: util })
        }).then(function (r) {
            if (!r.ok || !msg) return;
            msg.util = util;
            salvar();
            caixa.outerHTML = htmlFeedback(msg);
        }).catch(function () { /* sem rede: voto nao registrado, nada a fazer */ });
    }

    botao.addEventListener('click', function () { abrir(painel.hidden); });

    painel.addEventListener('click', function (e) {
        var voto = e.target.closest('.as-voto');
        if (voto) { votar(voto); return; }
        var acao = e.target.closest('[data-acao]');
        if (acao) {
            if (acao.dataset.acao === 'fechar') abrir(false);
            if (acao.dataset.acao === 'limpar') { conversa = []; salvar(); renderizar(); if (!telaCheia.matches) entrada.focus(); }
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
