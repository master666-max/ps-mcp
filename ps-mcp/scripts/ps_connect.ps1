# ps_connect.ps1 - ps-mcp connection self-check (S mode main channel: COM)
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File ps_connect.ps1 [-JsPath <jsx>] [-QuitAfter] [-NoLaunch]
# Protocol: OK-PROCESS / MODAL lines / OK-CONNECT / OK-DOJS / RESULT-BEGIN..END
# exit: 0 ok | 2 connect failed | 3 dojs failed | 4 process not ready
param(
    [string]$JsPath = "",
    [switch]$QuitAfter,
    [switch]$NoLaunch
)
$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# ---- C# helpers: window enumeration / WM_CLOSE ----
Add-Type @"
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public class PscpWin {
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc cb, IntPtr lp);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder sb, int max);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint msg, IntPtr wp, IntPtr lp);
    public delegate bool EnumWindowsProc(IntPtr h, IntPtr lp);
    public const uint WM_CLOSE = 0x0010;
    public static List<IntPtr> VisibleToplevelsOfPid(uint target) {
        var list = new List<IntPtr>();
        EnumWindows((h, lp) => {
            uint pid; GetWindowThreadProcessId(h, out pid);
            if (pid == target && IsWindowVisible(h)) {
                var sb = new StringBuilder(256);
                GetWindowText(h, sb, 256);
                if (sb.Length > 0) list.Add(h);
            }
            return true;
        }, IntPtr.Zero);
        return list;
    }
    public static string TitleOf(IntPtr h) {
        var sb = new StringBuilder(256);
        GetWindowText(h, sb, 256);
        return sb.ToString();
    }
}
"@

# ---- 1. process ----
$p = Get-Process -Name Photoshop -ErrorAction SilentlyContinue
if (-not $p) {
    if ($NoLaunch) { Write-Output "FAIL-NOPROCESS (and -NoLaunch set)"; exit 4 }
    Write-Output "[1] Photoshop not running -> Start-Process, wait ready (<=150s)"
    Start-Process -FilePath 'C:\Program Files\Adobe\Adobe Photoshop 2026\Photoshop.exe'
    $deadline = (Get-Date).AddSeconds(150)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 3
        $p = Get-Process -Name Photoshop -ErrorAction SilentlyContinue
        if ($p -and $p.MainWindowHandle -ne 0) { break }
    }
    if (-not $p -or $p.MainWindowHandle -eq 0) { Write-Output "FAIL-NOTREADY"; exit 4 }
}
Write-Output ("OK-PROCESS pid={0}" -f $p.Id)

# ---- 2. startup modal scan (0x80080005 root cause, see references/01 section 2) ----
# Settle first: MainWindowHandle drifts during splash (observed: it pointed at the splash
# while the real main window looked like an "extra window"). Wait until handle stable.
$prevH = [IntPtr]::Zero
for ($i = 0; $i -lt 10; $i++) {
    Start-Sleep -Seconds 2
    $p.Refresh()
    if ($p.MainWindowHandle -eq $prevH -and $p.MainWindowHandle -ne 0) { break }
    $prevH = $p.MainWindowHandle
}
$mainH = $p.MainWindowHandle
$mainTitle = [PscpWin]::TitleOf($mainH)
$modals = @()
foreach ($h in [PscpWin]::VisibleToplevelsOfPid([uint32]$p.Id)) {
    $t = [PscpWin]::TitleOf($h)
    if ($h -ne $mainH -and $t -ne $mainTitle) { $modals += $h }   # same-title windows are NOT modals
}
if ($modals.Count -gt 0) {
    foreach ($h in $modals) { Write-Output ("MODAL-FOUND hwnd={0} title='{1}'" -f $h, [PscpWin]::TitleOf($h)) }
    foreach ($h in $modals) {
        [PscpWin]::PostMessage($h, [PscpWin]::WM_CLOSE, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null
        Write-Output ("MODAL-WMCLOSE-SENT hwnd={0}" -f $h)
    }
    Start-Sleep -Seconds 3
    $still = @()
    foreach ($h in [PscpWin]::VisibleToplevelsOfPid([uint32]$p.Id)) { if ($h -ne $mainH) { $still += $h } }
    if ($still.Count -gt 0) {
        Write-Output "MODAL-STILL-PRESENT: manual click needed (screenshot+coordinate click or user)"
        foreach ($h in $still) { Write-Output ("MODAL-REMAINS hwnd={0} title='{1}'" -f $h, [PscpWin]::TitleOf($h)) }
    } else {
        Write-Output "OK-MODAL-DISMISSED"
    }
} else {
    Write-Output "OK-NO-MODAL"
}

# ---- 3. COM connect ----
Write-Output "[2] connect Photoshop.Application"
try {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $app = New-Object -ComObject Photoshop.Application
    Write-Output ("OK-CONNECT elapsed={0:n1}s" -f $sw.Elapsed.TotalSeconds)
} catch {
    Write-Output ("FAIL-CONNECT: " + $_.Exception.Message.Split("`n")[0])
    Write-Output "HINT: 0x80080005 => startup modal still up (see MODAL lines) or app busy"
    exit 2
}

# ---- 4. DoJavaScript probe ----
if ($JsPath -ne "") {
    $js = Get-Content -LiteralPath $JsPath -Raw -Encoding UTF8
} else {
    $js = 'app.displayDialogs = DialogModes.NO; "v=" + app.version + " docs=" + app.documents.length;'
}
Write-Output ("[3] DoJavaScript length={0}" -f $js.Length)
$sw.Restart()
try {
    $result = $app.DoJavaScript($js)
} catch {
    Write-Output ("FAIL-DOJS: " + $_.Exception.Message.Split("`n")[0])
    if ($QuitAfter) { try { $app.Quit() } catch {} }
    exit 3
}
Write-Output ("OK-DOJS elapsed={0:n1}s" -f $sw.Elapsed.TotalSeconds)
Write-Output "RESULT-BEGIN"
Write-Output $result
Write-Output "RESULT-END"

if ($QuitAfter) {
    try { $app.Quit(); Write-Output "OK-QUIT" } catch { Write-Output "FAIL-QUIT" }
}
exit 0
