BRAND_STYLES = """
.dhanraj-wordmark{display:inline-flex;align-items:center;gap:0;color:#1f2937;font-family:Inter,"Segoe UI",Arial,sans-serif;font-size:clamp(23px,3vw,34px);font-weight:750;line-height:1;letter-spacing:-.055em;white-space:nowrap;text-decoration:none}
.dhanraj-wordmark:hover{text-decoration:none}.dhanraj-wordmark .dhanraj-mark-d{display:inline-grid;width:1.04em;height:1.04em;margin-right:.08em;place-items:center;border-radius:50%;background:#DC2626;color:#111827;font-size:.88em;font-weight:900;letter-spacing:-.04em}
.dhanraj-wordmark .dhanraj-mark-raj{margin-left:.12em;color:#DC2626;font-weight:850;letter-spacing:-.045em}
"""

AUTH_STYLES = """
:root{color-scheme:light;--ink:#351538;--wine:#60132f;--wine-deep:#350d26;--red:#e73550;--red-deep:#bd203f;--lavender:#e8c9ff;--lavender-light:#f3e5ff;--panel:#f8f2ff;--muted:#806b8e;--line:#d3b3e8}
*{box-sizing:border-box}body{margin:0;background:#d8b3f1;color:var(--ink);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:var(--wine);text-decoration:none}a:hover{text-decoration:underline}
.site-header{background:#f3e5ff;box-shadow:0 3px 12px #37102140}
.topbar{height:64px;display:grid;grid-template-columns:1fr auto 1fr;align-items:center;padding:0 18px;background:#f3e5ff;border-bottom:1px solid #d3b3e8}
.brand{display:flex;align-items:center}
.top-link{justify-self:end;padding:6px 12px;border:1px solid #ff8ca3;border-radius:8px;background:var(--red);color:#fff;font-size:14px;font-weight:700;box-shadow:0 3px 8px #17051130}
.top-link:first-child{justify-self:start}
.site-nav{min-height:54px;background:var(--wine);display:flex;align-items:center;justify-content:center;gap:clamp(12px,3vw,34px);padding:10px 16px;flex-wrap:wrap}
.site-nav a{color:#fff;font-size:14px;font-weight:650}
.auth-area{padding:16px 12px 0;background:#d8b3f1;min-height:calc(100vh - 230px)}
.auth-card{max-width:1200px;min-height:405px;margin:0 auto;padding:26px 18px 30px;background:var(--lavender);border:1px solid #d5b0ee;border-radius:18px;box-shadow:0 8px 24px #4d1b5824;text-align:center;display:flex;flex-direction:column;align-items:center;justify-content:center}
.auth-card h1{font-size:18px;font-weight:650;margin:0 0 25px}
.auth-form{width:min(100%,360px);display:flex;flex-direction:column;align-items:stretch;gap:16px}
.field{height:56px;display:flex;padding:6px;background:#d7b3ed;border:1px solid #cba4e6;border-radius:12px;text-align:left}
.field-icon{width:48px;display:grid;place-items:center;flex:none;color:white;font-size:18px}
.field input{width:100%;min-width:0;border:0;border-radius:8px;outline:0;background:var(--panel);color:var(--ink);font:inherit;padding:0 14px}
.field input::placeholder{color:#957fa1}
.submit{align-self:center;min-width:145px;margin-top:24px;padding:10px 20px;border:0;border-radius:24px;background:var(--red);color:white;font:inherit;font-weight:700;cursor:pointer;box-shadow:0 4px 10px #7f132c35}
.submit:hover{background:var(--red-deep)}.auth-note{max-width:420px;color:var(--muted);font-size:13px;margin:16px 0 0}
.auth-switch{margin:12px 0 0}.auth-switch a{font-size:18px}
.terms{display:flex;justify-content:center;gap:8px;align-items:flex-start;color:var(--ink);text-align:left}
.terms input{margin-top:5px;accent-color:var(--red)}
.message{min-height:1.5em;margin:10px 0 0;color:#9e1937}
.site-footer{background:#f3e5ff;color:#351538;padding:24px;min-height:120px}
.site-footer p{max-width:900px;font-size:12px;color:#60456d}
""" + BRAND_STYLES + """
@media(max-width:600px){.topbar{height:56px;padding:0 10px}.brand .dhanraj-wordmark{font-size:clamp(21px,7vw,28px)}.top-link{padding:5px 8px;font-size:12px}.site-nav{gap:12px;min-height:48px}.site-nav a{font-size:12px}.auth-area{padding:12px 8px 0}.auth-card{min-height:390px;padding:24px 16px;border-radius:14px}.field{height:54px}}
"""

AUTH_HEADER = """<header class="site-header">
<div class="topbar"><a class="top-link" href="/login">Login</a><a class="brand" href="/" aria-label="DhanRAJ home"><span class="dhanraj-wordmark"><span class="dhanraj-mark-d">D</span><span>han</span><span class="dhanraj-mark-raj">RAJ</span></span></a><a class="top-link" href="/registration">Register</a></div>
<nav class="site-nav" aria-label="Main navigation"><a href="/">HOME</a><a href="/virtual-game">KINGSTARLINE</a></nav>
</header>"""

AUTH_FOOTER = """<footer class="site-footer"><a class="footer-brand" href="/" aria-label="DhanRAJ home"><span class="dhanraj-wordmark"><span class="dhanraj-mark-d">D</span><span>han</span><span class="dhanraj-mark-raj">RAJ</span></span></a>
<p>Virtual points only. No real money. For entertainment. Accounts are for this website only. virtual coins have no cash value and cannot be redeemed or withdrawn. Never share your password with an administrator or anyone else.</p>
</footer>"""

