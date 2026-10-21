$ErrorActionPreference = "Stop"

$distro = "Ubuntu-24.04"
$windowsScript = (Join-Path $PSScriptRoot "check-toolchain.sh").Replace("\", "/")
$translatedPath = & wsl.exe -d $distro -- wslpath -a -u $windowsScript
if ($LASTEXITCODE -ne 0 -or -not $translatedPath) {
    throw "Could not translate the toolchain check path for WSL."
}
$linuxScript = $translatedPath.Trim()

& wsl.exe -d $distro -- bash $linuxScript
exit $LASTEXITCODE
