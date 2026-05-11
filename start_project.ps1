[CmdletBinding()]
param(
    [switch]$Foreground,
    [switch]$NoBrowser,
    [switch]$SetupOnly,
    [ValidateRange(1, 65535)]
    [int]$Port = 8010,
    [string]$BindAddress = "127.0.0.1"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$projectRoot = $PSScriptRoot
$venvDir = Join-Path $projectRoot ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"
$managePy = Join-Path $projectRoot "manage.py"
$requirementsFile = Join-Path $projectRoot "requirements.txt"
$serverAddress = "${BindAddress}:$Port"
$projectUrl = "http://${serverAddress}/"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Test-Command {
    param([string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Get-BasePython {
    $candidates = @(
        @{ Command = "py"; Arguments = @("-3.12") },
        @{ Command = "py"; Arguments = @("-3") },
        @{ Command = "py"; Arguments = @() },
        @{ Command = "python"; Arguments = @() }
    )

    foreach ($candidate in $candidates) {
        if (-not (Test-Command $candidate.Command)) {
            continue
        }

        try {
            & $candidate.Command @($candidate.Arguments + @("--version")) *> $null
            return $candidate
        }
        catch {
        }
    }

    throw "Nie znaleziono interpretera Python. Zainstaluj Python 3.12 albo uruchom projekt z istniejacego .venv."
}

function Ensure-Venv {
    if (Test-Path $venvPython) {
        return
    }

    Write-Step "Tworze srodowisko .venv"
    $basePython = Get-BasePython
    & $basePython.Command @($basePython.Arguments + @("-m", "venv", $venvDir))

    if (-not (Test-Path $venvPython)) {
        throw "Nie udalo sie utworzyc .venv."
    }
}

function Ensure-Requirements {
    try {
        & $venvPython -c "import django" *> $null
        Write-Step "Django jest juz zainstalowane"
        return
    }
    catch {
        Write-Step "Instaluje zaleznosci z requirements.txt"
        & $venvPython -m pip install -r $requirementsFile
    }
}

function Invoke-Manage {
    param([string[]]$Arguments)
    & $venvPython $managePy @Arguments
}

function Test-ServerAvailable {
    try {
        $response = Invoke-WebRequest -Uri $projectUrl -UseBasicParsing -TimeoutSec 2
        return $response.StatusCode -ge 200
    }
    catch {
        return $false
    }
}

function Wait-ForServer {
    param([int]$TimeoutSeconds = 15)

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-ServerAvailable) {
            return $true
        }

        Start-Sleep -Seconds 1
    }

    return $false
}

$freshDatabase = -not (Test-Path (Join-Path $projectRoot "db.sqlite3"))

Write-Step "Przygotowuje projekt"
Ensure-Venv
Ensure-Requirements

Write-Step "Uruchamiam migracje"
Invoke-Manage -Arguments @("migrate", "--noinput")

if ($freshDatabase) {
    Write-Step "Dodaje dane startowe"
    Invoke-Manage -Arguments @("seed_data")
}

if ($SetupOnly) {
    Write-Step "Srodowisko jest gotowe do uruchomienia"
    return
}

if (Test-ServerAvailable) {
    Write-Step "Serwer juz dziala pod $projectUrl"
    if (-not $NoBrowser) {
        Start-Process $projectUrl
    }

    return
}

if ($Foreground) {
    Write-Step "Startuje serwer w tym oknie pod $projectUrl"
    if (-not $NoBrowser) {
        Start-Process $projectUrl
    }

    Invoke-Manage -Arguments @("runserver", $serverAddress)
    return
}

Write-Step "Startuje serwer w osobnym oknie pod $projectUrl"
$serverCommand = "& '$venvPython' '$managePy' runserver '$serverAddress'"
Start-Process -FilePath "powershell.exe" -WorkingDirectory $projectRoot -ArgumentList @(
    "-NoExit",
    "-Command",
    $serverCommand
)

if (Wait-ForServer) {
    Write-Step "Aplikacja jest dostepna pod $projectUrl"
    if (-not $NoBrowser) {
        Start-Process $projectUrl
    }
}
else {
    Write-Warning "Serwer startuje dluzej niz zwykle. Sprawdz nowe okno PowerShell z logami Django."
}
