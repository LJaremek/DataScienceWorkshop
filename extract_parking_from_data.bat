@echo off
setlocal enabledelayedexpansion

echo Starting processing of cropped_gm.png files...

for /r "data" %%f in (cropped_osm.png) do (
    echo Processing: %%f
    python src/preprocessing/parking_extractor.py "%%f"
    if !errorlevel! neq 0 (
        echo Error processing file: %%f
    ) else (
        echo Successfully processed: %%f
    )
)

echo Processing complete.
pause