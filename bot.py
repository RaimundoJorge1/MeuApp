import telebot
import pg8000
import os

TOKEN = "8833233090:AAFtpLC7dzhljwdU3z-Dn2q8KJm9oubdDko"
bot = telebot.TeleBot(TOKEN)

def conectar():
    return pg8000.connect(
        host="localhost",
        user="postgres",
        password="Jorgea1980@",
        database="produtosdb",
        port=5433
    )
TOKEN = os.getenv("TOKEN")

def conectar():
    return pg8000.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT"))
    )
def preparar(valor):
    valor = valor.lower()
    valor = valor.replace(".", "").replace(",", "").replace(" ", "").replace("-", "")
    return f"%{valor}%"

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg,
        "Envie os filtros no formato:\n\n"
        "bitola;isolacao;tensao;cor;fabricante\n\n"
        "Exemplo:\n1.5;PVC;750;Preta;PHELPS DODGE"
    )

@bot.message_handler(func=lambda m: True)
def receber(msg):
    texto = msg.text.split(";")

    if len(texto) != 5:
        bot.reply_to(msg, "Formato inválido. Use:\nbitola;isolacao;tensao;cor;fabricante")
        return

    bitola, isolacao, tensao, cor, fabricante = texto

    conn = conectar()
    cur = conn.cursor()

    sql = """
        SELECT *
        FROM produtos
        WHERE 
            REPLACE(REPLACE(REPLACE(LOWER(Bitola), '.', ''), ',', ''), ' ', '') LIKE %s
        AND REPLACE(REPLACE(REPLACE(LOWER(Isolacao), '.', ''), ',', ''), ' ', '') LIKE %s
        AND REPLACE(REPLACE(REPLACE(LOWER(Tensao), '.', ''), ',', ''), ' ', '') LIKE %s
        AND REPLACE(REPLACE(REPLACE(LOWER(Cor_Isolacao), '.', ''), ',', ''), ' ', '') LIKE %s
        AND REPLACE(REPLACE(REPLACE(REPLACE(LOWER(Fabricante_Fantasia), '.', ''), ',', ''), ' ', ''), '-', '') LIKE %s
        LIMIT 20;
    """

    cur.execute(sql, (
        preparar(bitola),
        preparar(isolacao),
        preparar(tensao),
        preparar(cor),
        preparar(fabricante)
    ))

    linhas = cur.fetchall()
    colunas = [desc[0] for desc in cur.description]

    if not linhas:
        bot.reply_to(msg, "Nenhum resultado encontrado.")
        return

    resposta = ""
    for linha in linhas:
        item = dict(zip(colunas, linha))
        resposta += f"{item}\n\n"

    bot.reply_to(msg, resposta)

bot.infinity_polling()
