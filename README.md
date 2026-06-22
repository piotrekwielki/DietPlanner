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
- terminal, np. PowerShell, Bash albo Zsh

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

## Najlatwiejszy start na Linux/macOS

Z katalogu projektu uruchom:

```bash
chmod +x ./start_project.sh
./start_project.sh
```

Mozesz tez uruchomic skrypt bez nadawania uprawnien wykonywania:

```bash
bash ./start_project.sh
```

Skrypt:

- utworzy `.venv`, jesli go nie ma
- zainstaluje zaleznosci, jesli brakuje Django
- wykona `migrate`
- zaladuje `seed_data` przy pierwszym starcie
- uruchomi serwer Django pod `http://127.0.0.1:8010/`
- sprobuje otworzyc aplikacje w przegladarce przez `xdg-open` albo `open`

Jesli chcesz tylko przygotowac srodowisko bez startu serwera:

```bash
./start_project.sh --setup-only
```

Jesli port `8010` jest zajety, wybierz inny:

```bash
./start_project.sh --port 8020
```

Jesli nie chcesz automatycznego otwierania przegladarki:

```bash
./start_project.sh --no-browser
```

## Uruchomienie reczne w czystym srodowisku

Wszystkie polecenia ponizej wykonuj z katalogu projektu:

```bash
cd /sciezka/do/DietPlanner
```

### 1. Sprawdz, czy Python dziala

```bash
python --version
```

Na Linux/macOS komenda moze nazywac sie `python3`:

```bash
python3 --version
```

Na Windows mozesz tez uzyc launchera `py`:

```bash
py --version
```

albo podaj pelna sciezke do interpretera, np.:

```powershell
C:\Users\piotr\AppData\Local\Programs\Python\Python312\python.exe --version
```

### 2. Utworz srodowisko wirtualne

Jesli `python` dziala:

```bash
python -m venv .venv
```

Na Linux/macOS czesto bedzie to:

```bash
python3 -m venv .venv
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

Linux/macOS:

```bash
source .venv/bin/activate
```

### 4. Zainstaluj zaleznosci

```bash
pip install -r requirements.txt
```

### 5. Wygeneruj migracje

```bash
python manage.py makemigrations
```

### 6. Zastosuj migracje do bazy

```bash
python manage.py migrate
```

### 7. Zaladuj dane startowe

Ta komenda doda:

- konto administratora
- konto demo
- przykladowe dania
- przykladowy szablon jadlospisu

```bash
python manage.py seed_data
```

### 8. Uruchom serwer developerski

```bash
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

Windows:

```powershell
cd C:\sciezka\do\DietPlanner
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
python manage.py runserver 127.0.0.1:8010
```

Linux/macOS:

```bash
cd /sciezka/do/DietPlanner
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
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
|-- start_project.bat
|-- start_project.ps1
|-- start_project.sh
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

Pliki takie jak `.venv/`, `db.sqlite3`, `staticfiles/`, `media/`, logi i cache Pythona sa lokalne i nie powinny trafic do repozytorium.

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
