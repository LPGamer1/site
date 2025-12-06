import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import mercadopago
import motor.motor_asyncio
import asyncio
import os

# --- CONFIGURAÇÕES DE AMBIENTE (RENDER) ---
# No Render, você configurará essas variáveis na aba "Environment"
TOKEN_DISCORD = os.environ.get("TOKEN_DISCORD")
TOKEN_MP = os.environ.get("TOKEN_MP")
MONGO_URL = os.environ.get("MONGO_URL") # Sua string de conexão do MongoDB Atlas

# Configurações
sdk = mercadopago.SDK(TOKEN_MP)
cluster = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = cluster["loja_bot"]
collection_produtos = db["produtos"]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- SISTEMA DE MENUS ---

class DropdownProdutos(Select):
    def __init__(self, produtos_lista):
        options = []
        for produto in produtos_lista:
            options.append(discord.SelectOption(
                label=produto["nome"], 
                description=f"Valor: R$ {produto['preco']:.2f}", 
                value=str(produto["_id"]), # O ID único do Mongo
                emoji=produto.get("emoji", "🛒")
            ))

        super().__init__(placeholder="Selecione um produto...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        from bson.objectid import ObjectId
        produto_id = self.values[0]
        
        # Busca o produto específico no banco
        produto = await collection_produtos.find_one({"_id": ObjectId(produto_id)})
        
        if not produto:
            return await interaction.response.send_message("Produto não encontrado.", ephemeral=True)

        embed = discord.Embed(title="🛒 Resumo de compras", color=0x2b2d31)
        embed.description = f"""
**Produtos**\n1x {produto['nome']}\n
**Preço**\nR$ {produto['preco']:.2f}\n
**Total**\nR$ {produto['preco']:.2f}
        """
        embed.set_footer(text="Aguardando pagamento...")
        
        await interaction.response.send_message(
            embed=embed, 
            view=CarrinhoView(produto), 
            ephemeral=True
        )

class CarrinhoView(View):
    def __init__(self, produto):
        super().__init__(timeout=None)
        self.produto = produto

    @discord.ui.button(label="Ir para o pagamento", style=discord.ButtonStyle.green, emoji="💸")
    async def pagar(self, interaction: discord.Interaction, button: Button):
        await gerar_pix(interaction, self.produto)

    @discord.ui.button(label="Cancelar carrinho", style=discord.ButtonStyle.red, emoji="🗑️")
    async def deletar(self, interaction: discord.Interaction, button: Button):
        await interaction.message.delete()

# --- INTEGRAÇÃO MERCADO PAGO ---

async def gerar_pix(interaction, produto):
    await interaction.response.defer(ephemeral=True)
    
    payment_data = {
        "transaction_amount": float(produto['preco']),
        "description": f"Compra: {produto['nome']}",
        "payment_method_id": "pix",
        "payer": {"email": "cliente_discord@test.com"}
    }

    try:
        payment_response = sdk.payment().create(payment_data)
        payment = payment_response["response"]
        
        # Verificação de erro do MP
        if "id" not in payment:
            return await interaction.followup.send("Erro ao comunicar com Mercado Pago.", ephemeral=True)

        qr_code = payment["point_of_interaction"]["transaction_data"]["qr_code"]
        payment_id = payment["id"]

        embed = discord.Embed(title="✅ Pagamento Gerado", description="Use o código abaixo para pagar.", color=0x00ff00)
        embed.set_thumbnail(url="https://http2.mlstatic.com/frontend-assets/ui-navigation/5.14.3/mercadopago/logo__large.png")
        
        view = View() # Botão decorativo ou funcional no futuro
        
        await interaction.followup.send(content=f"**Pix Copia e Cola:**\n```{qr_code}```", embed=embed, ephemeral=True)

        asyncio.create_task(verificar_pagamento(interaction, payment_id, produto))

    except Exception as e:
        await interaction.followup.send(f"Erro técnico: {str(e)}", ephemeral=True)

async def verificar_pagamento(interaction, payment_id, produto):
    # Verifica por 5 minutos (60 checks de 5s)
    for _ in range(60): 
        await asyncio.sleep(5)
        pagamento = sdk.payment().get(payment_id)["response"]
        
        if pagamento["status"] == "approved":
            try:
                embed_entrega = discord.Embed(title="📦 Entrega Confirmada!", color=0x00ff00)
                embed_entrega.description = f"Produto: **{produto['nome']}**\n\n**Acesse:**\n{produto['entrega']}"
                
                await interaction.user.send(embed=embed_entrega)
                await interaction.followup.send("✅ Pagamento aprovado! Verifique sua DM.", ephemeral=True)
            except:
                await interaction.followup.send("✅ Pago! Mas sua DM está fechada.", ephemeral=True)
            return

# --- COMANDO LOJA ---

class LojaView(View):
    def __init__(self, produtos):
        super().__init__(timeout=None)
        self.add_item(DropdownProdutos(produtos))

@bot.command()
async def loja(ctx):
    # Busca produtos do MongoDB
    produtos = await collection_produtos.find().to_list(length=100)
    
    if not produtos:
        return await ctx.send("A loja está vazia! Adicione produtos no MongoDB.")

    await ctx.message.delete()
    embed = discord.Embed(title="🛒 Loja de Aplicativos", description="Selecione seu produto abaixo.", color=0x2b2d31)
    # Coloque aqui o link do seu banner
    embed.set_image(url="https://media.discordapp.net/attachments/SEU_ID_AQUI/BANNER.png")
    
    await ctx.send(embed=embed, view=LojaView(produtos))

@bot.event
async def on_ready():
    print(f'Bot online: {bot.user}')

bot.run(TOKEN_DISCORD)
