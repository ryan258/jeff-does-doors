const { test } = require('node:test');
const assert = require('node:assert/strict');
const { validIndex, scoreEntry } = require('../assets/js/brief-core.js');
const entry = {title:'Water lines',url:'/subpath/services/water-lines/',summary:'Utility work',text:'Site details',section:'services'};
test('reject malformed or unsafe search entries without rendering them', () => {
  assert.ok(validIndex([entry]));
  for (const data of [null,{},[null],[{}],[{...entry,title:7}],[{...entry,url:'javascript:alert(1)'}],[{...entry,url:'//other-host/'}]]) assert.equal(Boolean(validIndex(data)),false);
});
test('rank title matches ahead of body matches', () => {
  assert.ok(scoreEntry(entry,'water') > scoreEntry({...entry,title:'Other',text:'water'},'water'));
});
