// NovaSocial AI - Modern Reactive Frontend Controller

let selectedInterval = 1.0;
let countdownTimer = null;
let currentRemainingSeconds = 0;
let studioGeneratedData = null;

// PWA Service Worker Registration
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/sw.js').catch(err => {
      console.log('SW registration notice:', err);
    });
  });
}

// Initial Boot
document.addEventListener('DOMContentLoaded', () => {
  initApp();
  // Poll live status & logs every 4 seconds for real-time auto-updates
  setInterval(refreshLiveStatus, 4000);
  setInterval(refreshLogs, 3000);
});

async function initApp() {
  await refreshLiveStatus();
  await loadTrends();
  await loadPosts();
  await refreshLogs();
  await loadSettings();
  await loadBackupStatus();
  // Trigger Automatic Laptop Backup upon opening the app
  triggerAutoBackupOnOpen();
}

async function triggerAutoBackupOnOpen() {
  try {
    const res = await fetch('/api/backup/auto-sync', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      showToast(`💾 Automatic Laptop Backup Completed! Synced to ${data.file}`, 'success');
      const backupStat = document.getElementById('stat-backup');
      if (backupStat) {
        backupStat.textContent = 'Synced Now';
        backupStat.className = 'text-xl sm:text-2xl font-bold font-heading text-emerald-400';
      }
      await loadBackupStatus();
    }
  } catch (err) {
    console.error('Auto backup error:', err);
  }
}

// Tab Switching
function switchTab(tabId) {
  // Hide all tab panes
  document.querySelectorAll('.tab-pane').forEach(el => el.classList.add('hidden'));
  
  // Show target pane
  const target = document.getElementById(`tab-content-${tabId}`);
  if (target) target.classList.remove('hidden');

  // Update button styles
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('bg-slate-800/80', 'text-cyan-400', 'border', 'border-cyan-500/30');
    btn.classList.add('text-slate-400');
  });

  const activeBtn = document.getElementById(`tab-btn-${tabId}`);
  if (activeBtn) {
    activeBtn.classList.remove('text-slate-400');
    activeBtn.classList.add('bg-slate-800/80', 'text-cyan-400', 'border', 'border-cyan-500/30');
  }

  // Refresh tab-specific data
  if (tabId === 'backup') loadBackupStatus();
  if (tabId === 'settings') loadSettings();
}

