# Kamień milowy nr 3
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
* login: admin
* hasło: admin

### Implementacja HATEOAS

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

### API obsługiwane przez serwer

Każde zapytanie do serwera API musi zostać opatrzone nagłówkiem `Authorization`,
który który stanowi login oraz hasło do usługi zaszyfrowany mechanizmem `HTTPBasicAuth`.

```http request
GET /files/list?pid=pid
```
`pid` opcjonalne; 

* brak `pid` zwróci listę wszystkich plików, 
* podanie pid zwróci pliki przypisane do publikacji o podanym ID,
* `pid=-1` zwróci listę plików nieprzypisanych do żadnej publikacji

```http request
GET /files/donwload?filename=filename
POST /files/upload
DELETE /files/delete?filename=filename
PATCH /files/attach?filename=filename&pid=pid
PATCH /files/detach?filename=filename
```

```http request
GET /publications/list
POST /publications/upload
DELETE /publications/delete?pid=pid
```

Usunięcię publikacji powoduje automatyczne odłączenie wszystkich jej plików.

```http request
GET /users/check
```

Sprawdzenie, czy użytkownik próbujący zakogować się do serwisu web znajduje się
w bazie użytkowników.