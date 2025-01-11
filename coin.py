import requests
import time

# Botunuzun Token'ı
telegram_token = '7566212163:AAGkBtmUz83yMHhJ9mEPjk4vvCag39DhZpg'
chat_id = '-4613991177'  # Buraya kendi chat ID'nizi koyun

# Binance API'den coinlerin 24 saatlik değişim yüzdelerini almak için
def get_binance_market_data():
    url = 'https://api.binance.com/api/v3/ticker/24hr'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Binance API'den veri alınamadı! Status code:", response.status_code)
        return []

# Binance API'den coinlerin 30 dakikalık fiyat bilgilerini almak için
def get_binance_half_hour_data(symbol):
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval=30m&limit=2'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"{symbol} için 30 dakikalık veriler alınamadı! Status code:", response.status_code)
        return []

# Telegram üzerinden mesaj gönderme fonksiyonu
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    params = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("Mesaj gönderildi!")
    else:
        print("Telegram mesajı gönderilemedi! Status code:", response.status_code)

# Mesajı 4096 karakterden uzun olmamak için parçalara ayıran fonksiyon
def send_long_message(message):
    max_length = 4096
    # Mesajı parçalara ayır
    for i in range(0, len(message), max_length):
        part = message[i:i+max_length]
        send_telegram_message(part)

# Binance'den alınan veriyi işleyip Telegram'a uygun formatta mesaj hazırlama
def prepare_message():
    market_data = get_binance_market_data()
    message = "Binance - 30 Dakikalık Değişimi %1 Artan Coinler (TRY ile işlem gören):\n\n"

    if not market_data:
        return message

    coin_changes = []

    for coin in market_data:
        symbol = coin['symbol']
        current_price = float(coin['lastPrice'])  # Şu anki fiyat
        
        # Sadece TRY ile işlem gören coin'leri listele (Örn: BTCTRY, ETHTRY)
        if 'TRY' in symbol:
            half_hour_data = get_binance_half_hour_data(symbol)  # 30 dakikalık fiyat bilgilerini al
            if half_hour_data:
                # 30 dakika önceki fiyat
                half_hour_ago_price = float(half_hour_data[0][4])  # 30 dakika önceki kapanış fiyatı
                
                # 30 dakikalık değişim oranını hesapla
                price_change_percent = ((current_price - half_hour_ago_price) / half_hour_ago_price) * 100
                
                print(f"{symbol} için 30 dakikalık değişim oranı: {price_change_percent:.2f}%")  # Konsol çıktısı ekledim

                # Eğer 30 dakikalık değişim %1'den fazla ise listele
                if price_change_percent >= 1:
                    coin_changes.append({
                        'symbol': symbol,
                        'current_price': current_price,
                        'half_hour_ago_price': half_hour_ago_price,
                        'price_change_percent': price_change_percent
                    })
            else:
                message += f"{symbol}: 30 dakikalık veri alınamadı.\n\n"

    # Coinleri %1'lik değişime göre sıralama
    coin_changes.sort(key=lambda x: x['price_change_percent'], reverse=True)

    if not coin_changes:
        return None  # Eğer coin yoksa None döner
    else:
        for coin in coin_changes:
            message += f"{coin['symbol']}: \n" \
                       f"- Şu Anki Fiyat: {coin['current_price']} TRY\n" \
                       f"- 30 Dakika Önceki Fiyat: {coin['half_hour_ago_price']} TRY\n" \
                       f"- 30 Dakikalık Değişim: {coin['price_change_percent']:.2f}%\n\n"

    return message

# Mesaj gönderme testi
def send_half_hourly_coin_updates():
    while True:
        message = prepare_message()
        
        if message:  # Eğer coin verisi varsa mesajı gönder
            send_long_message(message)  # Uzun mesajı bölerek gönder
        else:
            print("Veri bulunamadı, 1 dakika sonra tekrar denenecek...")
        
        time.sleep(60)  # 1 dakika bekle ve tekrar dene

# Testi çalıştır
send_half_hourly_coin_updates()