// Toast Notifications
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  
  const colors = {
    success: 'bg-emerald-950/90 border-emerald-500 text-emerald-200',
    error: 'bg-rose-950/90 border-rose-500 text-rose-200',
    info: 'bg-slate-900/95 border-cyan-500 text-cyan-200'
  };

  const icons = {
    success: 'fa-check-circle',
    error: 'fa-circle-exclamation',
    info: 'fa-bolt'
  };

  toast.className = `p-3.5 rounded-2xl border text-xs shadow-2xl backdrop-blur-md flex items-center gap-3 transition-all duration-300 transform translate-y-2 pointer-events-auto ${colors[type] || colors.info}`;
  toast.innerHTML = `
    <i class="fa-solid ${icons[type] || icons.info} text-base"></i>
    <span class="font-medium flex-1">${message}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => toast.classList.remove('translate-y-2'), 10);
  setTimeout(() => {
    toast.classList.add('opacity-0', '-translate-y-2');
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Live Status Refresh
async function refreshLiveStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();

    // 1. Facebook Connection
    const fbPill = document.getElementById('fb-status-pill');
    const fbText = document.getElementById('fb-status-text');
    const pageSelect = document.getElementById('active-page-select');
    if (data.facebook.connected) {
      fbText.textContent = data.facebook.page_name || 'Connected';
      fbText.className = 'text-emerald-400 font-medium';
      if (pageSelect && data.facebook.page_id) {
        pageSelect.value = data.facebook.page_id;
      }
    } else {
      fbText.textContent = 'Demo Mode (Add Token)';
      fbText.className = 'text-amber-400 font-medium';
    }

    // 2. Real Metrics
    if (data.insights) {
      const followers = data.insights.followers !== undefined ? data.insights.followers : 0;
      document.getElementById('stat-followers').textContent = Number(followers).toLocaleString();
      
      const reach = data.insights.weekly_reach !== undefined ? data.insights.weekly_reach : 0;
      document.getElementById('stat-reach').textContent = Number(reach).toLocaleString();
    }

    // 3. Scheduler & Countdown
    const scheduler = data.scheduler;
    const toggle = document.getElementById('autopilot-toggle');
    const dot = document.getElementById('autopilot-indicator-dot');
    const heading = document.getElementById('autopilot-status-heading');
    const stateText = document.getElementById('stat-autopilot-state');

    if (scheduler.running) {
      toggle.checked = true;
      dot.className = 'w-3.5 h-3.5 rounded-full bg-emerald-400 pulse-green';
      heading.textContent = `Auto-Pilot: Active (Every ${scheduler.interval_hours}h)`;
      heading.className = 'text-sm font-bold text-emerald-400';
      stateText.textContent = `Active (Every ${scheduler.interval_hours}h)`;
      stateText.className = 'text-[11px] text-emerald-400 mt-0.5 font-medium';

      if (scheduler.seconds_remaining !== null) {
        currentRemainingSeconds = scheduler.seconds_remaining;
        updateCountdownDisplay(currentRemainingSeconds);
      }
    } else {
      toggle.checked = false;
      dot.className = 'w-3.5 h-3.5 rounded-full bg-slate-600';
      heading.textContent = 'Auto-Pilot: Paused';
      heading.className = 'text-sm font-bold text-slate-200';
      stateText.textContent = 'Idle (Click to Activate)';
      stateText.className = 'text-[11px] text-amber-400 mt-0.5 font-medium';
      document.getElementById('stat-countdown').textContent = 'PAUSED';
    }

  } catch (err) {
    console.error('Status refresh error:', err);
  }
}

function updateCountdownDisplay(sec) {
  if (sec <= 0) {
    document.getElementById('stat-countdown').textContent = 'POSTING NOW';
    return;
  }
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = sec % 60;
  const pad = (n) => String(n).padStart(2, '0');
  document.getElementById('stat-countdown').textContent = `${pad(h)}:${pad(m)}:${pad(s)}`;
}

// Page Switching
async function switchActiveFacebookPage(pageId) {
  try {
    const res = await fetch('/api/pages/switch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ page_id: pageId })
    });
    const data = await res.json();
    if (data.success) {
      showToast(`Switched active page to: ${data.page_name}`, 'success');
      await refreshLiveStatus();
      if (!document.getElementById('tab-content-growth').classList.contains('hidden')) {
        runDeepProfileAudit();
      }
    }
  } catch (err) {
    showToast('Failed to switch page', 'error');
  }
}

// Auto-Pilot Controls
function selectInterval(hours) {
  selectedInterval = hours;
  document.querySelectorAll('.interval-chip').forEach(btn => {
    btn.className = 'interval-chip py-2 rounded-xl border border-slate-700 bg-slate-900/80 text-xs font-medium text-slate-300 hover:border-purple-500 transition';
  });

  const btnId = `btn-int-${String(hours).replace('.', '')}`;
  const activeBtn = document.getElementById(btnId);
  if (activeBtn) {
    activeBtn.className = 'interval-chip py-2 rounded-xl border border-purple-500 bg-purple-500/20 text-xs font-semibold text-purple-300 transition';
  }

  // If already running, update interval on backend
  const toggle = document.getElementById('autopilot-toggle');
  if (toggle.checked) {
    toggleAutoPilot(true);
  }
}

async function toggleAutoPilot(enabled) {
  try {
    const res = await fetch('/api/scheduler/toggle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled: enabled, interval_hours: selectedInterval })
    });
    const data = await res.json();
    showToast(enabled ? `Auto-Pilot activated! Posting every ${selectedInterval} hour(s)` : 'Auto-Pilot paused.', enabled ? 'success' : 'info');
    refreshLiveStatus();
  } catch (err) {
    showToast('Failed to toggle Auto-Pilot', 'error');
  }
}

async function triggerImmediatePipeline() {
  const btn = document.getElementById('btn-manual-trigger');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Triggering Pipeline...';
  }

  try {
    const res = await fetch('/api/trigger-pipeline', { method: 'POST' });
    const data = await res.json();
    showToast('🚀 Pipeline dispatched! Watching live progress...', 'success');
    refreshLogs();
  } catch (err) {
    showToast('Error dispatching pipeline', 'error');
  } finally {
    setTimeout(() => {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-play"></i> <span>Trigger AI Post Right Now</span>';
      }
    }, 2000);
  }
}

// Live Terminal Logs
async function refreshLogs() {
  try {
    const res = await fetch('/api/logs');
    const data = await res.json();
    const stream = document.getElementById('terminal-stream');
    if (!data.logs || data.logs.length === 0) return;

    stream.innerHTML = data.logs.map(log => {
      let badgeColor = 'text-slate-400';
      if (log.level === 'SUCCESS') badgeColor = 'text-emerald-400';
      if (log.level === 'WARNING') badgeColor = 'text-amber-400';
      if (log.level === 'ERROR') badgeColor = 'text-rose-400';
      if (log.level === 'INFO') badgeColor = 'text-cyan-400';

      return `<div class="leading-relaxed"><span class="text-slate-500">[${log.timestamp.split(' ')[1]}]</span> <span class="font-bold ${badgeColor}">[${log.event_type || 'SYS'}]</span> ${escapeHtml(log.message)}</div>`;
    }).join('');
  } catch (err) {
    // console.log(err);
  }
}

// Trends Radar
async function loadTrends() {
  try {
    const res = await fetch('/api/trends');
    const data = await res.json();
    
    // 1. Quick trends list on Dashboard
    const quickList = document.getElementById('quick-trends-list');
    if (quickList && data.trends) {
      quickList.innerHTML = data.trends.slice(0, 4).map(t => `
        <div class="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300 flex items-center justify-between hover:border-cyan-500/50 cursor-pointer transition" onclick="selectTrendAndOpenStudio('${escapeQuotes(t.title)}')">
          <span class="truncate flex-1 font-medium">${t.title}</span>
          <i class="fa-solid fa-arrow-right text-cyan-400 text-[10px] ml-2"></i>
        </div>
      `).join('');
    }

    // 2. Studio trends list
    const studioList = document.getElementById('studio-trends-list');
    if (studioList && data.trends) {
      studioList.innerHTML = data.trends.map((t, idx) => `
        <div class="p-3 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-cyan-500/60 cursor-pointer transition group" onclick="selectTrendAndOpenStudio('${escapeQuotes(t.title)}')">
          <div class="flex items-center justify-between text-[10px] text-slate-400 mb-1">
            <span class="text-cyan-400 font-semibold">#${idx + 1} Trending</span>
            <span>${t.source}</span>
          </div>
          <p class="text-xs font-bold text-slate-200 group-hover:text-cyan-300 transition line-clamp-2">${t.title}</p>
        </div>
      `).join('');
    }
  } catch (err) {
    console.error('Error loading trends:', err);
  }
}

function selectTrendAndOpenStudio(topic) {
  document.getElementById('custom-topic-input').value = topic;
  switchTab('studio');
  generateStudioPreview();
}

// Content Studio Preview & Publish
async function generateStudioPreview() {
  const topic = document.getElementById('custom-topic-input').value.trim();
  if (!topic) {
    showToast('Please enter or select a topic first!', 'info');
    return;
  }

  const btn = document.getElementById('btn-generate-preview');
  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating Post & Image...';

  const pillar = document.getElementById('pillar-select').value;
  const persona = document.getElementById('persona-select').value;

  try {
    const res = await fetch('/api/generate-preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic, pillar, persona })
    });
    const data = await res.json();
    studioGeneratedData = data;

    // Populate UI
    document.getElementById('preview-hook').value = data.ai_content.hook || '';
    document.getElementById('preview-content').value = data.ai_content.full_post || data.ai_content.body || '';

    // Image preview
    if (data.image && data.image.url) {
      const img = document.getElementById('preview-image');
      const placeholder = document.getElementById('image-placeholder');
      img.src = data.image.url + '?t=' + Date.now();
      img.classList.remove('hidden');
      placeholder.classList.add('hidden');
    }

    showToast('Masterpiece post & image ready for review!', 'success');
  } catch (err) {
    showToast('Failed to generate preview', 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-sparkles"></i> <span>Generate Viral Post & Image Preview</span>';
  }
}

async function publishStudioPost() {
  const content = document.getElementById('preview-content').value.trim();
  const hook = document.getElementById('preview-hook').value.trim();
  const topic = document.getElementById('custom-topic-input').value.trim() || 'Custom Post';

  if (!content) {
    showToast('Please generate or write some content first!', 'info');
    return;
  }

  const btn = document.getElementById('btn-studio-publish');
  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Publishing to Facebook...';

  const localImagePath = studioGeneratedData?.image?.local_path || null;
  const imageUrl = studioGeneratedData?.image?.url || null;

  try {
    const res = await fetch('/api/publish-now', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: topic,
        content: content,
        hook: hook,
        local_image_path: localImagePath,
        image_url: imageUrl
      })
    });
    const data = await res.json();

    if (data.success) {
      showToast('🎉 Published to Facebook successfully!', 'success');
      loadPosts();
      refreshLogs();
    } else {
      showToast(data.fb_response?.message || 'Publish completed in Demo Mode', 'info');
      loadPosts();
    }
  } catch (err) {
    showToast('Error publishing post', 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-brands fa-facebook"></i> <span>Publish to Facebook Page Now</span>';
  }
}

// Recent Posts Stream
async function loadPosts() {
  try {
    const res = await fetch('/api/posts');
    const data = await res.json();
    const container = document.getElementById('recent-posts-container');
    if (!data.posts || data.posts.length === 0) return;

    container.innerHTML = data.posts.slice(0, 6).map(post => `
      <div class="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 flex items-start gap-3 hover:border-slate-700 transition">
        ${post.image_url ? `<img src="${post.image_url}" class="w-16 h-16 rounded-xl object-cover border border-slate-800 flex-shrink-0">` : `
          <div class="w-16 h-16 rounded-xl bg-slate-800 flex items-center justify-center flex-shrink-0 text-slate-500"><i class="fa-solid fa-file-lines"></i></div>
        `}
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between text-[11px] text-slate-400 mb-1">
            <span class="text-cyan-400 font-semibold truncate">${post.topic}</span>
            <span class="text-slate-500 font-mono text-[10px]">${post.published_at || post.created_at}</span>
          </div>
          <p class="text-xs text-slate-300 font-medium line-clamp-2">${post.hook || post.content}</p>
          <div class="flex items-center gap-3 mt-1.5 text-[11px] text-slate-400">
            <span class="text-emerald-400 font-bold"><i class="fa-solid fa-check-double"></i> Published</span>
            <span><i class="fa-regular fa-thumbs-up"></i> ${post.likes_count || 0}</span>
            <span><i class="fa-regular fa-comment"></i> ${post.comments_count || 0}</span>
          </div>
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error('Error loading posts:', err);
  }
}

