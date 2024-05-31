$currentDir = Split-Path -Leaf (Get-Location)
if ($currentDir -eq "scripts") {
    Set-Location ..
}

# Update this as required to poing to your python environment
$python = "$env:USERPROFILE\.pyenv-win-venv\envs\fairmotion\Scripts\python.exe"
Write-Host "Run test using the following python executable: '$python'"

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
        & $python -m thirdparty.fairmotion.tasks.motion_prediction.preprocess --input-dir $inputDir --output-dir $outputDir --split-dir $splitDir --rep aa
    } else {
        Write-Host "Skipped existing preprocessed dataset '$inputDir'."
    }
}
