import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import mercadopago
import motor.motor_asyncio
import asyncio
import os
from aiohttp import web
from bson.objectid import ObjectId

# --- CONFIGURAÇÕES GERAIS ---

# No Render, essas chaves devem estar nas "Environment Variables"
TOKEN_DISCORD = os.environ.get("TOKEN_DISCORD")
TOKEN_MP = os.environ.get("TOKEN_MP")
MONGO_URL = os.environ.get("MONGO_URL")

# LINK DO SEU BANNER (A imagem amarela "TUDO POR 1 REAL")
# Coloque o link direto da imagem aqui (tem que terminar em .png ou .jpg)
BANNER_LINK = "https://cdn.discordapp.com/attachments/1446924629464715275/1446943992272126052/1765048714287.jpg?ex=6935d31a&is=6934819a&hm=8caabf0541ec43e1374106bc592cf799dc1f6e0fcda6f340e3e5a8eb3bbe59b1&"

# --- INICIALIZAÇÃO ---

# Mercado Pago
sdk = mercadopago.SDK(TOKEN_MP)

# MongoDB
cluster = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = cluster["loja_bot"]
collection_produtos = db["produtos"]

# Bot Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- SERVIDOR FALSO PARA O RENDER (FIX DO ERRO DE PORTA) ---
async def start_dummy_server():
    app = web.Application()
    app.add_routes([web.get('/', lambda request: web.Response(text="Bot Online e Operante!"))])
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Pega a porta que o Render oferece ou usa 8080
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Servidor Web (Keep-Alive) rodando na porta {port}")

@bot.event
async def on_ready():
    print(f'🤖 Bot logado como {bot.user}')
    # Inicia o servidor web junto com o bot
    await start_dummy_server()

# --- COMANDOS DE ADMINISTRAÇÃO (DISCORD) ---

@bot.command(name="add")
@commands.has_permissions(administrator=True)
async def adicionar_produto(ctx, *, conteudo):
    """
    Adiciona produto.
    Uso: !add Nome do Produto | 1.00 | Link da Entrega | 💻
    """
    try:
        dados = conteudo.split("|")
        if len(dados) < 4:
            return await ctx.send("❌ Uso incorreto! Exemplo:\n`!add Photoshop | 1.00 | https://link.com | 💿`")
        
        nome = dados[0].strip()
        preco = float(dados[1].strip().replace(",", "."))
        entrega = dados[2].strip()
        emoji = dados[3].strip()

        novo_produto = {
            "nome": nome,
            "preco": preco,
            "entrega": entrega,
            "emoji": emoji
        }

        await collection_produtos.insert_one(novo_produto)
        
        embed = discord.Embed(title="✅ Produto Adicionado!", color=0x00ff00)
        embed.add_field(name="Nome", value=nome)
        embed.add_field(name="Preço", value=f"R$ {preco:.2f}")
        await ctx.send(embed=embed)

    except ValueError:
        await ctx.send("❌ O preço deve ser um número (ex: 1.00 ou 5,50).")
    except Exception as e:
        await ctx.send(f"❌ Erro: {e}")

@bot.command(name="estoque")
@commands.has_permissions(administrator=True)
async def listar_estoque(ctx):
    """Lista produtos e seus IDs para remover"""
    produtos = await collection_produtos.find().to_list(length=100)
    
    if not produtos:
        return await ctx.send("Estoque vazio.")

    texto = "**📦 Estoque Atual (Use os IDs para deletar):**\n\n"
    for p in produtos:
        texto += f"🆔 `{p['_id']}`\n📌 **{p['nome']}** - R$ {p['preco']:.2f}\n\n"
        
    # Discord tem limite de 2000 caracteres, cuidado com estoques gigantes
    await ctx.send(texto[:2000])

@bot.command(name="del")
@commands.has_permissions(administrator=True)
async def remover_produto(ctx, id_produto):
    """Remove produto pelo ID. Uso: !del ID_DO_MONGO"""
    try:
        resultado = await collection_produtos.delete_one({"_id": ObjectId(id_produto)})
        if resultado.deleted_count > 0:
            await ctx.send("✅ Produto removido!")
        else:
            await ctx.send("❌ ID não encontrado.")
    except:
        await ctx.send("❌ ID inválido.")

# --- SISTEMA DA LOJA (INTERFACE) ---

