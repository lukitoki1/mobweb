# Kamień milowy nr 2
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
Serwer API otrzymując zapytanie pod `/publications/list` generuje pliki HAL według następującego schematu:

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

### API serwera API