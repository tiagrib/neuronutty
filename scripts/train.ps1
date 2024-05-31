$currentDir = Split-Path -Leaf (Get-Location)
if ($currentDir -eq "scripts") {
    Set-Location ..
}

# Update this as required to poing to your python environment
$python = "$env:USERPROFILE\.pyenv-win-venv\envs\fairmotion\Scripts\python.exe"
Write-Host "Run test using the following python executable: '$python'"

$elements = Get-ChildItem -Path "Z:\preprocessed" -Directory | ForEach-Object { $_.Name }
$architectures = "seq2seq","transformer","transformer_encoder"
foreach ($elem in $elements) {
    Write-Host "Preprocessing dataset '$elem'..."
    foreach ($architecture in $architectures) {
        Write-Host "Preprocessing architecture '$architecture'..."
        $saveModelPath = "Z:\models\${elem}_${architecture}"
        $preprocessedPath = "Z:\preprocessed\$elem\aa"
        Write-Host "Save model path: $saveModelPath"
        Write-Host "Preprocessing Path: $preprocessedPath"
        if (-not (Test-Path $saveModelPath)) {
            & $python -m thirdparty.fairmotion.tasks.motion_prediction.training --save-model-path $saveModelPath --preprocessed-path $preprocessedPath --epochs 100 --device cuda --save-model-frequency 5 --architecture $architecture
        } else {
            Write-Host "Skipped existing model '$saveModelPath'."
        }
    }
}