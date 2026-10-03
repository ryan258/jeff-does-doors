const { test } = require('node:test');
const assert = require('node:assert/strict');
const drafts = require('../assets/js/draft-storage.js');
const now = 1000000000;
const memory = () => { const data = new Map(); return { getItem: key => data.get(key) ?? null, setItem: (key,value) => data.set(key,value), removeItem: key => data.delete(key) }; };
test('saved drafts round-trip by profile and expire without restoring', () => {
  const storage = memory();
  assert.equal(drafts.save(storage,'profile-a',{details:'Door track',projectType:''},now).saved,true);
  assert.equal(drafts.read(storage,'profile-b',now).record,null);
  assert.equal(drafts.read(storage,'profile-a',now).record.fields.details,'Door track');
  assert.equal(drafts.read(storage,'profile-a',now + drafts.MAX_AGE).record,null);
  assert.equal(storage.getItem('profile-a'),null);
});
test('malformed, future, oversized and unexpected fields never restore', () => {
  for (const raw of ['{', 'null', JSON.stringify({version:1,savedAt:now+1,fields:{}}), JSON.stringify({version:1,savedAt:now,fields:{password:'no'}}), JSON.stringify({version:1,savedAt:now,fields:{details:'x'.repeat(10001)}})]) assert.equal(drafts.decode(raw,now),null);
});
test('denied storage never reports a successful save or deletion', () => {
  const blocked = { getItem(){throw Error('blocked')},setItem(){throw Error('quota')},removeItem(){throw Error('blocked')} };
  assert.equal(drafts.read(blocked,'x').available,false);
  assert.equal(drafts.save(blocked,'x',{details:'Test'}).saved,false);
  assert.equal(drafts.remove(blocked,'x'),false);
});
test('a storage provider that silently drops writes cannot report success', () => {
  const dropping = { getItem(){return null;}, setItem(){}, removeItem(){} };
  assert.equal(drafts.save(dropping,'x',{details:'Test'}).saved,false);
});