LOGIN_PAGE = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#1d2b37"><title>Log in | DhanRAJ</title><style>{AUTH_STYLES}</style></head><body>
{AUTH_HEADER}<main class="auth-area"><section class="auth-card" aria-labelledby="page-title">
<h1 id="page-title">Log in to your account</h1>
<form class="auth-form" id="login">
<label class="field"><span class="field-icon" aria-hidden="true">●</span><input id="identifier" name="identifier" placeholder="Username or phone number" autocomplete="username" required aria-label="Username or phone number"></label>
<label class="field"><span class="field-icon" aria-hidden="true">◆</span><input id="password" name="password" type="password" placeholder="Password" autocomplete="current-password" required aria-label="Password"></label>
<button class="submit" type="submit">LOGIN</button></form>
<p class="message" id="message" role="status" aria-live="polite"></p>
<p class="auth-switch">Don't have an account? <a href="/registration">Register now</a></p>
<p class="auth-note">Your password is private. Administrators can grant coins without seeing your login credentials.</p>
</section></main>{AUTH_FOOTER}
<script>
const message=document.getElementById("message");
document.getElementById("login").addEventListener("submit",async event=>{{event.preventDefault();message.textContent="";const form=new FormData(event.currentTarget);try{{const response=await fetch("/auth/login",{{method:"POST",headers:{{"Content-Type":"application/json"}},body:JSON.stringify({{identifier:form.get("identifier"),password:form.get("password")}})}});const result=await response.json();if(!response.ok)throw new Error(result.detail||"Login failed.");location.assign(result.role==="admin"||result.must_change_password?"/admin":"/wallet")}}catch(error){{message.textContent=error.message}}}});
</script></body></html>"""


GAME_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#351538"><title>KingStarline | Virtual Points Game</title>
<style>
*{box-sizing:border-box}:root{color-scheme:light;--ink:#351538;--wine:#60132f;--red:#e73550;--lav:#f3e5ff;--panel:#fffaff;--line:#d3b3e8;--muted:#806b8e}
body{margin:0;min-height:100vh;padding-bottom:78px;background:linear-gradient(145deg,#d9b5f0,#f1e2fc 58%,#d1a9ea);color:var(--ink);font:15px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:inherit;text-decoration:none}button,input,select{font:inherit}.bar{position:sticky;top:0;z-index:5;display:flex;align-items:center;justify-content:space-between;gap:8px;padding:12px;background:#f3e5ff;box-shadow:0 3px 12px #37102140}
.brand{font-size:20px;font-weight:850;letter-spacing:-.04em}.brand b{color:var(--red)}.balance{padding:7px 11px;border-radius:20px;background:#fff;color:var(--wine);font-weight:750}
main{width:min(100%,760px);margin:0 auto;padding:16px 12px}.card{margin:10px 0;padding:16px;border:1px solid #fff9;border-radius:16px;background:#f5e8ff;box-shadow:0 4px 12px #54225a20}
h1,h2,h3,p{margin-top:0}h1{font-size:22px;margin-bottom:8px}h2{font-size:18px;margin-bottom:8px}.muted{color:var(--muted);font-size:13px}
.row{display:flex;align-items:center;justify-content:space-between;gap:12px}.market-card{width:100%;margin:7px 0;padding:13px;border:0;border-radius:14px;text-align:left;background:#fffaff;color:var(--ink);box-shadow:0 3px 9px #54225a18;cursor:pointer}
.market-card.closed{background:#e8e5ea;color:#6b6870;cursor:not-allowed}.market-card.running{border-left:4px solid #27984e}.badge{display:inline-flex;align-items:center;gap:6px;padding:4px 8px;border-radius:20px;background:#dcf4e3;color:#19783a;font-size:11px;font-weight:800}.closed .badge{background:#d7d4da;color:#626068}.dot{width:7px;height:7px;border-radius:50%;background:#21a34a;animation:pulse 1.2s infinite}@keyframes pulse{50%{opacity:.25}}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.game-button,.action,.primary{width:100%;min-height:48px;padding:10px;border:1px solid var(--line);border-radius:14px;background:#fffaff;color:var(--ink);font-weight:700;cursor:pointer}.primary{border:0;background:var(--red);color:white}.actions{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin:12px 0}.form{display:grid;gap:12px}.form label{display:grid;gap:5px;font-size:13px;font-weight:700}.form input,.form select{width:100%;height:46px;padding:0 12px;border:1px solid #cba4e6;border-radius:12px;background:#fffaff;color:var(--ink)}
.session-options{display:flex;gap:10px}.session-options label{flex:1;display:flex;align-items:center;gap:8px;padding:10px;border:1px solid var(--line);border-radius:12px;background:#fffaff}.session-options input{width:auto;height:auto}
.error{min-height:1.4em;color:#9e1937;font-size:13px}.toast{position:fixed;z-index:15;left:50%;bottom:88px;transform:translateX(-50%);width:min(calc(100% - 24px),460px);padding:12px 16px;border-radius:12px;background:#351538;color:white;text-align:center;box-shadow:0 5px 16px #250d2e50}.toast[hidden]{display:none}
.sheet-backdrop{position:fixed;inset:0;z-index:20;display:none;align-items:flex-end;justify-content:center;background:#190d20a8}.sheet-backdrop.open{display:flex}.sheet{width:min(100%,480px);padding:20px 16px max(20px,env(safe-area-inset-bottom));border-radius:22px 22px 0 0;background:#fffaff;box-shadow:0 -8px 24px #17051130}.sheet dl{display:grid;grid-template-columns:1fr auto;gap:8px;font-size:13px}.sheet dt{color:var(--muted)}.sheet dd{margin:0;font-weight:750}
.rates-list{display:grid;gap:7px}.rate-row{display:flex;justify-content:space-between;padding:12px;border-radius:12px;background:#fffaff;font-weight:700}.bottom{position:fixed;z-index:4;right:0;bottom:0;left:0;display:grid;grid-template-columns:repeat(4,1fr);padding:6px 6px max(6px,env(safe-area-inset-bottom));border-top:1px solid var(--line);background:#f5e8ff}.bottom a{display:grid;justify-items:center;gap:2px;color:#705980;font-size:10px}.bottom span{font-size:17px}
footer{padding:12px;text-align:center;color:var(--muted);font-size:12px}
@media(max-width:380px){.grid{grid-template-columns:1fr}.bar{padding:10px}.brand{font-size:18px}}
</style></head><body>
<header class="bar"><a class="brand" href="/virtual-game">King<b>Starline</b></a><a class="balance" id="balance" href="/wallet">Points: ...</a></header>
<main>
<section class="view" id="markets-view"><div class="card"><h1>KingStarline</h1><p class="muted">Choose a market to view its sessions and available games.</p><div id="markets-list" aria-live="polite">Loading markets...</div></div></section>
<section class="view" id="menu-view" hidden><div class="card"><div class="row"><button class="action" id="back-markets" style="width:auto">Back</button><span class="balance" id="selected-market"></span></div><h1>Choose a game</h1><div class="grid" id="game-menu"></div><div class="actions"><button class="action" data-view="rates-view">Win Rates</button><button class="action" data-view="bets-view">My Bets</button><button class="action" data-view="results-view">Results</button><a class="action" href="/wallet" style="display:grid;place-items:center">Wallet</a></div></div></section>
<section class="view" id="bet-view" hidden><div class="card"><div class="row"><button class="action" id="back-menu" style="width:auto">Back</button><a class="balance" href="#rates-view" data-view="rates-view">Win Rates</a></div><h1 id="bet-title"></h1><p id="bet-hint" class="muted"></p><form class="form" id="bet-form" novalidate>
<label>Choose Date<input id="bet-date" type="date" required></label>
<div id="session-field"><span class="muted">Choose Session</span><div class="session-options"><label><input type="radio" name="session" value="open" checked> Open</label><label><input type="radio" name="session" value="close"> Close</label></div></div>
<label id="selection-label">Selection<input id="selection" type="text" inputmode="numeric" autocomplete="off" required></label>
<label>Points<input id="points" type="number" inputmode="numeric" min="10" step="1" value="10" required></label>
<p id="form-error" class="error" role="alert"></p><button class="primary" id="proceed" type="submit">Proceed</button></form></div></section>
<section class="view" id="rates-view" hidden><div class="card"><div class="row"><button class="action" data-back style="width:auto">Back</button><h1>Win Rates</h1></div><p class="muted">Winning amount includes your stake.</p><div class="rates-list" id="rates-list">Loading rates...</div><form class="form" id="calculator"><label>Game<select id="calculator-type"></select></label><label>Points<input type="number" id="calculator-points" min="1" step="1" value="10"></label></form><p id="calculator-result" class="balance">You win: 95 points</p></div></section>
<section class="view" id="bets-view" hidden><div class="card"><div class="row"><button class="action" data-back style="width:auto">Back</button><h1>My Bets</h1></div><div id="bets-list" class="rates-list">Loading bets...</div></div></section>
<section class="view" id="results-view" hidden><div class="card"><div class="row"><button class="action" data-back style="width:auto">Back</button><h1>Results</h1></div><div id="results-list" class="rates-list">Loading results...</div></div></section>
</main><footer>Virtual points only. No real money. For entertainment.</footer>
<nav class="bottom" aria-label="Game navigation"><a href="/virtual-game"><span>⌂</span>Markets</a><a href="/wallet#tab-bids"><span>▤</span>My Bets</a><a href="/virtual-game/rates"><span>◷</span>Win Rates</a><a href="/wallet"><span>◉</span>Wallet</a></nav>
<div id="toast" class="toast" role="status" hidden></div>
<div class="sheet-backdrop" id="confirm-sheet"><section class="sheet" role="dialog" aria-modal="true" aria-labelledby="confirm-title"><h2 id="confirm-title">Confirm entry</h2><dl id="confirmation-details"></dl><p id="confirm-error" class="error" role="alert"></p><div class="actions"><button class="action" id="cancel-confirm">Cancel</button><button class="primary" id="confirm-bet">Confirm</button></div></section></div>
<script>
const types=[
{code:"SINGLE_DIGIT",label:"Single Digit",selection:"digit",session:true},
{code:"JODI",label:"Jodi Digit",selection:"jodi",session:false},
{code:"SINGLE_PANNA",label:"Single Panna",selection:"single",session:true},
{code:"DOUBLE_PANNA",label:"Double Panna",selection:"double",session:true},
{code:"TRIPLE_PANNA",label:"Triple Panna",selection:"triple",session:true}
];
let markets=[],rates=[],user=null,selectedMarket=null,selectedRound=null,selectedType=null,lastView="menu-view",toastTimer;
const $=id=>document.getElementById(id);
function localDate(date=new Date()){return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,"0")}-${String(date.getDate()).padStart(2,"0")}`}
function cookie(name){const value=document.cookie.split("; ").find(item=>item.startsWith(name+"="));return value?decodeURIComponent(value.split("=").slice(1).join("=")):""}
async function api(url,options={}){const headers={...(options.headers||{})};if(options.method&&options.method!=="GET")headers["X-CSRF-Token"]=cookie("site_csrf");const response=await fetch(url,{...options,headers,credentials:"same-origin",cache:"no-store"});const data=await response.json();if(!response.ok)throw new Error(data.detail||"Request failed.");return data}
function showToast(message){$("toast").textContent=message;$("toast").hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>$("toast").hidden=true,3200)}
function showView(id){for(const view of document.querySelectorAll(".view"))view.hidden=view.id!==id;if(id==="rates-view")loadRates();if(id==="bets-view")loadBets();if(id==="results-view")loadResults()}
function h(value){return String(value??"").replace(/[&<>\"']/g,char=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]))}
async function loadProfile(){try{user=await api("/auth/me");$("balance").textContent=`Points: ${Number(user.coin_balance).toLocaleString()}`}catch{$("balance").textContent="Log in for Points";$("balance").href="/login"}}
async function loadMarkets(){try{markets=await api("/api/markets");const list=$("markets-list");list.replaceChildren();for(const market of markets){const button=document.createElement("button");button.className=`market-card ${market.status==="RUNNING"?"running":"closed"}`;button.dataset.cutoff=market.next_cutoff||"";button.innerHTML=`<div class="row"><strong>${h(market.name)}</strong><span class="badge">${market.status==="RUNNING"?'<i class="dot"></i>Market Running':"Betting Closed"}</span></div><div class="row muted"><span>Open: ${h(market.open_time)} - Close: ${h(market.close_time)}</span><span>${h(market.latest_result)}</span></div><div class="row muted"><span>${h(market.betting_session||"")}</span><span class="countdown"></span></div>`;button.addEventListener("click",()=>market.status==="RUNNING"?openMarket(market):showToast("Betting is closed for this market."));list.append(button)}updateCountdowns()}catch(error){$("markets-list").textContent=error.message}}
function updateCountdowns(){for(const card of document.querySelectorAll(".market-card[data-cutoff]")){const target=Date.parse(card.dataset.cutoff);if(!Number.isFinite(target))continue;const seconds=Math.max(0,Math.floor((target-Date.now())/1000));card.querySelector(".countdown").textContent=seconds?`Cutoff in ${Math.floor(seconds/3600)}h ${Math.floor(seconds%3600/60)}m`:"Cutoff passed"}}
async function openMarket(market){selectedMarket=market;try{selectedRound=await api(`/api/markets/${market.id}/today`);rates=await api("/api/bet-types");$("selected-market").textContent=market.name;$("game-menu").replaceChildren();for(const type of types.filter(item=>rates.some(rate=>rate.code===item.code))){const button=document.createElement("button");button.className="game-button";button.textContent=type.label;button.addEventListener("click",()=>openBet(type));$("game-menu").append(button)}showView("menu-view")}catch(error){showToast(error.message)}}
function openBet(type){if(!user){location.assign("/login?next=%2Fgame");return}selectedType=type;lastView="menu-view";$("bet-title").textContent=type.label;$("bet-hint").textContent=`Market: ${selectedMarket.name} · Minimum 10 points`;$("bet-date").value=localDate();$("bet-date").min=localDate();const max=new Date();max.setDate(max.getDate()+7);$("bet-date").max=localDate(max);$("session-field").hidden=!type.session;$("selection").value="";$("selection").placeholder=type.selection==="digit"?"0-9":type.selection==="jodi"?"00-99":"Enter a valid panna";$("selection").maxLength=type.selection==="digit"?1:type.selection==="jodi"?2:3;$("selection").inputMode="numeric";$("points").value="10";$("form-error").textContent="";showView("bet-view");refreshRound()}
async function refreshRound(){try{const date=$("bet-date").value;selectedRound=await api(`/api/markets/${selectedMarket.id}/today?round_date=${date}`);for(const radio of document.querySelectorAll('input[name="session"]')){radio.disabled=radio.value==="open"?!selectedRound.open_betting:!selectedRound.close_betting}const radios=[...document.querySelectorAll('input[name="session"]')];if(radios.every(radio=>radio.disabled))$("form-error").textContent="Betting closed for this round.";else if(document.querySelector('input[name="session"]:checked')?.disabled)radios.find(radio=>!radio.disabled).checked=true;if(selectedType.code==="JODI"&&!selectedRound.jodi_betting)$("form-error").textContent="Betting closed for this round."}catch(error){$("form-error").textContent=error.message}}
$("bet-date").addEventListener("change",refreshRound);document.querySelectorAll('input[name="session"]').forEach(radio=>radio.addEventListener("change",refreshRound));
$("selection").addEventListener("input",async()=>{const input=$("selection"),kind=selectedType?.selection;if(kind==="digit")input.value=input.value.replace(/[^0-9]/g,"").slice(0,1);if(kind==="jodi")input.value=input.value.replace(/[^0-9]/g,"").slice(0,2);if(["single","double","triple"].includes(kind)){input.value=input.value.replace(/[^0-9]/g,"").slice(0,3);if(input.value){try{const result=await api(`/api/panna/suggest?type=${kind}&prefix=${input.value}`);input.setAttribute("list","panna-options");let list=$("panna-options");if(!list){list=document.createElement("datalist");list.id="panna-options";input.after(list)}list.replaceChildren(...result.suggestions.map(value=>{const option=document.createElement("option");option.value=value;return option}))}catch(error){$("form-error").textContent=error.message}}}});
function validPanna(value,kind){if(!/^[0-9]{3}$/.test(value))return false;const order="1234567890",digits=[...value],sorted=[...digits].sort((a,b)=>order.indexOf(a)-order.indexOf(b));if(digits.join("")!==sorted.join(""))return false;const counts=Object.values([...new Set(digits)].map(digit=>digits.filter(item=>item===digit).length));return kind==="single"?counts.length===3:kind==="double"?counts.length===2&&counts.includes(2):counts.length===1}
function validateBet(){const selection=$("selection").value,points=Number($("points").value),rate=rates.find(item=>item.code===selectedType?.code);let message="";if(selectedType?.selection==="digit"&&!/^[0-9]$/.test(selection))message="Enter one digit from 0 to 9.";else if(selectedType?.selection==="jodi"&&!/^[0-9]{2}$/.test(selection))message="Enter a two-digit Jodi.";else if(["single","double","triple"].includes(selectedType?.selection)&&!validPanna(selection,selectedType.selection))message="Invalid panna.";else if(!Number.isInteger(points)||points<(rate?.min_points||10))message=`Minimum points are ${rate?.min_points||10}.`;else if(points>Number(user?.coin_balance||0))message=`Should be less than wallet balance ${Number(user?.coin_balance||0)}`;else if(rate&&points>rate.max_points)message=`Maximum points are ${rate.max_points}.`;return message}
$("bet-form").addEventListener("submit",event=>{event.preventDefault();const error=validateBet();$("form-error").textContent=error;if(error){if(error.startsWith("Should be less than"))showToast(error);return}const session=selectedType.session?document.querySelector('input[name="session"]:checked')?.value:"both";$("confirmation-details").innerHTML=`<dt>Market</dt><dd>${h(selectedMarket.name)}</dd><dt>Date</dt><dd>${h($("bet-date").value)}</dd><dt>Session</dt><dd>${h(session==="both"?"Open + Close":session)}</dd><dt>Selection</dt><dd>${h($("selection").value)}</dd><dt>Points</dt><dd>${Number($("points").value).toLocaleString()}</dd><dt>Balance after entry</dt><dd>${(Number(user.coin_balance)-Number($("points").value)).toLocaleString()}</dd>`;$("confirm-error").textContent="";$("confirm-sheet").classList.add("open")});
$("cancel-confirm").addEventListener("click",()=>$("confirm-sheet").classList.remove("open"));
$("confirm-bet").addEventListener("click",async()=>{const button=$("confirm-bet");button.disabled=true;try{const result=await api("/api/bets",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({round_id:selectedRound.round_id,bet_type:selectedType.code,session:selectedType.session?document.querySelector('input[name="session"]:checked')?.value:"both",selection:$("selection").value,points:Number($("points").value),idempotency_key:crypto.randomUUID()})});user.coin_balance=result.coin_balance;$("balance").textContent=`Points: ${Number(user.coin_balance).toLocaleString()}`;$("confirm-sheet").classList.remove("open");showToast("Virtual points entry recorded.");showView("menu-view")}catch(error){$("confirm-error").textContent=error.message}finally{button.disabled=false}});
async function loadRates(){try{rates=await api("/api/bet-types");rates.sort((a,b)=>types.findIndex(type=>type.code===a.code)-types.findIndex(type=>type.code===b.code));$("rates-list").replaceChildren();$("calculator-type").replaceChildren();for(const rate of rates){const row=document.createElement("div");row.className="rate-row";row.innerHTML=`<span>${h(rate.label)}</span><span>10-${Number(rate.win_per_10).toLocaleString()}</span>`;$("rates-list").append(row);const option=document.createElement("option");option.value=rate.code;option.textContent=rate.label;$("calculator-type").append(option)}updateCalculator()}catch(error){$("rates-list").textContent=error.message}}
function updateCalculator(){const rate=rates.find(item=>item.code===$("calculator-type").value),points=Number($("calculator-points").value);$("calculator-result").textContent=rate&&Number.isFinite(points)&&points>0?`You win: ${Math.floor(points*rate.win_per_10/10).toLocaleString()} points`:"Enter a positive points amount."}
$("calculator-type").addEventListener("change",updateCalculator);$("calculator-points").addEventListener("input",updateCalculator);
async function loadBets(){try{const result=await api("/api/bets");$("bets-list").innerHTML=result.items.length?result.items.map(item=>`<div class="rate-row"><span>${h(item.market)} · ${h(item.game)} ${h(item.selection)}<small class="muted"><br>${h(item.date)} · ${h(item.session)}</small></span><span>${h(item.status)}<br>${Number(item.points)} pts</span></div>`).join(""):"No entries yet."}catch(error){$("bets-list").textContent=error.message}}
async function loadResults(){try{const rows=await api("/api/results/history");$("results-list").innerHTML=rows.length?rows.map(item=>`<div class="rate-row"><span>${h(item.market)} · ${h(item.date)}<small class="muted"><br><a href="/api/verify/${item.round_id}" target="_blank" rel="noopener">Verify RNG</a></small></span><span>${h(item.open_panna||"***")}-${h(item.jodi||"**")}-${h(item.close_panna||"***")}</span></div>`).join(""):"No declared results yet."}catch(error){$("results-list").textContent=error.message}}
$("back-markets").addEventListener("click",()=>showView("markets-view"));$("back-menu").addEventListener("click",()=>showView(lastView));document.querySelectorAll("[data-view]").forEach(button=>button.addEventListener("click",()=>{lastView=selectedMarket?"menu-view":"markets-view";showView(button.dataset.view)}));document.querySelectorAll("[data-back]").forEach(button=>button.addEventListener("click",()=>showView(lastView)));
loadProfile();loadMarkets();setInterval(loadMarkets,60000);setInterval(updateCountdowns,1000);if(location.pathname.endsWith("/rates")){lastView="markets-view";showView("rates-view")}
</script></body></html>"""

