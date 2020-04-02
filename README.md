### Tagi `M2..M5` - aplikacja webowa (kolejne kroki rozwoju) na przedmiot "Programowanie aplikacji mobilnych i webowych".
### Tag `ochrona` - bezpieczna aplikacja webowa na przedmiot "Ochrona danych w systemach informatycznych".

## Kamień milowy M5

### Najważniejsze zmiany i poprawione błędy

* Modernizacja dostępu do zasobów poprzez API - implementacja struktury
  REST API odzwierciedlającej strukturę zasobów na serwerze (więcej niżej),
* reagowanie komunikatem na problem związany z łącznością z API,
* postawienie serwisu web na serwerze `gunicorn` z workerem `gevent`,
  co zapobiega blokowaniu serwera,
* ciasteczko `HttpOnly`.
  
### API

* Każde zapytanie do serwera API musi zostać opatrzone nagłówkiem `Authorization`,
który który zawiera token `JWT`. 
* Użytkownik może zapytać REST API wyłącznie 
o zasoby należące do użytkownika sprecyzowanego w żetonie (stąd brana jest informacja, 
czyj zasób zwrócić w odpowiedzi).
* Nazwy plików są unikalne w ramach pojedynczego użytkownika, dlatego służą
za ID plików.

#### Obsługa plików

```http request
GET /files - lista
GET /files?type=<type> - lista z parametrem filtrowania
```
gdzie `type` = `unattached` -> pliki nieprzypisane do żadnej publikacji

```http request
GET /files/<filename> - pobranie
POST /files - wysłanie
DELETE /files/<filename> - usunięcie
```

#### Obsługa publikacji

```http request
GET /publications - lista
GET /publications/<pid> - informacje o konkretnej publikacji
POST /publications - wysłanie
DELETE /publications/<pid> - usunięcie

PUT /publications/<pid>/files/<filename> - załączenie pliku
DELETE /publications/<pid>/files/<filename> - odłączenie pliku
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
                'delete': '/publications/<pid>'
            },
            'files': {
                {
                    'filename': '',
                    'download': '/files/<filename>',
                    'detach': '/publications/<pid>/files/<filename>'
                },
                ...      
            }   
        }     
    }
    ...
]
```
