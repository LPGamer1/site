import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import mercadopago
import motor.motor_asyncio
import asyncio
import os
from aiohttp import web
from bson.objectid import ObjectId

# --- CONFIGURAÇÕES DO RENDER ---
TOKEN_DISCORD = os.environ.get("TOKEN_DISCORD")
TOKEN_MP = os.environ.get("TOKEN_MP")
MONGO_URL = os.environ.get("MONGO_URL")

# --- CONEXÕES ---
sdk = mercadopago.SDK(TOKEN_MP)
cluster = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = cluster["loja_bot"]
collection_produtos = db["produtos"]
collection_config = db["config"] # Nova coleção para salvar o visual

# --- BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- SERVIDOR WEB (ANTI-CRASH RENDER) ---
async def start_dummy_server():
    app = web.Application()
    app.add_routes([web.get('/', lambda request: web.Response(text="Bot Online!"))])
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Servidor Web rodando na porta {port}")

@bot.event
async def on_ready():
    print(f'🤖 Bot logado como {bot.user}')
    await start_dummy_server()

# ==========================================================
#      SISTEMA DE INTERAÇÃO (MENU E BOTÕES)
# ==========================================================

class DropdownProdutos(Select):
    def __init__(self, produtos_lista):
        options = []
        for produto in produtos_lista:
            # Garante que o ID é string para passar no value
            options.append(discord.SelectOption(
                label=produto["nome"], 
                description=f"R$ {produto['preco']:.2f}", 
                value=str(produto["_id"]), 
                emoji=produto.get("emoji", "🛒")
            ))
        super().__init__(placeholder="Selecione um produto...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # Aqui estava o problema: precisamos tratar erros
        try:
            produto_id = self.values[0]
            
            # Busca no banco convertendo string para ObjectId
            produto = await collection_produtos.find_one({"_id": ObjectId(produto_id)})
            
            if not produto:
                return await interaction.response.send_message("❌ Este produto não existe mais no estoque.", ephemeral=True)

            # Cria o carrinho visual
            embed = discord.Embed(title="🛒 Resumo do Pedido", color=0x2b2d31)
            embed.description = f"""
**Produto:** {produto['nome']}
**Valor:** R$ {produto['preco']:.2f}

Clique em **Ir para pagamento** para gerar o Pix automático.
            """
            # Envia a resposta (Ephemeral = só você vê)
            await interaction.response.send_message(
                embed=embed, 
                view=CarrinhoView(produto), 
                ephemeral=True
            )
        except Exception as e:
            print(f"Erro no callback: {e}")
            await interaction.response.send_message(f"❌ Ocorreu um erro interno: {e}", ephemeral=True)

class CarrinhoView(View):
    def __init__(self, produto):
        super().__init__(timeout=None)
        self.produto = produto

    @discord.ui.button(label="Ir para pagamento", style=discord.ButtonStyle.green, emoji="💸")
    async def pagar(self, interaction: discord.Interaction, button: Button):
        await gerar_pix(interaction, self.produto)

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancelar(self, interaction: discord.Interaction, button: Button):
        await interaction.message.delete()

# ==========================================================
#      SISTEMA DE PAGAMENTO (PIX)
# ==========================================================

async def gerar_pix(interaction, produto):
    await interaction.response.defer(ephemeral=True)
    
    try:
        payment_data = {
            "transaction_amount": float(produto['preco']),
            "description": f"Discord: {produto['nome']}",
            "payment_method_id": "pix",
            "payer": {"email": "cliente@discord.com"} 
        }

        req = sdk.payment().create(payment_data)
        payment = req["response"]
        
        if "id" not in payment:
            # Mostra o erro real do Mercado Pago se houver
            erro_mp = payment.get('message', 'Erro desconhecido')
            return await interaction.followup.send(f"❌ O Mercado Pago recusou a criação: {erro_mp}", ephemeral=True)

        qr_code = payment["point_of_interaction"]["transaction_data"]["qr_code"]
        payment_id = payment["id"]

        embed = discord.Embed(title="✅ Pix Gerado!", description="Copie o código abaixo e pague no app do seu banco.", color=0x00ff00)
        embed.set_thumbnail(url="https://http2.mlstatic.com/frontend-assets/ui-navigation/5.14.3/mercadopago/logo__large.png")
        
        await interaction.followup.send(content=f"```{qr_code}```", embed=embed, ephemeral=True)

        asyncio.create_task(verificar_pagamento(interaction, payment_id, produto))

    except Exception as e:
        await interaction.followup.send(f"Erro técnico ao gerar Pix: {str(e)}", ephemeral=True)

async def verificar_pagamento(interaction, payment_id, produto):
    # Verifica por 5 minutos
    for _ in range(60): 
        await asyncio.sleep(5)
        try:
            pay_status = sdk.payment().get(payment_id)["response"]
            if pay_status["status"] == "approved":
                try:
                    dm_embed = discord.Embed(title="📦 Entrega Confirmada!", color=0x00ff00)
                    dm_embed.description = f"Obrigado por comprar **{produto['nome']}**!\n\n**Acesse sua entrega:**\n{produto['entrega']}"
                    await interaction.user.send(embed=dm_embed)
                    aviso = "✅ Pagamento aprovado! Verifique sua DM."
                except discord.Forbidden:
                    aviso = "✅ Pagamento aprovado! (Sua DM está fechada, não consegui entregar o link)."
                
                await interaction.followup.send(aviso, ephemeral=True)
                return
        except:
            continue

# ==========================================================
#      COMANDOS DE ADMIN (CONFIGURAR E GERENCIAR)
# ==========================================================

@bot.command(name="config")
@commands.has_permissions(administrator=True)
async def configurar_painel(ctx, *, conteudo=None):
    """
    Edita o visual do painel.
    Uso: !config Título do Painel | Link do Banner | Descrição
    """
    if not conteudo:
        return await ctx.send("❌ Uso: `!config Título Novo | https://link.com/imagem.png | Descrição Nova`")
    
    try:
        dados = conteudo.split("|")
        # Pega os dados, usa um valor padrão se estiver faltando
        titulo = dados[0].strip()
        banner = dados[1].strip() if len(dados) > 1 else ""
        descricao = dados[2].strip() if len(dados) > 2 else "Selecione um produto abaixo."

        # Salva no MongoDB (Atualiza se existir, cria se não existir)
        # Usamos update_one com upsert=True
        await collection_config.update_one(
            {"_id": "painel_loja"}, 
            {"$set": {"titulo": titulo, "banner": banner, "descricao": descricao}}, 
            upsert=True
        )

        await ctx.send("✅ Configuração salva! Digite `!loja` para ver o novo visual.")
    
    except Exception as e:
        await ctx.send(f"❌ Erro ao salvar config: {e}")

@bot.command(name="add")
@commands.has_permissions(administrator=True)
async def adicionar_produto(ctx, *, conteudo):
    try:
        dados = conteudo.split("|")
        if len(dados) < 4:
            return await ctx.send("❌ Uso: `!add Nome | 1.00 | Link | Emoji`")
        
        novo_produto = {
            "nome": dados[0].strip(),
            "preco": float(dados[1].strip().replace(",", ".")),
            "entrega": dados[2].strip(),
            "emoji": dados[3].strip()
        }
        await collection_produtos.insert_one(novo_produto)
        await ctx.send("✅ Produto Adicionado!")
    except Exception as e:
        await ctx.send(f"Erro: {e}")

@bot.command(name="del")
@commands.has_permissions(administrator=True)
async def remover_produto(ctx, id_produto):
    try:
        res = await collection_produtos.delete_one({"_id": ObjectId(id_produto)})
        msg = "✅ Deletado!" if res.deleted_count > 0 else "❌ ID não achado."
        await ctx.send(msg)
    except:
        await ctx.send("❌ ID Inválido.")

@bot.command(name="estoque")
@commands.has_permissions(administrator=True)
async def listar_estoque(ctx):
    produtos = await collection_produtos.find().to_list(length=100)
    msg = "**Estoque:**\n"
    for p in produtos:
        msg += f"🆔 `{p['_id']}` : {p['nome']} (R$ {p['preco']})\n"
    await ctx.send(msg[:2000])

# ==========================================================
#      COMANDO LOJA (COM CARREGAMENTO DE CONFIG)
# ==========================================================

class LojaView(View):
    def __init__(self, produtos):
        super().__init__(timeout=None)
        self.add_item(DropdownProdutos(produtos))

@bot.command()
async def loja(ctx):
    # 1. Busca produtos
    produtos = await collection_produtos.find().to_list(length=100)
    if not produtos:
        return await ctx.send("⚠️ Loja vazia! Use `!add`.")

    # 2. Busca configuração visual do banco
    config = await collection_config.find_one({"_id": "painel_loja"})
    
    # Valores padrão se não tiver config salva
    titulo = config.get("titulo", "🛒 Loja de Produtos") if config else "🛒 Loja de Produtos"
    desc = config.get("descricao", "Selecione um item abaixo.") if config else "Selecione um item abaixo."
    banner = config.get("banner", "") if config else ""

    await ctx.message.delete()
    
    embed = discord.Embed(title=titulo, description=desc, color=0x2b2d31)
    
    # Valida e seta imagem apenas se tiver link
    if banner.startswith("http"):
        embed.set_image(url=banner)
    
    await ctx.send(embed=embed, view=LojaView(produtos))

bot.run(TOKEN_DISCORD)