// Reels Lab
async function generateReelsScript() {
  const topic = document.getElementById('reels-topic-input').value.trim();
  if (!topic) {
    showToast('Please enter a Reels topic!', 'info');
    return;
  }

  const btn = document.getElementById('btn-reels-gen');
  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Writing Script...';

  try {
    const res = await fetch('/api/reels/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic })
    });
    const data = await res.json();
    const script = data.script;

    document.getElementById('reels-hook-text').textContent = script.hook;
    document.getElementById('reels-audio-text').textContent = script.audio_trend;
    document.getElementById('reels-visual-text').textContent = script.visual_directions;
    document.getElementById('reels-body-text').textContent = script.script_body;
    document.getElementById('reels-cta-text').textContent = script.cta;

    document.getElementById('reels-output').classList.remove('hidden');
    showToast('Viral Reels script created!', 'success');
  } catch (err) {
    showToast('Failed to create script', 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-video"></i> <span>Generate Script</span>';
  }
}

function copyReelsScript() {
  const hook = document.getElementById('reels-hook-text').textContent;
  const body = document.getElementById('reels-body-text').textContent;
  const cta = document.getElementById('reels-cta-text').textContent;
  navigator.clipboard.writeText(`${hook}\n\n${body}\n\n${cta}`);
  showToast('Reels script copied to clipboard!', 'success');
}

