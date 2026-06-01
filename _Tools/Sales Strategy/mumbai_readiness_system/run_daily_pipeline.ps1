param(
  [string]$PythonPath = 'python'
)

$script = Join-Path $PSScriptRoot 'run_pipeline.py'
& $PythonPath $script
