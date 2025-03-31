#Define na lista de hosts do PC o gateway.localhost

if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    $arguments = "& '" + $myinvocation.mycommand.definition + "'"
    Start-Process powershell -Verb runAs -ArgumentList $arguments
    exit
}

# Define a linha que deve ser adicionada
$line = "127.0.0.1    gateway.localhost"
$hostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"

# Lê o conteúdo do arquivo hosts
$content = Get-Content $hostsPath -ErrorAction SilentlyContinue

# Se a linha ainda não estiver presente, adiciona-a
if ($content -notcontains $line) {
    Add-Content -Path $hostsPath -Value $line
    Write-Output "Linha adicionada ao arquivo hosts."
} else {
    Write-Output "Linha já existe no arquivo hosts."
}
