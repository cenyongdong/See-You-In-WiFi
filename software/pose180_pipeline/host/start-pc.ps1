param(
	[string]$Board = "192.168.50.49",
	[string]$NodePath = "",
	[string]$LocalAddress = "",
	[switch]$Check,
	[ValidateRange(0, 86400)][int]$Seconds = 0
)

$ErrorActionPreference = "Stop"

# Deployment-root launcher. An explicit runtime path takes precedence.
$candidates = @()
if ($NodePath) {
	$candidates += $NodePath
} else {
	$candidates += Join-Path $PSScriptRoot "pc/runtime/node.exe"
	$command = Get-Command node.exe -CommandType Application -ErrorAction SilentlyContinue
	if ($command) {
		$candidates += $command.Source
	}
	if ($env:ProgramFiles) {
		$candidates += Join-Path $env:ProgramFiles "nodejs/node.exe"
	}
	if ($env:LOCALAPPDATA) {
		$candidates += Join-Path $env:LOCALAPPDATA "Programs/nodejs/node.exe"
	}
	if ($env:USERPROFILE) {
		$candidates += Join-Path $env:USERPROFILE ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe"
	}
}

# Validate the executable itself; the caller's PATH may differ from Codex's.
$nodeExecutable = $null
$nodeVersion = $null
foreach ($candidate in ($candidates | Select-Object -Unique)) {
	if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
		continue
	}
	try {
		$version = (& $candidate --version 2>&1 | Out-String).Trim()
		if ($LASTEXITCODE -eq 0 -and $version -match '^v(\d+)\.' -and [int]$Matches[1] -ge 20) {
			$nodeExecutable = (Resolve-Path -LiteralPath $candidate).Path
			$nodeVersion = $version
			break
		}
	} catch {
		# A stale runtime location must not hide another usable installation.
	}
}

if (-not $nodeExecutable) {
	throw "Node.js 20 or newer was not found. Supply its executable with -NodePath 'C:\path\to\node.exe'."
}
if ($Check) {
	[pscustomobject]@{ ready = $true; node = $nodeExecutable; version = $nodeVersion } | ConvertTo-Json -Compress
	exit 0
}

$entry = Join-Path $PSScriptRoot "pc/software/pose180_pipeline/host/resident.mjs"
if (-not (Test-Path -LiteralPath $entry -PathType Leaf)) {
	throw "PC entry point is missing. Run this launcher from the extracted deployment package."
}
$assets = @(
	"pc/software/pose180_pipeline/host/web/scene.js",
	"pc/software/pc_viewer/node_modules/three/build/three.module.js",
	"pc/software/pc_viewer/node_modules/three/build/three.core.js",
	"pc/software/pc_viewer/node_modules/three/examples/jsm/controls/OrbitControls.js"
)
foreach ($asset in $assets) {
	if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot $asset) -PathType Leaf)) {
		throw "PC viewer asset is missing: $asset. Extract the complete deployment package or the PC asset repair patch into this folder."
	}
}
Write-Host "Using Node.js $nodeVersion ($nodeExecutable)"
Write-Host "Before filtering: http://127.0.0.1:39381/"
Write-Host "After filtering:  http://127.0.0.1:39380/"
Write-Host "Press Ctrl+C to close both PC observers. Board inference and HDMI continue independently."
$logDirectory = Join-Path $PSScriptRoot "pc-logs"
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
$runStamp = Get-Date -Format "yyyyMMdd-HHmmss-fff"
$children = @()
$exitCode = 0
try {
	foreach ($mode in @("raw", "view")) {
		$httpPort = if ($mode -eq "raw") { "39381" } else { "39380" }
		$arguments = @($entry, "--board", $Board, "--mode", $mode, "--http-port", $httpPort, "--metrics-port", "0", "--seconds", "$Seconds")
		if ($LocalAddress) { $arguments += @("--local-address", $LocalAddress) }
		if ($mode -eq "view") { $arguments += @("--metrics-state-url", "http://127.0.0.1:39381/api/state") }
		# Start-Process joins arguments on Windows: quote each complete argument.
		$quoted = ($arguments | ForEach-Object { '"' + $_.Replace('"', '\"') + '"' }) -join ' '
		$stdout = Join-Path $logDirectory "$runStamp-$mode.stdout.log"
		$stderr = Join-Path $logDirectory "$runStamp-$mode.stderr.log"
		$child = Start-Process -FilePath $nodeExecutable -ArgumentList $quoted -WindowStyle Hidden -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
		$children += $child
	}
	while ($true) {
		$alive = 0
		foreach ($child in $children) {
			$child.Refresh()
			if ($child.HasExited) {
				if ($child.ExitCode -ne 0) { throw "PC observer exited ($($child.ExitCode)); inspect $logDirectory" }
			} else { $alive += 1 }
		}
		if ($alive -eq 0) { break }
		Start-Sleep -Milliseconds 200
	}
} finally {
	foreach ($child in $children) {
		$child.Refresh()
		if (-not $child.HasExited) {
			# Only this launcher's readonly Node children; never board processes.
			$child.Kill()
			$child.WaitForExit()
		}
		$child.Dispose()
	}
}
exit $exitCode
