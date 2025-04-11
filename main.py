import ccxt
import pandas as pd
import time
import requests

# === CONFIGURAÇÕES ===
PAR = 'XRP/USDT'
EMA_PERIODO = 50
INTERVALO = '1h'
TELEGRAM_TOKEN = '7860630935:AAHthiRVPAZanAW_QlRBk9WmleVLyu-lScE'
TELEGRAM_CHAT_ID = '397877740'
INTERVALO_VERIFICACAO = 60 * 60  # 1 hora

exchange = ccxt.bybit({
    'enableRateLimit': True,
})

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{7860630935:AAHthiRVPAZanAW_QlRBk9WmleVLyu-lScE}/sendMessage"
    payload = {
        "chat_id": 397877740,
        "text": mensagem
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

def obter_candles():
    dados = exchange.fetch_ohlcv(PAR, timeframe=INTERVALO, limit=EMA_PERIODO + 3)
    df = pd.DataFrame(dados, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['EMA50'] = df['close'].ewm(span=EMA_PERIODO, adjust=False).mean()
    return df

def verificar_sinal(df):
    vela_atual = df.iloc[-1]
    vela_anterior = df.iloc[-2]

    ema_anterior = vela_anterior['EMA50']
    ema_atual = vela_atual['EMA50']

    fechamento_anterior = vela_anterior['close']
    fechamento_atual = vela_atual['close']

    if fechamento_anterior < ema_anterior and fechamento_atual > ema_atual:
        return f"📈 SINAL DE COMPRA em {PAR}\nPreço: {fechamento_atual:.4f}\nEMA50: {ema_atual:.4f}"

    if fechamento_anterior > ema_anterior and fechamento_atual < ema_atual:
        return f"📉 SINAL DE VENDA em {PAR}\nPreço: {fechamento_atual:.4f}\nEMA50: {ema_atual:.4f}"

    return None

def main():
    print("🤖 Bot de sinais iniciado com BYBIT...")
    while True:
        try:
            df = obter_candles()
            sinal = verificar_sinal(df)
            if sinal:
                print(sinal)
                enviar_telegram(sinal)
            else:
                print("Nenhum sinal agora.")
        except Exception as e:
            print("Erro:", e)

        time.sleep(INTERVALO_VERIFICACAO)

if __name__ == "__main__":
    main()
