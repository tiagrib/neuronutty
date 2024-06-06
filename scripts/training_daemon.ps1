while ($true) {
    python . train_daemon --watch-path z:\jobs
    if ($LASTEXITCODE -ne 0) {
        Start-Sleep -Seconds 3
    } else {
        break
    }
}