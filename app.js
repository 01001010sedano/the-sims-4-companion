const pages = document.querySelectorAll('.page');
const crumb = document.querySelector('#crumb');
const toast = document.querySelector('#toast');
function showToast(message){toast.textContent=message;toast.classList.add('show');setTimeout(()=>toast.classList.remove('show'),3000)}
function openPage(id){pages.forEach(p=>p.classList.toggle('active-page',p.id===id));document.querySelectorAll('.nav-item').forEach(n=>n.classList.toggle('active',n.dataset.page===id));crumb.textContent=id==='mods'?'Scan Mods':id==='updates'?'Sims 4 Updates':id[0].toUpperCase()+id.slice(1);window.scrollTo({top:0,behavior:'smooth'})}
document.querySelectorAll('[data-page]').forEach(el=>el.addEventListener('click',()=>openPage(el.dataset.page)));
document.querySelector('#scanHero').addEventListener('click',()=>openPage('mods'));
document.querySelector('#connectTip').addEventListener('click',()=>openPage('mods'));
const folderInput=document.querySelector('#folderInput');
function chooseFolder(){folderInput.click()}
document.querySelector('#folderButton').addEventListener('click',chooseFolder);document.querySelector('#folderButton2').addEventListener('click',chooseFolder);
folderInput.addEventListener('change',()=>{if(folderInput.files.length){const scripts=[...folderInput.files].filter(f=>f.name.endsWith('.ts4script')).length;showToast(`Found ${folderInput.files.length} mod files${scripts?` · ${scripts} script mods`:''}.`);document.querySelector('.scan-empty h2').textContent='Scan complete';document.querySelector('.scan-empty p').textContent=`Found ${folderInput.files.length} files. Choose AI Search to find creator updates.`}});
document.querySelectorAll('.mode').forEach(btn=>btn.addEventListener('click',()=>{document.querySelectorAll('.mode').forEach(b=>b.classList.remove('active'));btn.classList.add('active');const guide=document.querySelector('#apiGuide');guide.classList.toggle('hidden',btn.dataset.mode!=='ai');if(btn.dataset.mode==='offline')showToast('Offline scan selected — no AI or web search.')}));
document.querySelector('#showKey').addEventListener('click',()=>document.querySelector('#keyForm').classList.toggle('hidden'));
document.querySelector('#saveKey').addEventListener('click',()=>{const key=document.querySelector('#geminiKey').value.trim();if(!key)return showToast('Please paste your Gemini API key first.');localStorage.setItem('geminiKey',key);document.querySelector('#keyForm').classList.add('hidden');showToast('Gemini API key saved in this browser.');});
document.querySelector('#checkUpdates')?.addEventListener('click',()=>showToast('Manual update check selected. Official source connection will run here.'));
// Factual update rows can be rendered by the future official-source adapter.
// Clicking a row/arrow opens its complete, source-backed detail list.
document.addEventListener('click',event=>{const row=event.target.closest('.news-item');if(!row)return;const detail=document.querySelector('#updateDetails');if(!detail)return;const title=row.dataset.title||row.querySelector('strong')?.textContent||'Update details';const items=(row.dataset.items||'').split('|').filter(Boolean);detail.innerHTML=`<div class="detail-heading"><strong>${title}</strong><button class="close-detail" aria-label="Close details">×</button></div>${items.length?`<ul>${items.map(item=>`<li>${item}</li>`).join('')}</ul>`:'<p>Details will appear here after the official update source is loaded.</p>'}`;detail.classList.remove('hidden');detail.querySelector('.close-detail').addEventListener('click',()=>detail.classList.add('hidden'));});