// Smart Comment Reply Simulator
async function generateSampleReply() {
  const comment = document.getElementById('sample-comment-input').value.trim();
  if (!comment) return;

  try {
    const res = await fetch('/api/comments/reply', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ comment, topic: 'Artificial Intelligence and Modern Social Media' })
    });
    const data = await res.json();
    document.getElementById('comment-reply-text').textContent = data.reply;
    document.getElementById('comment-reply-box').classList.remove('hidden');
    showToast('AI response formulated!', 'success');
  } catch (err) {
    showToast('Failed to reply', 'error');
  }
}

// Backup Status
async function loadBackupStatus() {
  try {
    const res = await fetch('/api/backup/status');
    const data = await res.json();
    document.getElementById('backup-dir-text').textContent = data.backup_dir;
    document.getElementById('backup-total-count').textContent = `${data.total_backups} (${data.total_size_mb} MB)`;

    const list = document.getElementById('backup-list-container');
    if (data.latest_backups && data.latest_backups.length > 0) {
      list.innerHTML = data.latest_backups.map(b => `
        <div class="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
          <div class="flex items-center gap-2">
            <i class="fa-regular fa-file-zipper text-cyan-400"></i>
            <span class="font-mono text-slate-300">${b.filename}</span>
          </div>
          <div class="flex items-center gap-3 text-slate-400 text-[11px]">
            <span>${b.size_mb} MB</span>
            <span>${b.created}</span>
          </div>
        </div>
      `).join('');
    } else {
      list.innerHTML = '<p class="text-xs text-slate-500">No backups generated yet. Click Download Backup above!</p>';
    }
  } catch (err) {
    console.error('Error loading backup status:', err);
  }
}

