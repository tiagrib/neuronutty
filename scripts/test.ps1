$datasets = Get-ChildItem -Path "Z:\preprocessed" -Directory | ForEach-Object { $_.Name }
foreach ($dataset in $datasets) {
    $models = Get-ChildItem -Path "Z:\models\$elem*" -Directory | ForEach-Object { $_.Name }

    foreach ($model in $models) {
        $architecture = $model.Replace($dataset, "").Trim('_')
        $saveModelPath = "Z:\models\${model}"
        $saveOutputPath = "Z:\generated\${model}"
        $preprocessedPath = "Z:\preprocessed\$dataset\aa"
        if (-not (Test-Path $saveOutputPath)) {
            python -m fairmotion.tasks.motion_prediction.test --preprocessed-path $preprocessedPath --save-model-path $saveModelPath --save-output-path $saveOutputPath --architecture $architecture
        } else {
            Write-Host "Skipped existing model '$saveModelPath'."
        }
    }
}

