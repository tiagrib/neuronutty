$sourceDir = "Z:\mocap\AMASS\Synthetic_60FPS"
$splitDir = "${sourceDir}_fnames"
$elements = Get-ChildItem -Path $sourceDir -Directory | ForEach-Object { $_.Name }
$elements += ""
foreach ($elem in $elements) {
    Write-Host "Preprocessing dataset '$elem'..."
    $inputDir = "${sourceDir}\${elem}"
    Write-Host "Input directory: $inputDir"
    if ($elem -eq "") {
        $elem = "AMASS_full"
        $inputDir = $sourceDir
    }
    $outputDir = "Z:\preprocessed\${elem}"    
    Write-Host "Output directory: $outputDir"
    if (-not (Test-Path $outputDir)) {
        python -m fairmotion.tasks.motion_prediction.preprocess --input-dir $inputDir --output-dir $outputDir --split-dir $splitDir --rep aa
    } else {
        Write-Host "Skipped existing preprocessed dataset '$inputDir'."
    }
}
