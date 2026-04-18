import requests

# Buraya kopyaladığın YENI şifreyi yapıştır (Başında ve sonunda boşluk olmasın)
API_KEY = "RGAPI-07d68d0c-6b91-432d-a8dc-13780908d9a0"

# Doğrudan senin hesabına giden saf URL
url = "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/qardesh0/00000"

headers = {
    "X-Riot-Token": API_KEY
}

print("Riot sunucularına bağlanılıyor...")
response = requests.get(url, headers=headers)

print(f"Gelen Kod: {response.status_code}")
print(f"Riot'un Cevabı: {response.text}")