// Settings Modal Handlers
function openSettingsModal() {
  loadSettings();
  const modal = document.getElementById('settings-modal');
  if (modal) modal.classList.remove('hidden');
}

function closeSettingsModal() {
  const modal = document.getElementById('settings-modal');
  if (modal) modal.classList.add('hidden');
}

// Mobile QR Modal Handlers
function openMobileModal() {
  const modal = document.getElementById('mobile-modal');
  if (modal) modal.classList.remove('hidden');
}

function closeMobileModal() {
  const modal = document.getElementById('mobile-modal');
  if (modal) modal.classList.add('hidden');
}

// Settings
async function loadSettings() {
  try {
    const res = await fetch('/api/settings');
    const data = await res.json();
    if (data.gemini_api_key) document.getElementById('input-gemini-key').value = data.gemini_api_key;
    if (data.facebook_page_id) document.getElementById('input-fb-page-id').value = data.facebook_page_id;
    if (data.facebook_page_access_token) document.getElementById('input-fb-token').value = data.facebook_page_access_token;
    if (data.brand_name) document.getElementById('input-brand-name').value = data.brand_name;
    if (data.content_language) document.getElementById('input-content-lang').value = data.content_language;
  } catch (err) {
    console.error('Error loading settings:', err);
  }
}

async function saveSettings(e) {
  e.preventDefault();
  const payload = {
    gemini_api_key: document.getElementById('input-gemini-key').value.trim(),
    facebook_page_id: document.getElementById('input-fb-page-id').value.trim(),
    facebook_page_access_token: document.getElementById('input-fb-token').value.trim(),
    brand_name: document.getElementById('input-brand-name').value.trim(),
    content_language: document.getElementById('input-content-lang').value
  };

  try {
    const res = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    showToast('Settings saved successfully! Closing settings...', 'success');
    closeSettingsModal();
    refreshLiveStatus();
  } catch (err) {
    showToast('Failed to save settings', 'error');
  }
}

