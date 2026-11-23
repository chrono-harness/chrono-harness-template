const test = require('node:test')
const assert = require('node:assert/strict')
const sync = require('../.github/roadmap.cjs')

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
  items.push({number: 5, state: 'open'})
  const rolling = {kind: 'copier', version: '1.2.0', version_policy: 'next_patch'}
  await run(rolling)
  assert.equal(items.at(-1).milestone, milestones.find(m => m.title === 'v1.2.1').number)
  items.push({number: 6, state: 'open'})
  await run({...rolling, version: '2.0.0'})
  assert.equal(items.at(-1).milestone, milestones.find(m => m.title === 'v2.0.0').number)
  await assert.rejects(run({...rolling, kind: 'binary'}), /Copier/)
  await assert.rejects(run({version: 'not-a-version'}), /Expected version/)
})

test('a failed publication owns one issue and its successful retry closes it', async () => {
  const run = {id: 123, name: 'Release', run_number: 9, run_attempt: 1,
    html_url: 'https://github.com/a/b/actions/runs/123', status: 'completed', head_sha: 'abcdef', conclusion: 'failure'}
  const items = [{number: 1, state: 'open', user: {login: 'somebody'}, body: '<!-- chrono-harness release-run 123 -->'}]
  let hasLabel = false
  const rest = {
    actions: {getWorkflowRun: async ({run_id}) => {assert.equal(run_id, 123); return {data: run}}},
    issues: {
      listForRepo: () => items,
      getLabel: () => {if (!hasLabel) throw Object.assign(new Error('missing label'), {status: 404})},
      createLabel: () => {hasLabel = true},
      create: data => {items.push({...data, number: 2, state: 'open', user: {login: 'github-actions[bot]'}})},
      update: ({issue_number, ...fields}) => {Object.assign(items.find(i => i.number === issue_number), fields)},
    },
  }
  const notify = () => sync.releaseIssue({rest, paginate: async fn => [...fn()]},
    {repo: {owner: 'a', repo: 'b'}, payload: {workflow_run: {id: 123}}})
  await notify()
  await notify()
  assert.equal(items.length, 2)
  assert.equal(hasLabel, true)
  assert.match(items[1].body, /attempts\/1/)
  run.run_attempt = 2
  run.conclusion = 'success'
  await notify()
  await notify()
  assert.equal(items[1].state, 'closed')
  assert.match(items[1].body, /attempts\/2/)
  assert.equal(items[0].state, 'open')
})
