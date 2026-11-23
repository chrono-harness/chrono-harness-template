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
  const target = plan ? 'v' + plan.version : null
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
