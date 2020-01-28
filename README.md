# Bezpieczna aplikacja webowa

### Wymagania dot. bezpieczeństwa

- [x] Ścisła weryfikacja wszystkich formularzy,
- [x] Szyfrowanie haseł użytkowników metodą wielokrotnego hashowania z solą,
- [x] Możliwe ograniczenie widoczności notatek do samego siebie (prywatne)
      lub konkretnych osób (publiczne),
- [x] Komunikacja przeglądarka <-> web poprzez protokół HTTPS,
- [x] Możliwość zmiany hasła,
- [x] Ochrona formularzy przed atakami XSRF,
- [x] Lakoniczne komunikaty o błędach dla formularza logowania oraz pola
      starego hasła w formularzu zmiany hasła,
- [x] Bezpieczne ciasteczko sesji z flagami `HttpOnly` oraz `Secure`,
- [x] Zabezpieczenie przed atakami brute-force/DDOS.

### Funkcjonalność serwisu

- [x] Dodawanie notatki,
- [x] Wyświetlanie notatek chronologicznie według daty dodania,
- [x] Ograniczanie widoczności notatki do konkretnych użytkowników,
- [x] Każda notatka opatrzona informacjami o właścicielu, kontach zewnętrznych
      oraz dacie dodania,
- [x] Identyczna notatka nie będzie drugi raz umieszczana na serwerze.
      Zamiast tego serwer nada starej notatce nową datę i wyświetli na samej 
      górze listy,
- [x] Możliwość dodania widoczności notatki jedynie dla użytkowników, 
      którzy istnieją na serwerze.