REGISTER_PAGE = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#1d2b37"><title>Create account | DhanRAJ</title><style>{AUTH_STYLES}
.registration-dialog{{width:min(calc(100% - 24px),440px);padding:24px;border:1px solid #d3b3e8;border-radius:18px;background:#f8f2ff;color:#351538;box-shadow:0 12px 36px #260b3240}}
.registration-dialog::backdrop{{background:#190d20a8}}
.registration-dialog h2{{margin:0 0 10px;font-size:21px}}
.registration-dialog p{{margin:0 0 20px;color:#60456d}}
.registration-dialog .submit{{margin:0}}
</style></head><body>
{AUTH_HEADER}<main class="auth-area"><section class="auth-card" aria-labelledby="page-title">
<h1 id="page-title">Create your account</h1>
<form class="auth-form" id="register">
<label class="field"><span class="field-icon" aria-hidden="true">●</span><input id="username" name="username" minlength="3" maxlength="32" pattern="[A-Za-z0-9_]+" placeholder="Username" autocomplete="username" required aria-label="Username"></label>
<label class="field"><span class="field-icon" aria-hidden="true">▯</span><input id="phone" name="phone" type="tel" placeholder="Mobile number" autocomplete="tel" required aria-label="Mobile number"></label>
<label class="field"><span class="field-icon" aria-hidden="true">◆</span><input id="password" name="password" type="password" minlength="12" maxlength="128" placeholder="Password (at least 12 characters)" autocomplete="new-password" required aria-label="Password, at least 12 characters"></label>
<label class="terms"><input id="terms" type="checkbox" required><span>I agree: Virtual points only. No real money. For entertainment.</span></label>
<button class="submit" type="submit">REGISTER</button></form>
<p class="message" id="message" role="status" aria-live="polite"></p>
<p class="auth-switch">Already have an account? <a href="/login">Log in</a></p>
<p class="auth-note">Phone ownership is not verified. Use a number you control. Never share your password.</p>
</section></main>{AUTH_FOOTER}
<dialog class="registration-dialog" id="registration-dialog" aria-labelledby="registration-dialog-title" aria-describedby="registration-dialog-message">
<h2 id="registration-dialog-title"></h2><p id="registration-dialog-message" aria-live="polite"></p>
<button class="submit" id="registration-dialog-action" type="button"></button>
</dialog>
<script>
const form=document.getElementById("register"),message=document.getElementById("message"),dialog=document.getElementById("registration-dialog"),dialogTitle=document.getElementById("registration-dialog-title"),dialogMessage=document.getElementById("registration-dialog-message"),dialogAction=document.getElementById("registration-dialog-action");
let registrationSucceeded=false;
function showRegistrationDialog(success,detail){{registrationSucceeded=success;dialogTitle.textContent=success?"Registration successful":"Registration unsuccessful";dialogMessage.textContent=detail;dialogAction.textContent=success?"Continue to login":"Close";dialog.showModal()}}
dialogAction.addEventListener("click",()=>{{if(registrationSucceeded)location.assign("/login");else dialog.close()}});
form.addEventListener("submit",async event=>{{event.preventDefault();message.textContent="";const submit=form.querySelector('button[type="submit"]');submit.disabled=true;submit.textContent="Registering…";const values=new FormData(form);try{{const response=await fetch("/auth/register",{{method:"POST",headers:{{"Content-Type":"application/json"}},body:JSON.stringify({{username:values.get("username"),phone:values.get("phone"),password:values.get("password")}})}});const result=await response.json();const detail=Array.isArray(result.detail)?result.detail.map(item=>item.msg).join(" "):result.detail;if(response.status!==201||result.registered!==true)throw new Error(typeof detail==="string"?detail:(result.message||"Could not confirm registration."));message.textContent=result.message;showRegistrationDialog(true,result.message)}}catch(error){{message.textContent=error.message;showRegistrationDialog(false,error.message)}}finally{{submit.disabled=false;submit.textContent="REGISTER"}}}});
</script></body></html>"""

ACCOUNT_TOOLBAR_SCRIPT = """<style>
.account-toolbar{display:flex;align-items:center;justify-content:flex-end;gap:8px;font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
.account-toolbar .hdr_login,.account-toolbar .hdr_register{width:auto;min-width:0;white-space:nowrap;cursor:pointer}
.account-toolbar .hdr_login,.account-toolbar .hdr_register{border-radius:8px;background:#e73550!important;border-color:#ff8ca3!important;color:#fff!important}
.account-toolbar .account-balance{color:#fff!important;background:#60132f!important}
.header_nav{background:#d8b3f1!important}
.top_header{background-color:#350d26!important;background-image:linear-gradient(45deg,#ffffff08 25%,transparent 25%,transparent 75%,#ffffff08 75%),linear-gradient(-45deg,#ffffff08 25%,transparent 25%,transparent 75%,#ffffff08 75%)!important;background-size:28px 28px!important;border-bottom-color:#9d3754!important}
.nav_wrap{background:#60132f!important}
.nav_wrap ul li a{color:#fff!important}
.active,.active a{color:#ffd9ee!important}
.active svg{fill:#ffd9ee!important}
@media(max-width:480px){.account-toolbar{gap:4px}.account-toolbar .hdr_login,.account-toolbar .hdr_register{padding:5px;font-size:11px}}
</style><script id="newgen-account-toolbar">
(()=>{async function start(){const header=document.querySelector(".top_header");if(!header)return;
try{const response=await fetch("/auth/me",{credentials:"same-origin",cache:"no-store"});if(response.status===401)return;if(!response.ok)throw new Error("Could not load your account.");const user=await response.json();
const login=header.querySelector(".hdr_login"),register=header.querySelector(".hdr_register");if(!register)return;
if(login){login.href="/wallet";login.classList.add("account-user");login.replaceChildren(document.createTextNode(user.username))}
const toolbar=document.createElement("div");toolbar.className="account-toolbar";
const balance=document.createElement("a");balance.className="hdr_login account-balance";balance.href="/wallet";balance.setAttribute("aria-label","Virtual coin balance");toolbar.append(balance);
const updateBalance=()=>{balance.textContent=Number(user.coin_balance).toLocaleString()+" coins"};updateBalance();
if(user.role==="admin"){const admin=document.createElement("a");admin.className="hdr_login";admin.href="/admin";admin.textContent="Admin";toolbar.append(admin)}
const logout=document.createElement("button");logout.className="hdr_register";logout.type="button";logout.textContent="Logout";logout.addEventListener("click",async()=>{logout.disabled=true;try{const csrf=document.cookie.split("; ").find(item=>item.startsWith("site_csrf="))?.split("=").slice(1).join("=");const result=await fetch("/auth/logout",{method:"POST",credentials:"same-origin",headers:{"X-CSRF-Token":decodeURIComponent(csrf||"")}});if(!result.ok)throw new Error("Could not log out. Please try again.");location.assign("/") }catch(error){logout.disabled=false;logout.title=error.message;console.error(error)}});toolbar.append(logout);
register.replaceWith(toolbar);
setInterval(async()=>{try{const refresh=await fetch("/auth/me",{credentials:"same-origin",cache:"no-store"});if(refresh.ok){const current=await refresh.json();balance.textContent=Number(current.coin_balance).toLocaleString()+" coins"}}catch(error){console.error("Could not refresh coin balance.",error)}},30000)
}catch(error){console.error("Could not load account controls.",error)}}if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",start,{once:true});else start()})();
</script>"""


def inject_account_toolbar(content: str) -> str:
    if 'id="newgen-account-toolbar"' in content:
        return content
    closing_body = content.lower().rfind("</body>")
    if closing_body < 0:
        return content + ACCOUNT_TOOLBAR_SCRIPT
    return content[:closing_body] + ACCOUNT_TOOLBAR_SCRIPT + content[closing_body:]


MARKET_HOME_SCRIPT = """<style id="newgen-market-home-style">
body.newgen-market-home{min-height:100vh;background:linear-gradient(145deg,#d9b5f0,#f1e2fc 58%,#d1a9ea);padding-bottom:76px;color:#351538}
body.newgen-market-home .header_nav{min-height:72px;padding-top:72px;background:#d8b3f1!important}
body.newgen-market-home .top_header{height:64px;box-sizing:border-box;padding:8px 14px;background:#f3e5ff!important;border-bottom:1px solid #d3b3e8!important}
body.newgen-market-home .page_logo .dhanraj-wordmark{font-size:clamp(23px,3vw,34px)}
body.newgen-market-home .dhanraj-wordmark{display:inline-flex;align-items:center;gap:0;color:#1f2937;font-family:Inter,"Segoe UI",Arial,sans-serif;font-size:clamp(23px,3vw,34px);font-weight:750;line-height:1;letter-spacing:-.055em;white-space:nowrap;text-decoration:none}
body.newgen-market-home .dhanraj-wordmark:hover{text-decoration:none}
body.newgen-market-home .dhanraj-mark-d{display:inline-grid;width:1.04em;height:1.04em;margin-right:.08em;place-items:center;border-radius:50%;background:#DC2626;color:#111827;font-size:.88em;font-weight:900;letter-spacing:-.04em}
body.newgen-market-home .dhanraj-mark-raj{margin-left:.12em;color:#DC2626;font-weight:850;letter-spacing:-.045em}
body.newgen-market-home footer,body.newgen-market-home .footer{background:#f3e5ff!important;color:#351538!important}
body.newgen-market-home footer a,body.newgen-market-home footer p,body.newgen-market-home footer h1,body.newgen-market-home footer h2,body.newgen-market-home footer h3,body.newgen-market-home .footer a,body.newgen-market-home .footer p,body.newgen-market-home .footer h1,body.newgen-market-home .footer h2,body.newgen-market-home .footer h3{color:#351538!important}
body.newgen-market-home .footer_logo .dhanraj-wordmark{font-size:32px}
body.newgen-market-home .hdr_login,body.newgen-market-home .hdr_register{width:auto;height:auto;min-width:0;padding:6px 9px;border:1px solid #ff8ca3!important;border-radius:20px;background:#e73550!important;color:#fff!important;font-size:12px}
body.newgen-market-home .hdr_login.account-user{max-width:34vw;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;background:#f3e5ff!important;border-color:#f3e5ff!important;color:#512354!important;text-transform:none}
body.newgen-market-home .account-toolbar{gap:5px}
body.newgen-market-home .account-toolbar .account-balance{max-width:33vw;overflow:hidden;text-overflow:ellipsis;background:#f3e5ff!important;border-color:#f3e5ff!important;color:#512354!important;text-transform:none}
body.newgen-market-home .account-toolbar .hdr_register{font-size:11px}
body.newgen-market-home .header_nav nav{display:none!important}
body.newgen-market-home .whatsapp_chat,body.newgen-market-home .calling_btn,body.newgen-market-home #goToTopBtn,body.newgen-market-home #goToDownBtn{display:none!important}
body.newgen-market-home .home-shortcuts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;padding:8px 10px 6px}
body.newgen-market-home .home-shortcuts a{display:flex;align-items:center;justify-content:center;gap:7px;min-height:40px;padding:7px 10px;border-radius:22px;background:#f3e5ff;color:#60456d;font-size:12px;font-weight:650;text-align:center;box-shadow:0 3px 8px #260b3230}
body.newgen-market-home .home-shortcuts .shortcut-icon{width:24px;height:24px;display:grid;place-items:center;flex:none;border-radius:50%;background:#e73550;color:#fff}
body.newgen-market-home #bet-results-section{padding:10px 10px 18px;background:transparent!important}
body.newgen-market-home #bet-results-section h2{margin:0 0 8px;padding:10px;border:0;border-radius:12px;background:#60132f;color:#fff;font-size:17px}
body.newgen-market-home #market-data-status{margin:0 2px 8px;color:#806b8e;font-size:12px;text-align:center}
body.newgen-market-home #bet-results-container{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,290px),1fr));gap:9px}
body.newgen-market-home .result-div-1{display:flex;flex-direction:column;justify-content:space-between;min-width:0;margin:0;padding:10px 12px;border:1px solid #fff9;border-radius:15px;background:#f5e8ff;box-shadow:0 4px 12px #54225a20;text-align:center}
body.newgen-market-home .result-div-2{order:0;width:100%;margin:0;gap:8px;font-size:11px}
body.newgen-market-home .r-d-2-p,body.newgen-market-home .r-d-2-pp{margin:0;padding:0;color:#806b8e}
body.newgen-market-home .result-div-3{order:1;margin:7px 0 0}
body.newgen-market-home .r-d-3-p{margin:0 0 4px;color:#512354;font-size:14px;font-weight:750}
body.newgen-market-home .r-d-3-pp{display:flex;align-items:center;justify-content:center;gap:8px;min-height:30px;margin:0;color:#e73550;font-size:18px;font-weight:800;font-variant-numeric:tabular-nums}
body.newgen-market-home .r-d-3-span{color:#bd203f;font-size:19px}
body.newgen-market-home .result-div-4{order:2;justify-content:center;gap:8px;margin:6px 0 0}
body.newgen-market-home .result-div-4 a{height:auto;margin:0;padding:4px 12px;border:0;border-radius:18px;background:#e73550;color:#fff;font-size:11px}
body.newgen-market-home .result-div-4 a::before{display:none!important}
body.newgen-market-home .market-bottom-nav{position:fixed;z-index:10001;right:0;bottom:0;left:0;display:grid;grid-template-columns:repeat(5,1fr);padding:6px 6px max(6px,env(safe-area-inset-bottom));border-top:1px solid #cba4e6;background:#f5e8ff;box-shadow:0 -4px 12px #54225a20}
body.newgen-market-home .market-bottom-nav a{display:grid;justify-items:center;gap:2px;color:#705980;font-size:10px}
body.newgen-market-home .market-bottom-nav .nav-icon{width:29px;height:29px;display:grid;place-items:center;border-radius:50%;font-size:16px}
body.newgen-market-home .market-bottom-nav a[aria-current="page"]{color:#e73550;font-weight:750}
body.newgen-market-home .market-bottom-nav a[aria-current="page"] .nav-icon{background:#e73550;color:#fff}
body.newgen-market-home .kingstarline-panel{padding:12px 10px 0}
body.newgen-market-home .kingstarline-card{padding:16px 14px;border:1px solid rgba(84,34,90,.12);border-radius:18px;background:linear-gradient(135deg,#fff8ff,#f0d8ff 45%,#f3e5ff);box-shadow:0 10px 24px rgba(84,34,90,.12)}
body.newgen-market-home .kingstarline-card .eyebrow{display:block;margin-bottom:8px;color:#7c5a85;font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase}
body.newgen-market-home .kingstarline-cta{position:relative;display:flex;align-items:center;justify-content:space-between;gap:12px;width:min(100%,360px);margin:0 auto;padding:15px 17px;border:1px solid #ff9aaf;border-radius:16px;background:linear-gradient(135deg,#d43d5d,#e73550 55%,#a51a39);color:#fff;font-size:18px;font-weight:800;text-decoration:none;box-shadow:0 0 0 2px #e7355033,0 0 18px 4px #e7355080,0 9px 18px #7b0f2b40;animation:kingstarline-glow 1.8s ease-in-out infinite}
body.newgen-market-home .kingstarline-cta:hover{color:#fff;text-decoration:none;transform:translateY(-1px)}
body.newgen-market-home .kingstarline-cta .kingstarline-label{display:flex;flex-direction:column;line-height:1.15;text-align:left}
body.newgen-market-home .kingstarline-cta small{font-size:11px;opacity:.9;font-weight:600}
@keyframes kingstarline-glow{0%,100%{box-shadow:0 0 0 2px #e7355033,0 0 12px 2px #e7355066,0 9px 18px #7b0f2b40}50%{box-shadow:0 0 0 3px #e7355066,0 0 24px 8px #e73550b3,0 9px 22px #7b0f2b66}}
@media(prefers-reduced-motion:reduce){body.newgen-market-home .kingstarline-cta{animation:none}}
@media(min-width:700px){body.newgen-market-home #bet-results-section{width:min(100%,1050px);margin:0 auto}body.newgen-market-home .market-bottom-nav{left:50%;right:auto;width:min(100%,760px);transform:translateX(-50%);border-radius:16px 16px 0 0}}
@media(max-width:380px){body.newgen-market-home .top_header{padding-right:7px;padding-left:7px}body.newgen-market-home .page_logo .dhanraj-wordmark{font-size:clamp(21px,7vw,28px)}body.newgen-market-home .hdr_login,body.newgen-market-home .hdr_register{padding:5px 6px;font-size:10px}}
</style><script id="newgen-market-home">
(()=>{function initialize(){const results=document.getElementById("bet-results-section"),main=document.querySelector("main");if(!results||!main)return;
document.body.classList.add("newgen-market-home");document.title="DhanRAJ | Market Results";const logo=document.querySelector(".page_logo a")||document.querySelector("a.page_logo");if(logo){logo.href="/";logo.classList.add("dhanraj-wordmark");logo.setAttribute("aria-label","DhanRAJ home");logo.innerHTML='<span class="dhanraj-mark-d">D</span><span>han</span><span class="dhanraj-mark-raj">RAJ</span>'}results.style.background="transparent";const status=document.createElement("p");status.id="market-data-status";status.setAttribute("role","status");status.setAttribute("aria-live","polite");status.textContent="Loading market results…";results.insertBefore(status,results.querySelector("#bet-results-container"));
for(const child of [...main.children]){if(child!==results)child.hidden=true}main.prepend(results);
const siteHeader=document.querySelector(".header_nav");
const kingstarlinePanel=document.createElement("section");kingstarlinePanel.className="kingstarline-panel";kingstarlinePanel.innerHTML='<div class="kingstarline-card"><span class="eyebrow">Virtual Points Game</span><a class="kingstarline-cta" href="/virtual-game"><span class="kingstarline-label"><span>KingStarline</span><small>Tap to Play</small></span><span aria-hidden="true">▶</span></a></div>';
if(siteHeader)siteHeader.insertAdjacentElement("afterend",kingstarlinePanel);else main.insertBefore(kingstarlinePanel,results);
const shortcuts=document.createElement("div");shortcuts.className="home-shortcuts";shortcuts.innerHTML='<a href="#bet-results-section"><span class="shortcut-icon">▶</span>Market results</a><a href="/wallet"><span class="shortcut-icon">◉</span>Virtual coin account</a><a data-dhanraj-support href="https://wa.me/918699915927"><span class="shortcut-icon">◉</span>WhatsApp support</a><a href="/wallet#tab-fund-request"><span class="shortcut-icon">＋</span>Request coin credit or debit</a>';
fetch("/auth/me",{cache:"no-store"}).then(response=>response.ok?response.json():null).then(user=>{if(!user)return;const link=shortcuts.querySelector("[data-dhanraj-support]"),identity=`Hello, I need help with my DhanRAJ account.\\nUsername: ${user.username}\\nPhone: ${user.phone||"Not provided"}\\nRequest: Please help me with my account or service issue.`;link.href="https://wa.me/918699915927?text="+encodeURIComponent(identity)}).catch(error=>console.error("Could not personalize DhanRAJ support link:",error));
if(siteHeader)siteHeader.insertAdjacentElement("afterend",shortcuts);else main.insertBefore(shortcuts,results);
const homeFooter=document.querySelector("footer,.footer");if(homeFooter&&!homeFooter.textContent.includes("Virtual points only. No real money. For entertainment.")){const note=document.createElement("p");note.textContent="Virtual points only. No real money. For entertainment.";homeFooter.append(note)}
const bottomNav=document.createElement("nav");bottomNav.className="market-bottom-nav";bottomNav.setAttribute("aria-label","Site navigation");bottomNav.innerHTML='<a href="/wallet#tab-bids"><span class="nav-icon">▤</span>My Activity</a><a href="/wallet#tab-passbook"><span class="nav-icon">◷</span>Passbook</a><a href="/" aria-current="page"><span class="nav-icon">⌂</span>Markets</a><a href="/wallet#tab-funds"><span class="nav-icon">▣</span>Coins</a><a href="/wallet#tab-support"><span class="nav-icon">•••</span>Support</a>';document.body.append(bottomNav);
let refreshing=false;function displayValue(record,key,statusKey,placeholder){const value=record[key];return String(record[statusKey])==="1"&&value!=null?String(value):placeholder}
async function refresh(){if(refreshing||document.visibilityState==="hidden")return;refreshing=true;try{const response=await fetch("/front/fetch_updated_results",{cache:"no-store",headers:{"X-Requested-With":"XMLHttpRequest"}});if(!response.ok)throw new Error(`Market results request failed (${response.status}).`);const records=await response.json();if(!Array.isArray(records))throw new Error("Market results response was not a list.");let rendered=0;for(const record of records){const cell=document.getElementById(`dynamic-data-${record.id}`);if(!cell)continue;const openPanel=displayValue(record,"open_digit","open_stat","***"),openResult=displayValue(record,"open_result","open_stat","*"),closeResult=displayValue(record,"close_result","close_stat","*"),closePanel=displayValue(record,"close_digit","close_stat","***");const spans=[document.createElement("span"),document.createElement("span"),document.createElement("span")];spans[0].textContent=openPanel==="0"?"000":openPanel;spans[1].className="r-d-3-span";spans[1].textContent=`${openResult}${closeResult}`;spans[2].textContent=closePanel==="0"?"000":closePanel;cell.replaceChildren(...spans);rendered++}if(!rendered)throw new Error("No matching market cards were found.");status.textContent=`Showing ${rendered} markets · Updated ${new Date().toLocaleTimeString()}`}catch(error){status.textContent="Market results are temporarily unavailable. Retrying…";console.error("Could not refresh market results:",error)}finally{refreshing=false}}
refresh();setInterval(refresh,60000);document.addEventListener("visibilitychange",()=>{if(document.visibilityState==="visible")refresh()})}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",initialize,{once:true});else initialize()})();
</script>"""


def inject_market_home(content: str) -> str:
    if 'id="newgen-market-home"' in content or 'id="bet-results-section"' not in content:
        return content
    closing_body = content.lower().rfind("</body>")
    if closing_body < 0:
        return content + MARKET_HOME_SCRIPT
    return content[:closing_body] + MARKET_HOME_SCRIPT + content[closing_body:]


WALLET_STYLES = """
*{box-sizing:border-box}:root{color-scheme:light;--ink:#351538;--wine:#60132f;--wine-deep:#350d26;--red:#e73550;--red-deep:#bd203f;--lavender:#e8c9ff;--lavender-light:#f3e5ff;--panel:#f8f2ff;--muted:#806b8e;--line:#d3b3e8}
body{margin:0;min-height:100vh;background:linear-gradient(150deg,#dcb9f5,#f3e5ff 55%,#d1a9ee);color:var(--ink);font:15px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif;padding-bottom:82px}
a{color:inherit;text-decoration:none}.app-header{position:sticky;top:0;z-index:5;background:#f3e5ff;color:var(--ink);box-shadow:0 3px 12px #37102140}
.app-top{height:56px;padding:0 12px;display:flex;align-items:center;justify-content:space-between;gap:8px}
.app-brand{display:flex;align-items:center}
.user-pill,.coin-pill{max-width:45vw;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;padding:6px 11px;border-radius:18px;background:#f8eaff;color:var(--wine);font-weight:700;box-shadow:0 2px 6px #17051124}
.app-top-right{display:flex;align-items:center;gap:7px}.coin-pill{font-variant-numeric:tabular-nums}
.small-button,.primary-button{border:0;border-radius:22px;background:var(--red);color:white;padding:9px 14px;font:inherit;font-weight:700;cursor:pointer;box-shadow:0 3px 8px #7f132c2c}
.app-greeting{padding:0 14px 12px;color:#351538;display:flex;align-items:center;justify-content:space-between;gap:8px}.app-greeting strong{font-size:17px}
.feature-strip,.contact-strip{display:flex;gap:8px;padding:8px 12px;overflow-x:auto;scrollbar-width:none}
.feature-strip::-webkit-scrollbar,.contact-strip::-webkit-scrollbar{display:none}
.feature-pill,.contact-pill{display:flex;align-items:center;justify-content:center;gap:7px;flex:1 0 max-content;padding:9px 14px;border:0;border-radius:22px;background:#f3e5ff;color:var(--ink);font:inherit;font-size:13px;box-shadow:0 3px 8px #260b3230}
.feature-pill{background:#f1ddff}.feature-icon{width:24px;height:24px;display:grid;place-items:center;border-radius:50%;background:var(--red);color:white}
.contact-strip{padding-top:2px}.contact-pill{min-width:0;flex:1;background:#ead4fa;color:#60456d;font-size:12px}
.dashboard-label{margin:4px 2px 8px;color:var(--muted);font-size:12px;font-weight:700;letter-spacing:.06em;text-transform:uppercase}
.app-wrap{width:min(100%,760px);margin:0 auto;padding:16px 14px}
.balance-card{padding:18px;border-radius:16px;background:linear-gradient(125deg,#fff5ff,#e9caff);box-shadow:0 5px 16px #54225a24}
.balance-label{margin:0;color:var(--muted);font-size:13px}.balance-value{margin:2px 0;color:var(--red);font-size:32px;font-weight:800}.disclaimer{font-size:12px;color:var(--muted)}
.quick-actions{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:14px 0}
.action-card,.panel-card,.menu-card{background:#f5e8ff;border:1px solid #fff9;border-radius:14px;box-shadow:0 4px 12px #54225a20}
.action-card{padding:12px;display:flex;align-items:center;gap:10px;font-weight:650}
.action-icon{width:36px;height:36px;flex:none;border-radius:50%;display:grid;place-items:center;background:var(--red);color:white;font-size:17px}
.panel-card{padding:16px;margin:12px 0}.panel-card h2{margin:0 0 5px;font-size:17px}.panel-card p{color:var(--muted)}
.menu-card{margin:9px 0;overflow:hidden}.menu-row{width:100%;border:0;background:transparent;color:var(--ink);font:inherit;text-align:left;padding:13px;display:flex;align-items:center;gap:12px;cursor:pointer}
.menu-row+.menu-row{border-top:1px solid var(--line)}.menu-copy{flex:1}.menu-title{display:block;font-weight:700}.menu-subtitle{display:block;color:var(--muted);font-size:12px}.menu-arrow{color:#805499;font-size:20px}
.form-stack{display:grid;gap:11px;margin-top:12px}.form-stack label{font-size:13px;font-weight:650}.form-stack input,.form-stack select{display:block;width:100%;height:46px;margin-top:4px;border:1px solid #cba4e6;border-radius:24px;padding:0 14px;background:#fffaff;color:var(--ink);font:inherit}
.form-stack .primary-button{justify-self:center;min-width:150px}.notice{min-height:1.4em;color:#9e1937;font-size:13px}
.credit-feedback{position:fixed;z-index:10010;top:16px;left:50%;display:flex;align-items:center;gap:14px;width:min(calc(100% - 24px),480px);padding:14px 16px;transform:translateX(-50%);border:1px solid #cba4e6;border-radius:14px;background:#f5e8ff;color:var(--ink);box-shadow:0 8px 28px #260b3240;font-weight:650}
.credit-feedback[hidden]{display:none}.credit-feedback[data-result="success"]{border-color:#6a9c77;background:#edf8ef;color:#235b31}.credit-feedback[data-result="error"]{border-color:#d97b8c;background:#fff0f2;color:#8f1831}
.credit-feedback button{flex:none;margin-left:auto;border:0;background:transparent;color:inherit;font:inherit;font-size:20px;cursor:pointer}
.table-wrap{overflow:auto}table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;vertical-align:top;padding:9px 7px;border-bottom:1px solid var(--line)}th{color:var(--muted)}
.bottom-nav{position:fixed;z-index:10;bottom:0;left:0;right:0;display:grid;grid-template-columns:repeat(5,1fr);padding:7px max(8px,env(safe-area-inset-left)) calc(7px + env(safe-area-inset-bottom));background:#f5e8ff;border-top:1px solid #cba4e6;box-shadow:0 -4px 12px #54225a20}
.nav-item{border:0;background:transparent;color:#705980;font:inherit;font-size:10px;display:grid;justify-items:center;gap:2px;cursor:pointer}.nav-icon{width:31px;height:31px;border-radius:50%;display:grid;place-items:center;font-size:16px}.nav-item[aria-current="page"]{color:var(--red);font-weight:750}.nav-item[aria-current="page"] .nav-icon{background:var(--red);color:white}
.tab-panel[hidden]{display:none}
.admin-shell{width:min(100%,680px);margin:0 auto;padding:22px 14px}.admin-panel{padding:17px;margin:12px 0;border-radius:15px;background:#f5e8ff;box-shadow:0 4px 12px #54225a20}
.admin-panel label{display:block;margin:10px 0 4px;font-size:13px;font-weight:650}.admin-panel input{width:100%;height:44px;border:1px solid #cba4e6;border-radius:10px;padding:0 12px;background:#fffaff;color:var(--ink);font:inherit}.admin-panel .primary-button{margin-top:14px}
@media(min-width:700px){.app-wrap{padding-top:24px}.balance-card{padding:24px}.bottom-nav{left:50%;right:auto;width:min(100%,760px);transform:translateX(-50%);border-radius:16px 16px 0 0}}
""" + BRAND_STYLES

WALLET_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#1d2b37"><title>My account | DhanRAJ</title><style>""" + WALLET_STYLES + """</style></head><body>
<header class="app-header"><div class="app-top"><a class="user-pill" href="#tab-home" aria-label="Your profile"><span aria-hidden="true">☻</span> <span id="username">…</span></a><div class="app-top-right"><span class="coin-pill"><span aria-hidden="true">◉</span> <span id="header-balance">… coins</span></span><button class="small-button" id="logout" type="button">Log out</button></div></div><div class="app-greeting"><a class="app-brand" href="/" aria-label="DhanRAJ home"><span class="dhanraj-wordmark"><span class="dhanraj-mark-d">D</span><span>han</span><span class="dhanraj-mark-raj">RAJ</span></span></a><span>Account overview</span></div><div class="feature-strip"><a class="feature-pill" href="/"><span class="feature-icon">▶</span>Market results</a><button class="feature-pill" type="button" data-open-tab="bids"><span class="feature-icon">▶</span>My virtual activity</button></div><div class="contact-strip"><a class="contact-pill" data-dhanraj-support href="https://wa.me/918699915927" target="_blank" rel="noopener noreferrer"><span class="feature-icon">◉</span>WhatsApp support · 8699915927</a></div></header>
<main class="app-wrap">
<section class="tab-panel" id="tab-home">
<div class="balance-card"><p class="balance-label">VIRTUAL COIN BALANCE</p><p class="balance-value" id="balance">Loading…</p><p class="disclaimer">Virtual coins only. No cash value, deposits, withdrawals, or payouts.</p></div>
<p class="dashboard-label">Your account</p><div class="quick-actions"><button class="action-card" type="button" data-open-tab="funds"><span class="action-icon">＋</span><span>Request virtual coins</span></button><button class="action-card" type="button" data-open-tab="passbook"><span class="action-icon">◷</span><span>Coin history</span></button></div>
<section class="panel-card"><h2>Account details</h2><p id="profile" class="disclaimer"></p><p>Coin credits are added by an administrator. Keep your login password private; an admin never needs it.</p></section>
<section class="menu-card"><button class="menu-row" type="button" data-open-tab="passbook"><span class="action-icon">◷</span><span class="menu-copy"><span class="menu-title">Coin activity</span><span class="menu-subtitle">View credits and virtual entries</span></span><span class="menu-arrow">›</span></button><a class="menu-row" href="/"><span class="action-icon">⌂</span><span class="menu-copy"><span class="menu-title">Market results</span><span class="menu-subtitle">Return to the results page</span></span><span class="menu-arrow">›</span></a></section>
</section>
<section class="tab-panel" id="tab-bids" hidden><section class="panel-card"><h1>My Activity</h1><p>Your previous virtual-point activity appears here. New game entries are made from an open market.</p><div class="table-wrap"><table><thead><tr><th>Date</th><th>Activity</th><th>Points</th><th>Balance</th></tr></thead><tbody id="activity"></tbody></table></div><p id="activity-empty" class="disclaimer" hidden>No previous activity yet.</p></section></section>
<section class="tab-panel" id="tab-passbook" hidden><section class="panel-card"><h1>Passbook</h1><p>All virtual-point transactions, including the reason and resulting balance.</p><div class="table-wrap"><table><thead><tr><th>Date</th><th>Type</th><th>Reason</th><th>Credited</th><th>Debited</th><th>Balance</th></tr></thead><tbody id="history"></tbody></table></div><p id="history-empty" class="disclaimer" hidden>No transactions yet.</p></section></section>
<section class="tab-panel" id="tab-funds" hidden><p class="dashboard-label">Virtual coin center</p><section class="panel-card"><h1>Coins</h1><p class="balance-value" id="funds-balance">Loading…</p><p>Admin-granted demo credits only. No cash deposits, withdrawals, or payouts are available.</p></section><div class="menu-card"><button class="menu-row" type="button" data-open-tab="fund-request"><span class="action-icon">＋</span><span class="menu-copy"><span class="menu-title">Request virtual credits</span><span class="menu-subtitle">Send a request to support; credits are added by an admin</span></span><span class="menu-arrow">›</span></button><button class="menu-row" type="button" data-open-tab="passbook"><span class="action-icon">◷</span><span class="menu-copy"><span class="menu-title">Coin history</span><span class="menu-subtitle">Review admin credits and virtual entries</span></span><span class="menu-arrow">›</span></button></div></section>
<section class="tab-panel" id="tab-fund-request" hidden><section class="panel-card"><h1>Request a coin adjustment</h1><p>This opens WhatsApp to support with a prefilled request. Coins change only after an administrator reviews and applies it.</p><form class="form-stack" id="request-form"><label>Request type<select id="request-type" required><option value="credit">Request credit (add virtual coins)</option><option value="withdrawal">Request withdrawal (remove virtual coins)</option></select></label><label>Coins<input id="request-amount" type="number" min="1" max="1000000" placeholder="Enter amount" required></label><div id="withdrawal-bank-fields" hidden><label>Full name<input id="bank-holder" type="text" maxlength="120" placeholder="Account holder name"></label><label>Bank account number<input id="bank-account" type="text" maxlength="40" placeholder="Bank account number"></label><label>IFSC code<input id="bank-ifsc" type="text" maxlength="20" placeholder="IFSC code"></label></div><button class="primary-button">Send request on WhatsApp · 8699915927</button></form><p class="notice" id="fund-message" role="status" aria-live="polite"></p></section></section>
<section class="tab-panel" id="tab-support" hidden><section class="panel-card"><h1>Support</h1><p>Chat about your DhanRAJ account. Your username and phone number are included in the prefilled message. Never send anyone your password or verification codes.</p><div class="quick-actions"><a class="action-card" data-dhanraj-support href="https://wa.me/918699915927" target="_blank" rel="noopener noreferrer"><span class="action-icon">◉</span><span>WhatsApp support · 8699915927</span></a></div><p class="disclaimer">Support cannot process cash deposits or withdrawals.</p></section></section>
</main>
<nav class="bottom-nav" aria-label="Account navigation"><button class="nav-item" type="button" data-tab="bids"><span class="nav-icon">▤</span>My Activity</button><button class="nav-item" type="button" data-tab="passbook"><span class="nav-icon">◷</span>Passbook</button><button class="nav-item" type="button" data-tab="home" aria-current="page"><span class="nav-icon">⌂</span>Home</button><button class="nav-item" type="button" data-tab="funds"><span class="nav-icon">▣</span>Coins</button><button class="nav-item" type="button" data-tab="support"><span class="nav-icon">•••</span>Support</button></nav>
<footer class="site-footer">Virtual points only. No real money. For entertainment.</footer>
<script>
const tabNames=["home","bids","passbook","funds","fund-request","support"];
function showTab(name){if(!tabNames.includes(name))name="home";for(const tab of tabNames)document.getElementById("tab-"+tab).hidden=tab!==name;for(const button of document.querySelectorAll(".nav-item")){if(button.dataset.tab===name||((name==="fund-request")&&button.dataset.tab==="funds"))button.setAttribute("aria-current","page");else button.removeAttribute("aria-current")}}
function showHashTab(){const tab=location.hash.replace("#tab-","");if(tabNames.includes(tab))showTab(tab)}
document.querySelectorAll("[data-tab]").forEach(button=>button.addEventListener("click",()=>showTab(button.dataset.tab)));
document.querySelectorAll("[data-open-tab]").forEach(button=>button.addEventListener("click",()=>showTab(button.dataset.openTab)));
window.addEventListener("hashchange",showHashTab);showHashTab();
let currentUser=null;
function whatsappUrl(phone,text){return "https://wa.me/"+phone+"?text="+encodeURIComponent(text)}
function cookie(name){const item=document.cookie.split("; ").find(value=>value.startsWith(name+"="));return item?decodeURIComponent(item.split("=").slice(1).join("=")):""}
async function api(path,options={}){const headers={"Content-Type":"application/json",...(options.headers||{})};if(options.method&&options.method!=="GET")headers["X-CSRF-Token"]=cookie("site_csrf");const response=await fetch(path,{...options,headers});const result=await response.json();if(!response.ok)throw new Error(result.detail||"Request failed.");return result}
async function load(){try{const [profile,data]=await Promise.all([api("/auth/me"),api("/wallet/history")]);currentUser=profile;document.getElementById("username").textContent=profile.username;document.getElementById("profile").textContent=(profile.phone||"Administrator account")+" · Signed in";const identity=`Username: ${profile.username}\\nPhone: ${profile.phone||"Not provided"}`;for(const link of document.querySelectorAll("[data-dhanraj-support]"))link.href=whatsappUrl("918699915927",`Hello, I need help with my DhanRAJ account.\\n${identity}\\nRequest: Please help me with my account or service issue.`);for(const id of ["balance","funds-balance"])document.getElementById(id).textContent=Number(data.coin_balance).toLocaleString()+" coins";document.getElementById("header-balance").textContent=Number(data.coin_balance).toLocaleString()+" coins";const activity=document.getElementById("activity"),history=document.getElementById("history");activity.replaceChildren();history.replaceChildren();for(const item of data.transactions){const date=new Date(item.created_at).toLocaleString(),kind=item.kind.replaceAll("_"," "),credited=item.amount_delta>0?Number(item.amount_delta).toLocaleString():"—",debited=item.amount_delta<0?Math.abs(Number(item.amount_delta)).toLocaleString():"—",balance=Number(item.balance_after).toLocaleString();const activityRow=document.createElement("tr");for(const value of [date,item.description,`${item.amount_delta>0?"+":""}${Number(item.amount_delta).toLocaleString()}`,balance]){const cell=document.createElement("td");cell.textContent=value;activityRow.append(cell)}activity.append(activityRow);const historyRow=document.createElement("tr");for(const value of [date,kind,item.description,credited,debited,balance]){const cell=document.createElement("td");cell.textContent=value;historyRow.append(cell)}history.append(historyRow)}document.getElementById("activity-empty").hidden=data.transactions.length>0;document.getElementById("history-empty").hidden=data.transactions.length>0}catch(error){location.assign("/login")}}
const requestType=document.getElementById("request-type");const bankFields=document.getElementById("withdrawal-bank-fields");function toggleBankFields(){bankFields.hidden=requestType.value!=="withdrawal";}requestType.addEventListener("change",toggleBankFields);toggleBankFields();
document.getElementById("request-form").addEventListener("submit",async event=>{event.preventDefault();const message=document.getElementById("fund-message");message.textContent="";if(!currentUser){message.textContent="Please log in again before sending a request.";return}const type=document.getElementById("request-type").value;const amount=Number(document.getElementById("request-amount").value);const endpoint=type==="withdrawal"?"/api/requests/withdraw":"/api/requests/credit";if(type==="credit"&&amount<500){message.textContent="Minimum credit request is 500 coins.";message.dataset.result="error";return}if(type==="withdrawal"&&amount<1000){message.textContent="Minimum withdrawal request is 1,000 coins.";message.dataset.result="error";return}try{const payload={amount};if(type==="withdrawal"){payload.account_holder_name=document.getElementById("bank-holder").value;payload.bank_account_number=document.getElementById("bank-account").value;payload.ifsc_code=document.getElementById("bank-ifsc").value;}await api(endpoint,{method:"POST",body:JSON.stringify(payload)});const text=type==="withdrawal"?`Withdrawal request\nName: ${payload.account_holder_name||currentUser.username}\nAmount: ${amount} coins\nAccount: ${payload.bank_account_number||"Not provided"}\nIFSC: ${payload.ifsc_code||"Not provided"}\nUser ID: ${currentUser.username}`:`Credit request\nUser: ${currentUser.username}\nUser ID: ${currentUser.username}\nAmount: ${amount} coins\nPlease review and process this request.`;location.href=whatsappUrl("918699915927",text);message.textContent="Request saved. WhatsApp is opening for confirmation.";message.dataset.result="success";}catch(error){message.textContent=error.message;message.dataset.result="error"}});
document.getElementById("logout").addEventListener("click",async()=>{try{await api("/auth/logout",{method:"POST"});location.assign("/login")}catch(error){document.getElementById("activity-empty").textContent=error.message;document.getElementById("activity-empty").hidden=false}});
setInterval(load,30000);load();
</script></body></html>"""


ADMIN_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#1d2b37"><title>Admin | DhanRAJ</title><style>""" + WALLET_STYLES + """</style></head><body>
<header class="app-header"><div class="app-top"><a class="app-brand" href="/" aria-label="DhanRAJ home"><span class="dhanraj-wordmark"><span class="dhanraj-mark-d">D</span><span>han</span><span class="dhanraj-mark-raj">RAJ</span></span></a><div class="app-top-right"><a class="coin-pill" href="/wallet">My account</a><button class="small-button" id="logout" type="button">Log out</button></div></div></header>
<main class="admin-shell"><p id="profile" class="disclaimer"></p><p id="message" class="notice" role="status" aria-live="polite"></p>
<div style="display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin:12px 0 16px;">
  <button type="button" class="primary-button" data-admin-tab="credit">Credit Requests</button>
  <button type="button" class="primary-button" data-admin-tab="withdrawal">Withdraw Requests</button>
</div>
<section class="admin-panel" id="no-session" hidden><h1>Admin sign-in required</h1><p>Sign in with the administrator account to manage virtual credits.</p><a href="/login?next=%2Fadmin">Continue to admin sign-in</a></section>
<section class="admin-panel" id="wrong-account" hidden><h1>Administrator account required</h1><p>Sign out of this account and sign in as an administrator to manage virtual credits.</p><button class="primary-button" id="switch-account">Switch account</button></section>
<section class="admin-panel" id="change-section" hidden><h1>Update administrator password</h1><p>Choose a new password of at least 12 characters before using admin tools.</p><form id="change-password"><label>Current password</label><input name="current_password" type="password" autocomplete="current-password" required><label>New password</label><input name="new_password" type="password" minlength="12" autocomplete="new-password" required><button class="primary-button">Change password</button></form></section>
<section class="admin-panel" id="credit-section" hidden><h1>Grant virtual coins</h1><p>Identify the account with its registered username and phone number. Never ask for a user's password. These coins cannot be redeemed or withdrawn.</p>
<form class="form-stack" id="credit"><label>Username<input name="username" minlength="3" maxlength="32" autocomplete="off" required></label><label>Registered phone number<input name="phone" type="tel" placeholder="+91 9876543210" autocomplete="off" required></label><label>Coins to add<input name="amount" type="number" min="1" max="1000000" required></label><button class="primary-button">Add virtual coins</button></form>
<hr>
<h2>Debit virtual coins</h2><p>Debits cannot exceed the user's current balance. The adjustment is recorded in the user's coin history.</p>
<form class="form-stack" id="debit"><label>Username<input name="username" minlength="3" maxlength="32" autocomplete="off" required></label><label>Registered phone number<input name="phone" type="tel" placeholder="+91 9876543210" autocomplete="off" required></label><label>Coins to remove<input name="amount" type="number" min="1" max="1000000" required></label><button class="primary-button">Debit virtual coins</button></form>
<hr><h2>Declare game result</h2><p>Results are immutable after declaration. Enter a panna only after the session cutoff.</p>
<form class="form-stack" id="game-result"><label>Market and round<select id="result-round" required></select></label><label>Session<select id="result-session"><option value="open">Open</option><option value="close">Close</option></select></label><label>Panna<input id="result-panna" inputmode="numeric" pattern="[0-9]{3}" maxlength="3" required></label><button class="primary-button">Declare result</button></form>
<hr><h2>Market schedule</h2><form class="form-stack" id="market-edit"><label>Market<select id="market-edit-id" required></select></label><label>Name<input id="market-name" maxlength="80" required></label><label>Open time<input id="market-open" type="time" required></label><label>Close time<input id="market-close" type="time" required></label><label>Active weekdays (0 Monday through 6 Sunday)<input id="market-days" value="0,1,2,3,4,5,6" required></label><label>Bet cutoff minutes<input id="market-cutoff" type="number" min="1" max="180" value="10" required></label><label>Paused<select id="market-paused"><option value="false">No</option><option value="true">Yes</option></select></label><label>Sort order<input id="market-sort" type="number" min="0" value="0" required></label><button class="primary-button">Save market</button></form>
<hr><h2>Win rates</h2><form class="form-stack" id="rate-edit"><label>Game<select id="rate-code"></select></label><label>Win per 10 points<input id="rate-value" type="number" min="1" required></label><label>Minimum points<input id="rate-min" type="number" min="1" required></label><label>Maximum points<input id="rate-max" type="number" min="1" required></label><label>Enabled<select id="rate-enabled"><option value="true">Yes</option><option value="false">No</option></select></label><button class="primary-button">Save win rate</button></form>
</section></main>
<div class="credit-feedback" id="credit-feedback" hidden role="status" aria-live="polite"><span id="credit-feedback-message"></span><button id="credit-feedback-close" type="button" aria-label="Dismiss notification">×</button></div>
<footer class="site-footer">Virtual points only. No real money. For entertainment.</footer>
<script>
const message=document.getElementById("message");
let feedbackTimeout;
function showCreditFeedback(text,result){const feedback=document.getElementById("credit-feedback");feedback.dataset.result=result;feedback.setAttribute("role",result==="error"?"alert":"status");feedback.setAttribute("aria-live",result==="error"?"assertive":"polite");document.getElementById("credit-feedback-message").textContent=text;feedback.hidden=false;clearTimeout(feedbackTimeout);feedbackTimeout=setTimeout(()=>{feedback.hidden=true},8000)}
function cookie(name){const item=document.cookie.split("; ").find(value=>value.startsWith(name+"="));return item?decodeURIComponent(item.split("=").slice(1).join("=")):""}
async function api(path,options={}){const headers={"Content-Type":"application/json",...(options.headers||{})};if(options.method&&options.method!=="GET")headers["X-CSRF-Token"]=cookie("site_csrf");const response=await fetch(path,{...options,headers});const result=await response.json();if(!response.ok){const error=new Error(result.detail||"Request failed.");error.status=response.status;throw error}return result}
async function load(){try{const user=await api("/auth/me");document.getElementById("profile").textContent="Signed in as "+user.username;if(user.role!=="admin"){document.getElementById("wrong-account").hidden=false;return}if(user.must_change_password)document.getElementById("change-section").hidden=false;else{document.getElementById("credit-section").hidden=false;await loadGameRounds()}}catch(error){if(error.status===401){document.getElementById("no-session").hidden=false;return}message.textContent=error.message}}
let gameMarkets=[],gameRates=[];
async function loadGameRounds(){gameMarkets=await api("/api/markets");const rounds=document.getElementById("result-round"),marketsSelect=document.getElementById("market-edit-id"),ratesSelect=document.getElementById("rate-code");rounds.replaceChildren();marketsSelect.replaceChildren();for(const market of gameMarkets){const round=await api(`/api/markets/${market.id}/today`);const roundOption=document.createElement("option");roundOption.value=round.round_id;roundOption.textContent=`${market.name} · ${round.date}`;rounds.append(roundOption);const marketOption=document.createElement("option");marketOption.value=market.id;marketOption.textContent=market.name;marketsSelect.append(marketOption)}const newOption=document.createElement("option");newOption.value="new";newOption.textContent="Create a market";marketsSelect.append(newOption);const mode=await api("/api/result-mode");document.getElementById("game-result").hidden=mode.mode!=="admin";gameRates=await api("/api/bet-types?include_disabled=true");ratesSelect.replaceChildren();for(const rate of gameRates){const option=document.createElement("option");option.value=rate.code;option.textContent=rate.label;ratesSelect.append(option)}loadMarketFields();loadRateFields()}
function loadMarketFields(){const id=document.getElementById("market-edit-id").value,market=gameMarkets.find(item=>String(item.id)===id);document.getElementById("market-name").value=market?.name||"";document.getElementById("market-open").value=market?.open_time_24||"10:00";document.getElementById("market-close").value=market?.close_time_24||"23:00";document.getElementById("market-days").value=market?.active_days||"0,1,2,3,4,5,6";document.getElementById("market-cutoff").value=market?.bet_cutoff_minutes||10;document.getElementById("market-paused").value=String(Boolean(market?.paused));document.getElementById("market-sort").value=market?.sort_order||0}
function loadRateFields(){const rate=gameRates.find(item=>item.code===document.getElementById("rate-code").value);if(!rate)return;document.getElementById("rate-value").value=rate.win_per_10;document.getElementById("rate-min").value=rate.min_points;document.getElementById("rate-max").value=rate.max_points;document.getElementById("rate-enabled").value=String(rate.enabled!==false)}
document.getElementById("market-edit-id").addEventListener("change",loadMarketFields);document.getElementById("rate-code").addEventListener("change",loadRateFields);
document.getElementById("market-edit").addEventListener("submit",async event=>{event.preventDefault();const marketId=document.getElementById("market-edit-id").value;try{const days=document.getElementById("market-days").value.split(",").map(value=>Number(value.trim()));await api(marketId==="new"?"/api/admin/markets":`/api/admin/markets/${marketId}`,{method:marketId==="new"?"POST":"PUT",body:JSON.stringify({name:document.getElementById("market-name").value,open_time:document.getElementById("market-open").value,close_time:document.getElementById("market-close").value,active_days:days,bet_cutoff_minutes:Number(document.getElementById("market-cutoff").value),paused:document.getElementById("market-paused").value==="true",sort_order:Number(document.getElementById("market-sort").value)})});showCreditFeedback("Market schedule saved.","success");await loadGameRounds()}catch(error){showCreditFeedback(`Could not save market: ${error.message}`,"error")}});
document.getElementById("rate-edit").addEventListener("submit",async event=>{event.preventDefault();const code=document.getElementById("rate-code").value;try{await api(`/api/admin/bet-types/${code}`,{method:"PUT",body:JSON.stringify({win_per_10:Number(document.getElementById("rate-value").value),min_points:Number(document.getElementById("rate-min").value),max_points:Number(document.getElementById("rate-max").value),enabled:document.getElementById("rate-enabled").value==="true"})});showCreditFeedback("Win rate saved. New entries use the updated rate.","success");await loadGameRounds()}catch(error){showCreditFeedback(`Could not save win rate: ${error.message}`,"error")}});
document.getElementById("game-result").addEventListener("submit",async event=>{event.preventDefault();const button=event.currentTarget.querySelector("button");button.disabled=true;try{const result=await api(`/api/admin/rounds/${document.getElementById("result-round").value}/result`,{method:"POST",body:JSON.stringify({session:document.getElementById("result-session").value,panna:document.getElementById("result-panna").value})});showCreditFeedback(`Result declared. ${result.settled} entries settled.`,"success");event.currentTarget.reset();await loadGameRounds()}catch(error){showCreditFeedback(`Could not declare result: ${error.message}`,"error")}finally{button.disabled=false}});
async function logout(){try{await api("/auth/logout",{method:"POST"})}finally{location.assign("/login?next=%2Fadmin")}}
document.getElementById("logout").addEventListener("click",logout);document.getElementById("switch-account").addEventListener("click",logout);
document.getElementById("credit-feedback-close").addEventListener("click",()=>{clearTimeout(feedbackTimeout);document.getElementById("credit-feedback").hidden=true});
document.getElementById("change-password").addEventListener("submit",async event=>{event.preventDefault();const values=new FormData(event.currentTarget);try{const result=await api("/auth/change-password",{method:"POST",body:JSON.stringify({current_password:values.get("current_password"),new_password:values.get("new_password")})});message.textContent=result.message;location.reload()}catch(error){message.textContent=error.message}});
function wireCoinAdjustment(formId,endpoint,verb,buttonLabel,loadingLabel){document.getElementById(formId).addEventListener("submit",async event=>{event.preventDefault();const form=event.currentTarget,button=form.querySelector("button[type=submit],button:not([type])"),values=new FormData(form);button.disabled=true;button.textContent=loadingLabel;try{const result=await api(endpoint,{method:"POST",body:JSON.stringify({username:values.get("username"),phone:values.get("phone"),amount:Number(values.get("amount"))})}),amount=result.amount_added??result.amount_removed;showCreditFeedback(`Success: ${verb} ${amount} virtual coins ${verb==="added"?"to":"from"} ${result.username}. New balance: ${Number(result.coin_balance).toLocaleString()} coins.`,"success");form.reset()}catch(error){showCreditFeedback(`Transaction failed: ${error.message}`,"error")}finally{button.disabled=false;button.textContent=buttonLabel}})}
wireCoinAdjustment("credit","/admin/credits","added","Add virtual coins","Adding coins…");
wireCoinAdjustment("debit","/admin/debits","removed","Debit virtual coins","Debiting coins…");
load();
</script></body></html>"""
