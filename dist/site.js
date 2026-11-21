(function(){
  // menu mobile
  var btn=document.querySelector('.menu-btn'),nav=document.getElementById('nav');
  if(btn){btn.addEventListener('click',function(){var o=nav.classList.toggle('open');btn.setAttribute('aria-expanded',o);document.body.style.overflow=o?'hidden':'';});}
  // borda do header ao rolar
  var hdr=document.querySelector('.hdr');
  addEventListener('scroll',function(){hdr.classList.toggle('scrolled',scrollY>40)},{passive:true});
  // barra de promoções
  var P=window.PROMOS||[],i=0,el=document.getElementById('promo');
  if(el&&P.length>1&&!matchMedia('(prefers-reduced-motion: reduce)').matches){
    setInterval(function(){i=(i+1)%P.length;el.style.opacity=0;setTimeout(function(){el.innerHTML='';el.append(P[i].text+' ');var a=document.createElement('a');a.href=P[i].link;a.textContent=P[i].cta;el.append(a);el.style.opacity=1},300)},5000);
  }
  // setas dos trilhos
  document.querySelectorAll('[data-rail]').forEach(function(b){b.addEventListener('click',function(){var r=document.getElementById(b.dataset.rail);r.scrollBy({left:r.clientWidth*0.8*b.dataset.dir,behavior:'smooth'})})});
  // copiar cupom / e-mail
  document.querySelectorAll('[data-code]').forEach(function(b){b.addEventListener('click',function(){
    var t=b.dataset.code,old=b.textContent;
    var done=function(){b.textContent='Copiado';setTimeout(function(){b.textContent=old},1600)};
    if(navigator.clipboard){navigator.clipboard.writeText(t).then(done,function(){prompt('Copie:',t)})}else{prompt('Copie:',t)}
  })});
  // esconder promoções vencidas (fim do dia, horário de Brasília)
  var now=new Date();
  document.querySelectorAll('[data-until]').forEach(function(n){var u=new Date(n.dataset.until+'T23:59:59-03:00');if(now>u)n.hidden=true});
})();
