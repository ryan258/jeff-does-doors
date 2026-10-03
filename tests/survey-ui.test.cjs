const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
let core;
test.before(async () => { core = await import('../assets/js/survey-core.mjs'); });
function setup(saved) {
  const element = (value = '') => ({value,hidden:false,disabled:true,checked:false,listeners:{},addEventListener(type, fn){this.listeners[type]=fn;},focus(){}});
  const fields = Object.fromEntries(Object.entries(core.emptyPacket()).map(([name,value]) => [name, {...element(value),name}]));
  const controls = Object.fromEntries(['status','save','restore','delete','import','prepare','json','text','copy','print','new'].map(name => [name, element()]));
  const result = element(), output = element();
  const form = {...element(),dataset:{profile:'jeff-does-doors',scope:'/'},elements:{namedItem:name=>fields[name]},querySelector:selector=>controls[selector.match(/data-survey-(.+)\]/)[1]],querySelectorAll:()=>Object.values(controls)};
  const map = new Map(), key = 'door-survey:v1:jeff-does-doors:/';
  if (saved) map.set(key,saved);
  const storage = {getItem:key=>map.get(key)||null,setItem:(key,value)=>map.set(key,value),removeItem:key=>map.delete(key)};
  const source = fs.readFileSync(path.join(__dirname,'../assets/js/survey.js'),'utf8').replace(/^import .*;\n/,'');
  const window = {localStorage:storage,confirm:()=>true,listeners:{},addEventListener(type,fn){this.listeners[type]=fn;}};
  vm.runInNewContext(source,{...core,window,document:{querySelector:selector=>selector==='[data-survey]'?form:selector==='[data-survey-result]'?result:output},setTimeout,URL,Blob,navigator:{}});
  const change = target => { target.listeners?.change?.({target,type:'change'}); form.listeners.change({target,type:'change'}); };
  return {fields,controls,form,result,output,map,key,storage,change,window};
}
test('survey values are not stored until opt in; deleting preserves current input', () => {
  const ui = setup(); ui.fields.job.value = 'Opening A'; ui.change(ui.fields.job);
  assert.equal(ui.map.size,0);
  ui.controls.save.checked=true; ui.change(ui.controls.save);
  assert.equal(core.decodePacket(ui.storage.getItem(ui.key)).job,'Opening A');
  ui.controls.delete.listeners.click();
  assert.equal(ui.map.size,0); assert.equal(ui.fields.job.value,'Opening A');
});
test('unit changes convert dimensions and weights independently', () => {
  const ui = setup(); ui.fields.widthTop.value='36 1/2'; ui.fields.weight.value='100';
  ui.fields.units.value='mm'; ui.change(ui.fields.units);
  assert.equal(Number(ui.fields.widthTop.value),927.1); assert.equal(ui.fields.weight.value,'100');
  ui.fields.weightUnit.value='kg'; ui.change(ui.fields.weightUnit);
  assert.equal(Number(ui.fields.weight.value),45.359237);
});
test('expired packet is removed and saving cannot silently replace an offered packet', () => {
  const expired=setup(core.encodePacket({...core.emptyPacket(),job:'Old'},Date.now()-core.MAX_AGE));
  assert.equal(expired.map.size,0); assert(expired.controls.restore.hidden);
  const ui=setup(core.encodePacket({...core.emptyPacket(),job:'Keep'}));
  ui.window.confirm=()=>false; ui.controls.save.checked=true; ui.change(ui.controls.save);
  assert.equal(core.decodePacket(ui.storage.getItem(ui.key)).job,'Keep'); assert(!ui.controls.save.checked);
});
test('import does not overwrite edits made while a file is loading', async () => {
  const ui = setup(); let finish;
  ui.controls.import.files=[{size:100,text:()=>new Promise(resolve=>{finish=resolve;})}];
  const pending=ui.controls.import.listeners.change({target:ui.controls.import});
  ui.fields.job.value='Newer work';ui.change(ui.fields.job);
  finish(core.encodePacket({...core.emptyPacket(),job:'File copy'}));await pending;
  assert.equal(ui.fields.job.value,'Newer work'); assert.match(ui.controls.status.textContent,/Fields changed/);
});
test('browser print refreshes the current packet and never prints stale validated output', () => {
  const ui=setup(); ui.fields.job.value='Latest job'; ui.window.listeners.beforeprint();
  assert.match(ui.output.textContent,/Latest job/);
  ui.fields.widthTop.value='wrong'; ui.window.listeners.beforeprint();
  assert.match(ui.output.textContent,/cannot be prepared/);
  assert.doesNotMatch(ui.output.textContent,/Latest job/);
});
