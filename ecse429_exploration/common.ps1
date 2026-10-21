$BaseUrl = 'http://localhost:4567'
$RunId = [guid]::NewGuid().ToString('N').Substring(0,10)
$OutputDir = Join-Path $PSScriptRoot ("logs/{0}-{1}" -f $Area,$RunId)
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
$script:Counter=0
$script:Manifest=@()
function Invoke-Probe {
 param([string]$Name,[string]$Method,[string]$Path,[string]$Body='', [string]$ContentType='application/json',[string]$Accept='application/json',[string]$Expected='')
 $script:Counter++
 $stem=('{0:D3}-{1}' -f $script:Counter,($Name -replace '[^a-zA-Z0-9_-]','_'))
 $headers=Join-Path $OutputDir "$stem.headers.txt"; $response=Join-Path $OutputDir "$stem.body.txt"
 $argsList=@('-sS','--max-time','12','-X',$Method,'-D',$headers,'-o',$response,'-w','%{http_code}','-H',"Accept: $Accept")
 if ($Body -ne '') {
  $requestFile=Join-Path $OutputDir "$stem.request.txt"
  [System.IO.File]::WriteAllText($requestFile,$Body,[System.Text.UTF8Encoding]::new($false))
  $argsList+=@('-H',"Content-Type: $ContentType",'--data-binary',"@$requestFile")
 }
 $argsList+= "$BaseUrl$Path"
 $status= & curl.exe @argsList 2> (Join-Path $OutputDir "$stem.stderr.txt")
 $exit=$LASTEXITCODE
 $raw=if(Test-Path $response){[System.IO.File]::ReadAllText($response)}else{''}
 $entry=[pscustomobject]@{name=$Name;method=$Method;path=$Path;expected=$Expected;status=($status -join '').Trim();curlExit=$exit;body=$raw;headersFile="$stem.headers.txt";bodyFile="$stem.body.txt"}
 $script:Manifest+= $entry
 Write-Host ("{0,-34} {1,-7} {2,-45} HTTP {3} (curl {4})" -f $Name,$Method,$Path,$entry.status,$exit)
 return $entry
}
function Get-Id($Result) {
 try {
  $data=$Result.body | ConvertFrom-Json
  if($data -is [array]) {$data=$data[0]}
  if($null -ne $data.id){return [string]$data.id}
 } catch {}
 return $null
}
function Save-Manifest {
 $script:Manifest | ConvertTo-Json -Depth 12 | Set-Content -Encoding UTF8 (Join-Path $OutputDir 'results.json')
 $script:Manifest | Select-Object name,method,path,expected,status,curlExit,headersFile,bodyFile | Export-Csv -NoTypeInformation (Join-Path $OutputDir 'summary.csv')
 Write-Host "`nSaved results to: $OutputDir"
}
function Check-Service {
 $r=Invoke-Probe 'service-check' 'GET' '/todos' -Expected '200'
 if($r.curlExit -ne 0 -or $r.status -ne '200') {Save-Manifest;throw 'API is unavailable. Start the JAR first.'}
}
