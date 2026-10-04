const { test } = require('node:test');
const assert = require('node:assert/strict');
const { validIndex, scoreEntry } = require('../assets/js/brief-core.js');
const entry = {title:'Door tracks',url:'/subpath/services/tracks-hardware/',summary:'Hardware work',text:'Site details',section:'services'};
test('reject malformed or unsafe search entries without rendering them', () => {
  assert.ok(validIndex([entry]));
  for (const data of [null,{},[null],[{}],[{...entry,title:7}],[{...entry,url:'javascript:alert(1)'}],[{...entry,url:'//other-host/'}]]) assert.equal(Boolean(validIndex(data)),false);
});
test('rank title matches ahead of body matches', () => {
  const query = 'tracks';
  const titleScore = scoreEntry(entry, query);
  const bodyScore = scoreEntry({...entry, title:'Other', text:query}, query);
  assert.ok(titleScore > 0, 'The fixture must contain the query in its title');
  assert.ok(bodyScore > 0, 'The comparison must contain the query in its body');
  assert.ok(titleScore > bodyScore, 'Title matches must rank ahead of body matches');
});
