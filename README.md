# Diet Planner

Diet Planner to aplikacja webowa w Django do planowania diety, liczenia kalorii i makroskladnikow, generowania list zakupow oraz monitorowania BMI.

## Stack

- Python 3.12
- Django 5
- SQLite
- Bootstrap 5
- Chart.js

## Moduly projektu

- `core` - strona glowna i dashboard
- `users` - rejestracja, logowanie i profil uzytkownika
- `meals` - baza dan, skladniki, ulubione i wlasne przepisy
- `planner` - planowanie posilkow na dni i tygodnie
- `shopping` - generowanie list zakupow
- `health` - BMI, BMR, TDEE i historia wagi

## Wymagania

Do uruchomienia projektu w czystym srodowisku potrzebujesz:

- Windows, Linux albo macOS
- Python 3.11 lub nowszy
- `pip`
- terminal, np. PowerShell

Najbezpieczniej uzyc Python 3.12.

## Najlatwiejszy start na Windows

Z katalogu projektu uruchom po prostu:

```powershell
.\start_project.bat
```

albo:

```powershell
powershell -ExecutionPolicy Bypass -File .\start_project.ps1
```

Skrypt:

- utworzy `.venv`, jesli go nie ma
- zainstaluje zaleznosci, jesli brakuje Django
- wykona `migrate`
- zaladuje `seed_data` przy pierwszym starcie
- odpali serwer Django w osobnym oknie
- otworzy aplikacje pod `http://127.0.0.1:8010/`

Jesli chcesz uruchomic serwer w tym samym terminalu, uzyj:

```powershell
.\start_project.ps1 -Foreground
```

Jesli port `8010` jest zajety, wybierz inny:

```powershell
.\start_project.ps1 -Port 8020
```

## Uruchomienie w czystym srodowisku

Wszystkie polecenia ponizej wykonuj z katalogu projektu:

```powershell
cd C:\Users\piotr\Desktop\ZZPO_Dieta\diet_project
```

### 1. Sprawdz, czy Python dziala

```powershell
python --version
```

Jesli komenda `python` nie dziala, a Python jest zainstalowany, sprobuj:

```powershell
py --version
```

albo podaj pelna sciezke do interpretera, np.:

```powershell
C:\Users\piotr\AppData\Local\Programs\Python\Python312\python.exe --version
```

### 2. Utworz srodowisko wirtualne

Jesli `python` dziala:

```powershell
python -m venv .venv
```

Jesli nie, a dziala pelna sciezka:

```powershell
C:\Users\piotr\AppData\Local\Programs\Python\Python312\python.exe -m venv .venv
```

### 3. Aktywuj srodowisko

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Po aktywacji w terminalu powinno pojawic sie `(.venv)`.

Jesli PowerShell blokuje skrypty, uruchom:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 4. Zainstaluj zaleznosci

```powershell
pip install -r requirements.txt
```

### 5. Wygeneruj migracje

```powershell
python manage.py makemigrations
```

### 6. Zastosuj migracje do bazy

```powershell
python manage.py migrate
```

### 7. Zaladuj dane startowe

Ta komenda doda:

- konto administratora
- konto demo
- przykladowe dania
- przykladowy szablon jadlospisu

```powershell
python manage.py seed_data
```

### 8. Uruchom serwer developerski

```powershell
python manage.py runserver 127.0.0.1:8010
```

### 9. Otworz aplikacje w przegladarce

```text
http://127.0.0.1:8010/
```

## Konta testowe

Po wykonaniu `python manage.py seed_data` dostepne beda:

- administrator: `admin` / `admin12345`
- uzytkownik demo: `demo` / `demo12345`

## Jak uruchomic projekt od zera - szybka wersja

Jesli wszystko dziala poprawnie, wystarczy:

```powershell
cd C:\Users\piotr\Desktop\ZZPO_Dieta\diet_project
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
python manage.py runserver 127.0.0.1:8010
```

## Struktura katalogow

```text
diet_project/
|-- manage.py
|-- requirements.txt
|-- README.md
|-- db.sqlite3
|-- diet_project/
|   |-- settings.py
|   |-- urls.py
|   |-- asgi.py
|   `-- wsgi.py
|-- core/
|-- users/
|-- meals/
|-- planner/
|-- shopping/
|-- health/
|-- templates/
`-- static/
```

## Co robi aplikacja

- rejestracja, logowanie, wylogowanie i reset hasla
- osobne konta i profile uzytkownikow
- limit kalorii i makroskladnikow na uzytkownika
- baza dan z filtrowaniem
- dodawanie wlasnych dan
- ulubione dania
- tygodniowy planer posilkow
- dzienny bilans kalorii, bialka, tluszczu i weglowodanow
- kopiowanie jadlospisu miedzy dniami
- szablony jadlospisow
- lista zakupow generowana z zaplanowanych dan
- kalkulator BMI, BMR i TDEE
- historia BMI i wpisow wagi

## Typowe problemy

### `python` otwiera Microsoft Store zamiast prawdziwego Pythona

Uzyj pelnej sciezki do interpretera, np.:

```powershell
C:\Users\piotr\AppData\Local\Programs\Python\Python312\python.exe manage.py runserver 127.0.0.1:8010
```

### Brak aktywnego `.venv`

Jesli `pip` albo `python` wskazuja zly interpreter, aktywuj srodowisko jeszcze raz:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Brak tabel w bazie

Jesli pojawia sie bledy typu `no such table`, wykonaj:

```powershell
python manage.py migrate
python manage.py seed_data
```

### Chcesz zaczac od czystej bazy

Usun plik `db.sqlite3`, a potem wykonaj:

```powershell
python manage.py migrate
python manage.py seed_data
```

## Status

Projekt zostal lokalnie sprawdzony:

- srodowisko `.venv` zostalo utworzone
- zaleznosci zainstalowane
- migracje wykonane
- dane startowe zaladowane
- strona glowna zwraca `HTTP 200`