class DropdownProdutos(Select):
    def __init__(self, produtos_lista):
        options = []
        for produto in produtos_lista:
            options.append(discord.SelectOption(
                label=produto["nome"], 
                description=f"R$ {produto['preco']:.2f}", 
                value=str(produto["_id"]),
                emoji=produto.get("emoji", "🛒")
            ))
        super().__init__(placeholder="Selecione um produto...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        produto_id = self.values[0]
        produto = await collection_produtos.find_one({"_id": ObjectId(produto_id)})
        
        if not produto:
            return await interaction.response.send_message("Produto não existe mais.", ephemeral=True)

        embed = discord.Embed(title="🛒 Resumo do Pedido", color=0x2b2d31)
        embed.description = f"**Produto:** {produto['nome']}\n**Valor:** R$ {produto['preco']:.2f}"
        embed.set_footer(text="Clique em 'Ir para pagamento' para gerar o Pix.")
        
        await interaction.response.send_message(
            embed=embed, 
            view=CarrinhoView(produto), 
            ephemeral=True
        )

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

# --- LÓGICA DE PAGAMENTO (MERCADO PAGO) ---

async def gerar_pix(interaction, produto):
    await interaction.response.defer(ephemeral=True)
    
    payment_data = {
        "transaction_amount": float(produto['preco']),
        "description": f"Discord: {produto['nome']}",
        "payment_method_id": "pix",
        "payer": {"email": "cliente@discord.com"} # Email genérico obrigatório
    }

    try:
        req = sdk.payment().create(payment_data)
        payment = req["response"]
        
        if "id" not in payment:
            return await interaction.followup.send("❌ Erro ao criar Pix. Tente novamente.", ephemeral=True)

        qr_code = payment["point_of_interaction"]["transaction_data"]["qr_code"]
        payment_id = payment["id"]

        embed = discord.Embed(title="✅ Pix Gerado!", description="Copie o código abaixo e pague no seu banco.", color=0x00ff00)
        embed.set_thumbnail(url="https://http2.mlstatic.com/frontend-assets/ui-navigation/5.14.3/mercadopago/logo__large.png")
        
        await interaction.followup.send(content=f"```{qr_code}```", embed=embed, ephemeral=True)

        # Inicia verificação em segundo plano
        asyncio.create_task(verificar_pagamento(interaction, payment_id, produto))

    except Exception as e:
        await interaction.followup.send(f"Erro: {str(e)}", ephemeral=True)

async def verificar_pagamento(interaction, payment_id, produto):
    # Verifica por 5 minutos (60 checks de 5 segundos)
    for _ in range(60): 
        await asyncio.sleep(5)
        try:
            pay_status = sdk.payment().get(payment_id)["response"]
            
            if pay_status["status"] == "approved":
                # Entrega na DM
                try:
                    dm_embed = discord.Embed(title="📦 Entrega Confirmada!", color=0x00ff00)
                    dm_embed.description = f"Obrigado por comprar **{produto['nome']}**!\n\n**Acesse aqui:**\n{produto['entrega']}"
                    await interaction.user.send(embed=dm_embed)
                    msg_final = "✅ Pagamento aprovado! Produto enviado na sua DM."
                except discord.Forbidden:
                    msg_final = "✅ Pagamento aprovado! Mas sua DM está fechada (não consegui entregar)."

                await interaction.followup.send(msg_final, ephemeral=True)
                return
        except:
            continue

# --- COMANDO PRINCIPAL (!loja) ---

class LojaView(View):
    def __init__(self, produtos):
        super().__init__(timeout=None)
        self.add_item(DropdownProdutos(produtos))

@bot.command()
async def loja(ctx):
    # Pega produtos do Mongo
    produtos = await collection_produtos.find().to_list(length=100)
    
    if not produtos:
        return await ctx.send("⚠️ A loja está vazia! Use `!add` para colocar produtos.")

    await ctx.message.delete()
    
    embed = discord.Embed(title="🛒 Bem-vindo à Loja", description="Selecione um item abaixo para comprar.", color=0x2b2d31)
    
    # Aplica o banner configurado lá no topo
    if BANNER_LINK.startswith("http"):
        embed.set_image(url=BANNER_LINK)
    
    await ctx.send(embed=embed, view=LojaView(produtos))

bot.run(TOKEN_DISCORD)
