# CMS API (zadanie rekrutacyjne) 

Do napisania aplikacji użyte zostały:
  - python 3.10.10
  - Flask 2.2.3
  - Flask-SQLAlchemy==3.0.3
  - baza danych na silniku sqlite3
  - pytest 7.3.0
 
Aplikacja została napisana przy pomocy blueprintów, oddzielnego dla widoków oraz dla błędów. W celu operacji na bazie użyłem silnika ORM. Dla ułatwienia testów baza danych jest tworzona na nowo przy każdym uruchomieniu aplikacji.Jako że w dokumentacji nie jest opisana żadna metoda autoryzacji, przyjąłem za taką dostęp użytkownika z konkretnym id (dostarczanym z każdym requestem w obiekcie "source") do konkretnej strony. W przypadku nie istnienia lub nie zawierania relacji z zasobem nadrzędnym zwracany jest błąd (404). Za metode pozycjonowania albumów oraz zdjęć przyjąłem wysokość parametru sort, parametr ten jest też domyślny dla sortowania zpaginowanych albumów oraz zawartych w nich zdjęć. Nie było dla mnie jasne jaki jest dokładny cel ostatnich dwóch endpointów w dokumentacji (/site/<int:site_id>/module/subject/<string:row_prefix>/<int:row_id). W pierwszym przyjąłem wyszukiwanie wszystkich tematyk strony zaczynających się prefiksem (row_id zostało pominięte).
Drugi z endpointów pominąłem całkowicie.
