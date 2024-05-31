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
            python -m fairmotion.tasks.motion_prediction.training --save-model-path $saveModelPath --preprocessed-path $preprocessedPath --epochs 100 --device cuda --save-model-frequency 5 --architecture $architecture
        } else {
            Write-Host "Skipped existing model '$saveModelPath'."
        }
    }
}