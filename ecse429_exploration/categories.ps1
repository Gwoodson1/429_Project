$Area='categories'
. "$PSScriptRoot/common.ps1"
$categoryId=$null;$todoId=$null;$projectId=$null
try {
 Check-Service
 Invoke-Probe 'list-json' GET '/categories' -Expected '200' | Out-Null
 Invoke-Probe 'list-xml' GET '/categories' -Accept 'application/xml' -Expected '200' | Out-Null
 Invoke-Probe 'collection-head' HEAD '/categories' -Expected '200' | Out-Null
 Invoke-Probe 'collection-options' OPTIONS '/categories' -Expected '200' | Out-Null
 foreach($m in @('PUT','DELETE','PATCH')){Invoke-Probe "collection-disallowed-$m" $m '/categories' -Expected '405' | Out-Null}
 $c=Invoke-Probe 'create-category' POST '/categories' -Body ('{"title":"ECSE429 Category '+$RunId+'","description":"Exploratory test"}') -Expected '201'
 $categoryId=Get-Id $c
 if(!$categoryId){Write-Warning 'Creation did not return an ID; skipping ID-dependent probes.'}
 else {
  $p="/categories/$categoryId"
  Invoke-Probe 'get-created' GET $p -Expected '200' | Out-Null
  Invoke-Probe 'get-created-xml' GET $p -Accept 'application/xml' -Expected '200' | Out-Null
  Invoke-Probe 'update-post' POST $p -Body '{"description":"Updated via POST"}' -Expected '200' | Out-Null
  Invoke-Probe 'verify-post' GET $p -Expected '200' | Out-Null
  Invoke-Probe 'update-put' PUT $p -Body '{"description":"Updated via PUT"}' -Expected '200' | Out-Null
  Invoke-Probe 'verify-put' GET $p -Expected '200' | Out-Null
  Invoke-Probe 'item-head' HEAD $p -Expected '200' | Out-Null
  Invoke-Probe 'item-options' OPTIONS $p -Expected '200' | Out-Null
  Invoke-Probe 'item-disallowed-patch' PATCH $p -Expected '405' | Out-Null
  foreach($rel in @('todos','projects')) {
   Invoke-Probe "list-$rel" GET "$p/$rel" -Expected '200' | Out-Null
   Invoke-Probe "head-$rel" HEAD "$p/$rel" -Expected '200' | Out-Null
   Invoke-Probe "options-$rel" OPTIONS "$p/$rel" -Expected '200' | Out-Null
   foreach($m in @('PUT','DELETE','PATCH')){Invoke-Probe "disallowed-$rel-$m" $m "$p/$rel" -Expected '405' | Out-Null}
  }
  $t=Invoke-Probe 'create-related-todo' POST '/todos' -Body ('{"title":"ECSE429 Category Todo '+$RunId+'","doneStatus":false}') -Expected '201'
  $todoId=Get-Id $t
  $pr=Invoke-Probe 'create-related-project' POST '/projects' -Body ('{"title":"ECSE429 Category Project '+$RunId+'","description":"Temporary"}') -Expected '201'
  $projectId=Get-Id $pr
  foreach($relation in @(@('todos',$todoId),@('projects',$projectId))) {
   $rel=$relation[0];$target=$relation[1]
   if(!$target){continue}
   $rp="$p/$rel";$rid="$rp/$target"
   Invoke-Probe "create-$rel-link" POST $rp -Body ('{"id":"'+$target+'"}') -Expected '201' | Out-Null
   Invoke-Probe "verify-$rel-link" GET $rp -Expected '200' | Out-Null
   Invoke-Probe "link-options-$rel" OPTIONS $rid -Expected '200' | Out-Null
   foreach($m in @('GET','PUT','POST','HEAD','PATCH')){Invoke-Probe "link-disallowed-$rel-$m" $m $rid -Expected '405' | Out-Null}
   Invoke-Probe "delete-$rel-link" DELETE $rid -Expected '200' | Out-Null
   Invoke-Probe "delete-$rel-link-again" DELETE $rid -Expected '404 or 400' | Out-Null
  }
  Invoke-Probe 'delete-category' DELETE $p -Expected '200' | Out-Null
  $categoryId=$null
  Invoke-Probe 'get-deleted' GET $p -Expected '404' | Out-Null
  Invoke-Probe 'delete-again' DELETE $p -Expected '404' | Out-Null
 }
 Invoke-Probe 'get-missing' GET '/categories/999999999' -Expected '404' | Out-Null
 Invoke-Probe 'malformed-json' POST '/categories' -Body '{"title":' -Expected '400' | Out-Null
 Invoke-Probe 'malformed-xml' POST '/categories' -ContentType 'application/xml' -Body '<category><title>broken' -Expected 'error response' | Out-Null
} finally {
 if($categoryId){Invoke-Probe 'cleanup-category' DELETE "/categories/$categoryId" | Out-Null}
 if($todoId){Invoke-Probe 'cleanup-todo' DELETE "/todos/$todoId" | Out-Null}
 if($projectId){Invoke-Probe 'cleanup-project' DELETE "/projects/$projectId" | Out-Null}
 Save-Manifest
}
