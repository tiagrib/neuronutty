$currentDir = Split-Path -Leaf (Get-Location)
if ($currentDir -eq "scripts") {
    Set-Location ..
}

# Update this as required to poing to your python environment
$python = "$env:USERPROFILE\.pyenv-win-venv\envs\fairmotion\Scripts\python.exe"
Write-Host "Run test using the following python executable: '$python'"

$datasets = Get-ChildItem -Path "Z:\preprocessed" -Directory | ForEach-Object { $_.Name }
foreach ($dataset in $datasets) {
    $models = Get-ChildItem -Path "Z:\models\$elem*" -Directory | ForEach-Object { $_.Name }

    foreach ($model in $models) {
        $architecture = $model.Replace($dataset, "").Trim('_')
        $saveModelPath = "Z:\models\${model}"
        $saveOutputPath = "Z:\generated\${model}"
        $preprocessedPath = "Z:\preprocessed\$dataset\aa"
        if (-not (Test-Path $saveOutputPath)) {
            & $python -m thirdparty.fairmotion.tasks.motion_prediction.test --preprocessed-path $preprocessedPath --save-model-path $saveModelPath --save-output-path $saveOutputPath --architecture $architecture
        } else {
            Write-Host "Skipped existing model '$saveModelPath'."
        }
    }
}

