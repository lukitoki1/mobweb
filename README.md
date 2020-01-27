# Kamień milowy nr 5

### Najważniejsze zmiany

* Modernizacja dostępu do zasobów poprzez API - implementacja struktury
  REST API odzwierciedlającej strukturę zasobów na serwerze,
* implementacja odpowiednich kodów oraz komunikatów błędów dla błędnych
  danych dostarczanych API,
* reagowanie komunikatem na problem związany z łącznością z API,
* ciasteczko `HttpOnly`.
  
### API

* Każde zapytanie do serwera API musi zostać opatrzone nagłówkiem `Authorization`,
który który zawiera token `JWT`. 
* Użytkownik może zapytać REST API wyłącznie 
o zasoby należące do użytkownika sprecyzowanego w żetonie (stąd brana jest informacja, 
czyj zasób zwrócić w odpowiedzi).

#### Obsługa plików

```http request
GET /files - lista
GET /files?type=<type> - lista z parametrem filtrowania
```
gdzie `type` to `all` lub `unattached`

```http request
GET /files/<fid> - pobranie
POST /files - wysłanie
DELETE /files/<fid> - usunięcie
```

#### Obsługa publikacji

```http request
GET /publications - lista
GET /publications/<pid> - informacje o konkretnej publikacji
POST /publications - wysłanie
DELETE /publications/<pid> - usunięcie

POST /publications/<pid>/files/<fid> - załączenie pliku
DELETE /publications/<pid>/files/<fid> - odłączenie pliku
```

Usunięcię publikacji powoduje automatyczne odłączenie wszystkich jej plików.

### Uruchomienie

Serwery aplikacji mają adresy odpowiednio:
* https://web.company.com
* https://cdn.company.com
* https://api.company.com

Aby wysłanie zapytania było możliwe, należy w swoim systemie operacyjnym
zmapować powyższe adresy na localhost.

Następnie należy ustawić się w terminalu w korzeniu projektu i uruchomić 
środowisko za pomocą komendy:

```
docker-compose -f "docker-compose.yml" up -d --build  
```

Aplikacja dostępna jest pod adresem https://web.company.com.

Przykładowe dane logowania umieszczone w bazie:
* login: `admin@gmail.com`
* hasło: `admin`

### Komunikaty

Mechanizm powiadamiania o dodanej publikacji opracowany został
na podstawie kodu z repozytorium `flask-redis-realtime-chat` udostępnianego
na licencji "BSD-3-Clause".

Link do repozytorium:
https://github.com/petronetto/flask-redis-realtime-chat 

Powiadomienia pojawiają się na stronie z listą publikacji.

### HATEOAS

Postanowiłem od zera zaimplementować własny mechanizm generowania informacji o linkach.
Za generowanie struktur HATEOAS odpowiedzialny jest serwer API.
Serwer API otrzymując zapytanie pod `/publications/list` generuje i zwraca pliki HAL według 
następującego schematu:

```python
[
    {
        'pid': '',
        'title': '',
        'authors': ['', '', ..., ''],
        'year': '',
        '_links':{
            'publication': {
                'delete': '/publications/delete?pid=...'
            },
            'files': {
                {
                    'filename': '',
                    'download': '/files/download?...',
                    'delete': '/files/delete?...'
                },
                ...      
            }   
        }     
    }
    ...
]
```