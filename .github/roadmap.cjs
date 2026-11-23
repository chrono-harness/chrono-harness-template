const coreVersion = /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/

module.exports = async function syncRoadmap(github, context, plan) {
  if (plan !== null && (typeof plan.version !== 'string' || !coreVersion.test(plan.version))) {
    throw new Error('Expected version X.Y.Z in .chrono-harness/release.json')
  }
  const repo = context.repo
  const issues = github.rest.issues
  const all = (method, parameters) => github.paginate(method, {...repo, per_page: 100, ...parameters})
  const releases = await all(github.rest.repos.listReleases, {})
  const published = releases.filter(r => !r.draft && r.published_at)
  const stable = new Map(published.filter(r => !r.prerelease).map(r => [r.tag_name, r]))
  const milestones = await all(issues.listMilestones, {state: 'all'})

  async function ensure(title) {
    const existing = milestones.find(m => m.title === title)
    if (existing) return existing
    const {data} = await issues.createMilestone({...repo, title})
    milestones.push(data)
    return data
  }
  let target = plan ? 'v' + plan.version : null
  if (plan?.version_policy === 'next_patch') {
    if (plan.kind !== 'copier') throw new Error('next_patch requires a Copier source product')
    const compare = (a, b) => {
      for (let index = 0; index < 3; index++) {
        if (a[index] !== b[index]) return a[index] > b[index] ? 1 : -1
      }
      return 0
    }
    const versions = [...stable.keys()].filter(tag => tag.startsWith('v') && coreVersion.test(tag.slice(1)))
      .map(tag => tag.slice(1).split('.').map(BigInt)).sort(compare)
    const latest = versions.at(-1)
    if (latest && compare(latest, plan.version.split('.').map(BigInt)) >= 0) {
      target = 'v' + [latest[0], latest[1], latest[2] + 1n].join('.')
    }
  }
  const next = target && !stable.has(target) ? target : 'Backlog'
  const unassigned = await all(issues.listForRepo, {state: 'open', milestone: 'none'})
  for (const issue of unassigned) {
    if (issue.pull_request || issue.state !== 'open' || issue.milestone) continue
    const milestone = await ensure(next)
    await issues.update({...repo, issue_number: issue.number, milestone: milestone.number})
  }
  // Publishers using GITHUB_TOKEN wake this workflow via workflow_run.
  // Use the newest public release even when this host has no version plan.
  const newest = published.slice().sort((a, b) => b.published_at.localeCompare(a.published_at))[0]
  const tag = context.payload.release?.tag_name || newest?.tag_name
  const releasedVersion = tag?.split('-')[0]
  if (target) await ensure(target)
  if (releasedVersion?.startsWith('v') && coreVersion.test(releasedVersion.slice(1))) {
    await ensure(releasedVersion)
  }

  for (const known of milestones) {
    if (!known.title.startsWith('v') || !coreVersion.test(known.title.slice(1))) continue
    const final = stable.get(known.title)
    const preview = published.filter(r => r.prerelease && r.tag_name.startsWith(known.title + '-'))
      .sort((a,b) => b.published_at.localeCompare(a.published_at))[0]
    if (!final && !preview) continue
    const {data: milestone} = await issues.getMilestone({...repo, milestone_number: known.number})
    const begin = '<!-- chrono-harness release -->'
    const end = '<!-- /chrono-harness release -->'
    const lines = [begin]
    if (preview) lines.push(`测试版 [${preview.tag_name}](${preview.html_url})`)
    if (final) lines.push(`正式版 [${final.tag_name}](${final.html_url})`)
    lines.push(end)
    const block = lines.join('\n')
    const original = milestone.description || ''
    const start = original.indexOf(begin)
    const stop = original.indexOf(end)
    if ((start < 0) !== (stop < 0) || (start >= 0 && stop < start)) {
      throw new Error('Incomplete release block in milestone ' + milestone.number)
    }
    const description = start >= 0
      ? original.slice(0, start) + block + original.slice(stop + end.length)
      : [original, block].filter(Boolean).join('\n\n')
    const state = final && milestone.open_issues === 0 ? 'closed' : 'open'
    if (description !== original || state !== milestone.state) {
      await issues.updateMilestone({...repo, milestone_number: known.number, description, state})
    }
  }
}

// A workflow_run identifies the original release run across retry attempts.
module.exports.releaseIssue = async function releaseIssue(github, context) {
  const repo = context.repo
  const runId = context.payload.workflow_run.id
  const {data: run} = await github.rest.actions.getWorkflowRun({...repo, run_id: runId})
  if (run.status !== 'completed' || !['failure', 'timed_out', 'success'].includes(run.conclusion)) return
  const issues = github.rest.issues
  const label = 'release-failure'
  const marker = `<!-- chrono-harness release-run ${runId} -->`
  const history = await github.paginate(issues.listForRepo, {...repo, labels: label, state: 'all', per_page: 100})
  const item = history.find(i => !i.pull_request && i.user?.login === 'github-actions[bot]' && i.body?.startsWith(marker))
  if (run.conclusion === 'success') {
    if (item?.state === 'open') {
      const recovery = `同次运行已恢复。[成功的第 ${run.run_attempt} 次尝试](${run.html_url}/attempts/${run.run_attempt})`
      const body = item.body.includes(recovery) ? item.body : item.body + '\n\n' + recovery
      await issues.update({...repo, issue_number: item.number, state: 'closed', body})
    }
    return
  }
  if (item) {
    if (item.state === 'closed' && item.state_reason !== 'not_planned') {
      await issues.update({...repo, issue_number: item.number, state: 'open'})
    }
    return
  }
  try {
    await issues.getLabel({...repo, name: label})
  } catch (error) {
    if (error.status !== 404) throw error
    try {
      await issues.createLabel({...repo, name: label, color: 'b60205', description: 'Failed product release run'})
    } catch (conflict) {
      if (conflict.status !== 422) throw conflict
      await issues.getLabel({...repo, name: label})
    }
  }
  await issues.create({...repo, labels: [label], title: `发行失败 · ${run.name} #${run.run_number}`,
    body: `${marker}\n\n工作流在第 ${run.run_attempt} 次尝试返回 \`${run.conclusion}\`。提交为 \`${run.head_sha}\`。同一次运行重试成功会关闭本事项。通过后续版本修复时，从修复事项或 PR 引用此处并保留原始运行。\n\n[查看发布作业](${run.html_url}/attempts/${run.run_attempt})`})
}
