@echo off


python status\statuscalc.py example_data/status/input/ example_data/status/output/output_Python/ --startYear 1990 --endYear 2020



python status\status_to_json.py ./example_data/status/output/output_Python ./example_data/status/output/output_json

echo.
echo Successfully finished. Press any key to close...
pause >nul