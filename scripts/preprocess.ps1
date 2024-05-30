$sourceDir = "Z:\mocap\AMASS\Synthetic_60FPS"
$splitDir = "${sourceDir}_fnames"
$elements = Get-ChildItem -Path $sourceDir -Directory | ForEach-Object { $_.Name }
$elements += "."
foreach ($elem in $elements) {
    $inputDir = "${sourceDir}\${elem}"
    if ($elem -eq ".") {
        $elem = "full"
    }
    $outputDir = "Z:\preprocessed\${elem}"    
    if (-not (Test-Path $inputDir)) {
        python -m fairmotion.tasks.motion_prediction.preprocess --input-dir $inputDir --output-dir $outputDir --split-dir $splitDir --rep aa
    } else {
        Write-Host "Skipped existing preprocessed dataset '$inputDir'."
    }
}
