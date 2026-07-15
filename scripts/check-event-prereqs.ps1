Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-CheckResult {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Detail
    )

    $status = if ($Passed) { "PASS" } else { "FAIL" }
    Write-Host ("[{0}] {1} - {2}" -f $status, $Name, $Detail)
}

function Test-CommandAvailable {
    param([string]$CommandName)
    return [bool](Get-Command $CommandName -ErrorAction SilentlyContinue)
}

$results = @()

# 1) Azure CLI
$azAvailable = Test-CommandAvailable -CommandName "az"
$azDetail = if ($azAvailable) {
    try {
        $azVersion = az version --query '"azure-cli"' -o tsv 2>$null
        if (-not $azVersion) { $azVersion = "installed" }
        "Azure CLI detected (version: $azVersion)"
    }
    catch {
        "Azure CLI detected"
    }
}
else {
    "Azure CLI not found on PATH"
}
$results += @{ Name = "Azure CLI installed"; Passed = $azAvailable; Detail = $azDetail }

# 2) Azure CLI sign-in
$azSignedIn = $false
$azAccountDetail = "Not checked (Azure CLI missing)"
if ($azAvailable) {
    try {
        $accountJson = az account show -o json 2>$null
        if ($LASTEXITCODE -eq 0 -and $accountJson) {
            $account = $accountJson | ConvertFrom-Json
            $azSignedIn = $true
            $azAccountDetail = "Signed in as $($account.user.name)"
        }
        else {
            $azAccountDetail = "Not signed in (run: az login)"
        }
    }
    catch {
        $azAccountDetail = "Not signed in (run: az login)"
    }
}
$results += @{ Name = "Azure CLI signed in"; Passed = $azSignedIn; Detail = $azAccountDetail }

# 3) Power BI Desktop
$pbiPaths = @(
    "$env:ProgramFiles\Microsoft Power BI Desktop\bin\PBIDesktop.exe",
    "$env:LOCALAPPDATA\Microsoft\Power BI Desktop\bin\PBIDesktop.exe",
    "$env:ProgramFiles\WindowsApps"
)

$pbiInstalled = Test-Path "$env:ProgramFiles\Microsoft Power BI Desktop\bin\PBIDesktop.exe" -PathType Leaf -ErrorAction SilentlyContinue
if (-not $pbiInstalled) {
    $pbiInstalled = Test-Path "$env:LOCALAPPDATA\Microsoft\Power BI Desktop\bin\PBIDesktop.exe" -PathType Leaf -ErrorAction SilentlyContinue
}

$pbiDetail = if ($pbiInstalled) {
    "Power BI Desktop executable found"
}
else {
    "Power BI Desktop executable not found in common install locations"
}
$results += @{ Name = "Power BI Desktop installed"; Passed = [bool]$pbiInstalled; Detail = $pbiDetail }

# 4) VS Code (optional but useful for this repo workflow)
$codeAvailable = Test-CommandAvailable -CommandName "code"
$codeDetail = if ($codeAvailable) { "VS Code CLI detected" } else { "VS Code CLI not found (optional)" }
$results += @{ Name = "VS Code CLI available (optional)"; Passed = $codeAvailable; Detail = $codeDetail }

# 5) Copilot extension(s) if VS Code CLI is available
$copilotInstalled = $false
$copilotChatInstalled = $false
$copilotDetail = "Not checked (VS Code CLI unavailable)"
if ($codeAvailable) {
    try {
        $exts = code --list-extensions 2>$null
        $copilotInstalled = $exts -contains "GitHub.copilot"
        $copilotChatInstalled = $exts -contains "GitHub.copilot-chat"

        if ($copilotInstalled -and $copilotChatInstalled) {
            $copilotDetail = "GitHub Copilot and Copilot Chat extensions found"
        }
        elseif ($copilotInstalled -or $copilotChatInstalled) {
            $copilotDetail = "Only one Copilot extension found; install both for best experience"
        }
        else {
            $copilotDetail = "Copilot extensions not found in VS Code"
        }
    }
    catch {
        $copilotDetail = "Could not query VS Code extensions"
    }
}
$results += @{ Name = "Copilot extensions installed"; Passed = ($copilotInstalled -and $copilotChatInstalled); Detail = $copilotDetail }

# 6) curl
$curlAvailable = Test-CommandAvailable -CommandName "curl"
$curlDetail = if ($curlAvailable) {
    try {
        $curlVersionLine = (curl --version 2>$null | Select-Object -First 1)
        if ($curlVersionLine) { $curlVersionLine } else { "curl detected" }
    }
    catch {
        "curl detected"
    }
}
else {
    "curl not found on PATH"
}
$results += @{ Name = "curl available"; Passed = $curlAvailable; Detail = $curlDetail }

# 7) jq
$jqAvailable = Test-CommandAvailable -CommandName "jq"
$jqDetail = if ($jqAvailable) {
    try {
        $jqVersion = jq --version 2>$null
        if ($jqVersion) { "jq detected ($jqVersion)" } else { "jq detected" }
    }
    catch {
        "jq detected"
    }
}
else {
    "jq not found on PATH"
}
$results += @{ Name = "jq available"; Passed = $jqAvailable; Detail = $jqDetail }

# 8) sqlcmd (Go version)
$sqlcmdAvailable = Test-CommandAvailable -CommandName "sqlcmd"
$sqlcmdDetail = if ($sqlcmdAvailable) {
    try {
        $sqlcmdVersion = sqlcmd --version 2>$null
        if ($sqlcmdVersion) { "sqlcmd detected ($sqlcmdVersion)" } else { "sqlcmd detected" }
    }
    catch {
        "sqlcmd detected"
    }
}
else {
    "sqlcmd not found on PATH (install Go sqlcmd: winget install sqlcmd)"
}
$results += @{ Name = "sqlcmd available"; Passed = $sqlcmdAvailable; Detail = $sqlcmdDetail }

Write-Host ""
Write-Host "=== Local Preflight Results ==="
foreach ($r in $results) {
    Write-CheckResult -Name $r.Name -Passed ([bool]$r.Passed) -Detail $r.Detail
}

$failed = @($results | Where-Object { -not $_.Passed })
Write-Host ""
if ($failed.Count -eq 0) {
    Write-Host "Local prerequisite checks passed."
}
else {
    Write-Host ("Local prerequisite checks completed with {0} failure(s)." -f $failed.Count)
}

Write-Host ""
Write-Host "=== Manual Checks Required (Not Fully Automatable Locally) ==="
Write-Host "- Fabric workspace exists and is on active capacity (F64+ recommended)."
Write-Host "- Your account has Contributor or Member role on the workspace."
Write-Host "- You have a Power BI Pro license."
Write-Host "- Tenant settings allow Lakehouse, Notebook/Spark, Eventhouse/KQL, semantic model authoring, Data Agent, OrgApp, and sharing/publishing."

if ($failed.Count -gt 0) {
    exit 1
}
exit 0
