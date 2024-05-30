$elements = Get-ChildItem -Path "Z:\preprocessed" -Directory | ForEach-Object { $_.Name }
$architectures = "seq2seq","transformer","transformer_encoder"
foreach ($elem in $elements) {
    $saveModelPath = "Z:\models\${elem}_${architecture}"
    $preprocessedPath = "Z:\preprocessed\$elem\aa"
    if (-not (Test-Path $saveModelPath)) {
        python -m fairmotion.tasks.motion_prediction.training --save-model-path $saveModelPath --preprocessed-path $preprocessedPath --epochs 100 --device cuda --save-model-frequency 5  --architecture $architecture
    } else {
        Write-Host "Skipped existing model '$saveModelPath'."
    }
}