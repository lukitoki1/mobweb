# Kamień milowy nr 2
## Aplikacja do przechowywania plików

Serwery aplikacji mają adresy odpowiednio:
* https://web.company.com
* https://cdn.company.com

Aby wysłanie zapytania było możliwe, należy w swoim systemie operacyjnym
zmapować powyższe adresy na localhost.

Następnie należy ustawić się w terminalu w korzeniu projektu i uruchomić 
środowisko za pomocą komendy:

```
docker-compose -f "docker-compose.yml" up -d --build  
```

Aplikacja dostępna jest pod adresem https://web.company.com.

Przykładowe dane logowania umieszczone w bazie:
* login: admin
* hasło: admin

Komentarz: Jako twórca strony jestem świadom, iż nie reprezentuje ona sobą wysokich walorów
estetycznych, lecz moim głównym założeniem przy jej rozwoju było stworzenie
solidnego serwera, który w następnym kamieniu milowym będę mógł ozdobić
dowolnym frameworkiem.