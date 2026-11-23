const test = require('node:test')
const assert = require('node:assert/strict')
const sync = require('./.github/roadmap.cjs')

test('new work, release publication, closing and reopening reconcile against current GitHub state', async () => {
  const items = [{number: 1, state: 'open'}, {number: 2, state: 'open', pull_request: {}}]
  const milestones = []
  const releases = []
  const writes = []
  const issues = {
    listMilestones: () => milestones,
    listForRepo: () => items.filter(i => !i.milestone && i.state === 'open'),
    createMilestone: ({title}) => {
      const data = {number: milestones.length + 1, title, state: 'open', description: ''}
      writes.push(['create', title])
      milestones.push(data)
      return {data}
    },
    getMilestone: ({milestone_number}) => {
      const row = milestones.find(m => m.number === milestone_number)
      return {data: {...row, open_issues: items.filter(i => i.milestone === row.number && i.state === 'open').length}}
    },
    update: ({issue_number, milestone}) => {
      writes.push(['assign', issue_number])
      items.find(i => i.number === issue_number).milestone = milestone
    },
    updateMilestone: ({milestone_number, description, state}) => {
      Object.assign(milestones.find(m => m.number === milestone_number), {state, description})
      writes.push(['update', milestone_number])
    },
  }
  const github = {rest: {issues, repos: {listReleases: () => releases}}, paginate: async (fn, args) => [...fn(args)]}
  const run = (plan = {version: '1.2.0'}) => sync(github, {repo: {owner: 'a', repo: 'b'}, payload: {}}, plan)
  await run(null)
  assert.equal(milestones[0].title, 'Backlog')
  assert.equal(items[0].milestone, 1)
  assert.equal(items[1].milestone, undefined)
  items.push({number: 3, state: 'open'})
  await run()
  const target = milestones.find(m => m.title === 'v1.2.0')
  target.description = '保留宿主计划。'
  assert.equal(items[2].milestone, target.number)
  assert.equal(items[0].milestone, 1)
  releases.push({tag_name: 'v1.2.0-alpha.1', published_at: '2025-01-01', prerelease: true, html_url: 'https://example.org/preview'})
  releases.push({tag_name: 'v1.2.0', draft: true})
  await run()
  assert.match(target.description, /保留宿主计划。/)
  assert.match(target.description, /v1\.2\.0-alpha\.1/)
  assert.doesNotMatch(target.description, /正式版/)
  releases.push({tag_name: 'v1.2.0', published_at: '2025-02-01', prerelease: false, html_url: 'https://example.org/stable'})
  items.push({number: 4, state: 'open'})
  await run()
  assert.equal(items[3].milestone, 1)
  assert.equal(target.state, 'open')
  assert.match(target.description, /正式版/)
  items[2].state = 'closed'
  await run()
  assert.equal(target.state, 'closed')
  writes.length = 0
  await run()
  assert.deepEqual(writes, [])
  items[2].state = 'open'
  await run()
  assert.equal(target.state, 'open')
  await assert.rejects(run({version: 'not-a-version'}), /Expected version/)
})
