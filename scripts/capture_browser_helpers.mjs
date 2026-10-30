// Import in the existing authenticated node_repl. Never persist auth state.
export function installCaptureHelpers({fs,root,page}) {
var captureManifests = [];
var captureRows = [];
var loaded = false;
var saveCapture = async function (algorithm, similarity, response, payload) {
  if (!loaded) {
    const dir=root+'/data/website/verified_baseline';
    try {
      captureManifests=JSON.parse(await fs.readFile(dir+'/capture_manifest.json','utf8'));
      for(const c of captureManifests) {
        const saved=JSON.parse(await fs.readFile(dir+'/'+c.capture_id+'.json','utf8'));
        for(const x of saved.items) captureRows.push({capture_id:c.capture_id,captured_at:c.captured_at,algorithm:c.algorithm,user_id:c.user_id,similarity:c.similarity,...x,source_screenshot:c.screenshot});
      }
    } catch(e) { if(e.code!=='ENOENT') throw e; }
    loaded=true;
  }
  const captureId = algorithm + '_' + similarity;
  const capturedAt = new Date().toISOString();
  if (response.status() !== 200) throw new Error('HTTP ' + response.status() + '; capture rejected');
  if (payload.algorithm !== algorithm) throw new Error('Backend algorithm mismatch');
  await page.waitForFunction(a => document.querySelector('#algo-label')?.textContent.trim().endsWith(a.toUpperCase()), algorithm);
  await page.waitForLoadState('networkidle');
  const cards = await page.locator('#recommendation-list > *').count();
  const label = await page.locator('#algo-label').innerText();
  if (await page.locator('#algorithm').inputValue() !== algorithm || await page.locator('#similarity-method').inputValue() !== similarity) throw new Error('Selected configuration mismatch');
  const ids = payload.items.map(x=>String(x.job.id));
  const selectedIds = (payload.diagnostics?.selected_result?.job_ids || []).map(String);
  if (JSON.stringify(ids) !== JSON.stringify(selectedIds)) throw new Error('Result IDs mismatch');
  if (ids.length && cards !== ids.length) throw new Error('Rendered card count mismatch');
  const screenshot = 'evidence/website/verified_baseline/' + captureId + '.png';
  await fs.mkdir(root + '/evidence/website/verified_baseline', {recursive:true});
  await fs.mkdir(root + '/data/website/verified_baseline', {recursive:true});
  await page.locator('#recommendations').screenshot({path:root+'/'+screenshot});
  const safe = {
    capture_id:captureId, captured_at:capturedAt, user_id:'458', requested_algorithm:algorithm,
    returned_algorithm:payload.algorithm, similarity, http_status:200, capture_status:'success',
    rendered_label:label, profile_state:'missing', rating_count:0,
    filters:{query:'',location:await page.locator('#context-location').inputValue(),job_type:''},
    candidate_count:payload.diagnostics?.candidate_count, candidate_limit:payload.diagnostics?.candidate_limit,
    // The diagnostics return only 50 feature rows: this is NOT the full candidate set.
    diagnostic_sample_job_ids:payload.diagnostics?.feature_matrix?.map(x=>String(x.job_id)),
    selected_result:payload.diagnostics?.selected_result, website_metrics:payload.diagnostics?.metrics,
    screenshot, items:payload.items.map((x,i)=>({rank:i+1,job_id:String(x.job.id),title:x.job.job_title||x.job.title,company_name:x.job.company_name,location:x.job.job_location||x.job.location,score:x.score,reason:x.reason}))
  };
  await fs.writeFile(root+'/data/website/verified_baseline/'+captureId+'.json',JSON.stringify(safe,null,2),'utf8');
  captureManifests = captureManifests.filter(x=>x.capture_id!==captureId);
  captureRows = captureRows.filter(x=>x.capture_id!==captureId);
  captureManifests.push({capture_id:captureId,captured_at:capturedAt,screenshot,algorithm,user_id:'458',returned_algorithm:payload.algorithm,similarity,http_status:200,capture_status:'success',n_items:safe.items.length,candidate_count:safe.candidate_count,profile_state:'missing'});
  for (const x of safe.items) captureRows.push({capture_id:captureId,captured_at:capturedAt,algorithm,user_id:'458',similarity,...x,source_screenshot:screenshot});
  await fs.writeFile(root+'/data/website/verified_baseline/capture_manifest.json',JSON.stringify(captureManifests,null,2),'utf8');
  const columns=['capture_id','captured_at','algorithm','user_id','similarity','rank','job_id','title','company_name','location','score','reason','source_screenshot'];
  const csv = [columns,...captureRows.map(r=>columns.map(k=>r[k]??''))].map(row=>row.map(x=>'"'+String(x).replaceAll('"','""')+'"').join(',')).join('\r\n');
  await fs.writeFile(root+'/data/website/verified_baseline/recommendations.csv','\uFEFF'+csv,'utf8');
  console.log({captureId,status:'success',n_items:safe.items.length,label});
};
var captureOne = async function (algorithm,similarity='cosine') {
  const oldAlgo=await page.locator('#algorithm').inputValue();
  const oldSim=await page.locator('#similarity-method').inputValue();
  if (oldAlgo!==algorithm && oldSim!==similarity) throw new Error('Change one selector at a time to avoid redundant calls');
  const responsePromise=page.waitForResponse(r=>{const u=new URL(r.url());return u.pathname==='/api/recommend/458'&&u.searchParams.get('algo')===algorithm&&u.searchParams.get('similarity')===similarity});
  if(oldAlgo!==algorithm) await page.locator('#algorithm').selectOption(algorithm);
  else if(oldSim!==similarity) await page.locator('#similarity-method').selectOption(similarity);
  else await page.locator('#recommend-button').click();
  const response=await responsePromise;
  if(response.status()!==200) throw new Error('HTTP '+response.status()+'; stop and respect rate limit');
  await saveCapture(algorithm,similarity,response,await response.json());
};
return {saveCapture,captureOne};
}