// Deep Profile Audit & Growth Doctor
async function runDeepProfileAudit() {
  const btn = document.getElementById('btn-run-audit');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing Profile Views & Engagement...';
  }

  try {
    const res = await fetch('/api/audit/run', { method: 'POST' });
    const data = await res.json();
    const m = data.metrics || {};
    const a = data.audit || {};

    // 1. Metrics Strip
    if (m.total_views) document.getElementById('audit-views').textContent = Number(m.total_views).toLocaleString();
    if (m.weekly_reach) document.getElementById('audit-reach').textContent = Number(m.weekly_reach).toLocaleString();
    if (m.avg_engagement_rate) document.getElementById('audit-eng-rate').textContent = m.avg_engagement_rate;
    const totalInteractions = (m.total_likes || 0) + (m.total_comments || 0) + (m.total_shares || 0);
    if (totalInteractions > 0) document.getElementById('audit-interactions').textContent = totalInteractions.toLocaleString();

    // 2. Health Score & Overview
    if (a.health_score) document.getElementById('audit-health-score').textContent = a.health_score;
    if (a.health_grade) document.getElementById('audit-health-grade').textContent = a.health_grade;
    if (a.executive_summary) document.getElementById('audit-summary-text').textContent = a.executive_summary;
    if (a.optimal_posting_times) document.getElementById('audit-peak-time').textContent = a.optimal_posting_times;

    // 3. Verdicts
    if (a.views_and_reach_verdict) document.getElementById('audit-views-verdict').textContent = a.views_and_reach_verdict;
    if (a.engagement_verdict) document.getElementById('audit-eng-verdict').textContent = a.engagement_verdict;

    // 4. Strengths & Weaknesses
    if (a.strengths && a.strengths.length > 0) {
      document.getElementById('audit-strengths-list').innerHTML = a.strengths.map(s => `
        <li class="flex items-start gap-2"><i class="fa-solid fa-check text-emerald-400 mt-0.5 text-[10px]"></i> <span>${escapeHtml(s)}</span></li>
      `).join('');
    }

    if (a.weaknesses && a.weaknesses.length > 0) {
      document.getElementById('audit-weaknesses-list').innerHTML = a.weaknesses.map(w => `
        <li class="flex items-start gap-2"><i class="fa-solid fa-arrow-right text-amber-400 mt-0.5 text-[10px]"></i> <span>${escapeHtml(w)}</span></li>
      `).join('');
    }

    // 5. Tactical Action Suggestions
    if (a.top_action_suggestions && a.top_action_suggestions.length > 0) {
      document.getElementById('audit-suggestions-list').innerHTML = a.top_action_suggestions.map((sug, i) => `
        <div class="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 flex items-start gap-3">
          <span class="w-6 h-6 rounded-lg bg-cyan-500/20 text-cyan-400 font-bold flex items-center justify-center flex-shrink-0 text-xs">${i + 1}</span>
          <p>${escapeHtml(sug)}</p>
        </div>
      `).join('');
    }

    // 6. Viral Reels Topics
    if (a.viral_reels_topics && a.viral_reels_topics.length > 0) {
      document.getElementById('audit-reels-topics').innerHTML = a.viral_reels_topics.map(topic => `
        <div class="p-3 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center justify-between gap-3 text-xs">
          <span class="text-slate-200 font-medium">${escapeHtml(topic)}</span>
          <button onclick="useTopicInReels('${escapeQuotes(topic)}')" class="px-3 py-1 rounded-lg bg-rose-500/20 text-rose-300 hover:bg-rose-500/30 text-[11px] font-semibold flex-shrink-0">Use in Reels Lab</button>
        </div>
      `).join('');
    }

    // 7. 7-Day Content Roadmap
    if (a.weekly_calendar && a.weekly_calendar.length > 0) {
      document.getElementById('audit-calendar-container').innerHTML = a.weekly_calendar.map(item => `
        <div class="p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800 flex flex-col justify-between">
          <div>
            <span class="text-[10px] font-bold text-cyan-400 uppercase tracking-wider block mb-1">${escapeHtml(item.day)} • ${escapeHtml(item.format)}</span>
            <p class="font-semibold text-slate-200 mb-1">${escapeHtml(item.topic)}</p>
            <p class="text-[11px] text-slate-400 italic">"${escapeHtml(item.hook)}"</p>
          </div>
          <button onclick="selectTrendAndOpenStudio('${escapeQuotes(item.topic)}')" class="mt-3 w-full py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 text-[11px] font-semibold">Create Post</button>
        </div>
      `).join('');
    }

    showToast(`🎉 Profile Audit Complete! Algorithm Score: ${a.health_score || 86}/100`, 'success');
  } catch (err) {
    showToast('Failed to complete Profile Audit', 'error');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> <span>Run Deep Profile & Engagement Audit</span>';
    }
  }
}

function useTopicInReels(topic) {
  // Strip emojis or extra hooks if wrapped in quotes
  let clean = topic.replace(/^[🔥🤯💡🚨\s'"]+/, '').replace(/['"]+$/, '');
  if (clean.includes('(')) clean = clean.split('(')[0].trim();
  
  document.getElementById('reels-topic-input').value = clean;
  switchTab('reels');
  generateReelsScript();
}

// Helpers
function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function escapeQuotes(str) {
  if (!str) return '';
  return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
}
