/**
 * OpenClaw Monitor - 主应用脚本
 */

// 配置
const CONFIG = {
    refreshInterval: 10 * 60 * 1000, // 10分钟刷新
    timeUpdateInterval: 1000 // 1秒更新时间
};

// 状态
let refreshTimer = null;
let timeTimer = null;
let currentTheme = localStorage.getItem('theme') || 'light';

// DOM 元素
const elements = {
    loadingOverlay: document.getElementById('loadingOverlay'),
    version: document.getElementById('version'),
    statusBadge: document.getElementById('statusBadge'),
    timeDisplay: document.getElementById('timeDisplay'),
    themeToggle: document.getElementById('themeToggle'),
    themeIcon: document.getElementById('themeIcon'),
    refreshBtn: document.getElementById('refreshBtn'),
    logoutBtn: document.getElementById('logoutBtn'),
    agentsGrid: document.getElementById('agentsGrid'),
    cpuMetric: document.getElementById('cpuMetric'),
    memMetric: document.getElementById('memMetric'),
    diskMetric: document.getElementById('diskMetric'),
    uptimeMetric: document.getElementById('uptimeMetric')
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    applyTheme(currentTheme);
    checkAuthAndLoad();
    startTimers();
    bindEvents();
});

function checkAuthAndLoad() {
    showLoading();
    
    fetch('/api/check-auth')
        .then(response => {
            if (!response.ok) {
                window.location.href = '/login';
                return null;
            }
            return fetch('/api/status');
        })
        .then(response => response?.json())
        .then(data => {
            if (data) {
                renderData(data);
            }
        })
        .catch(err => {
            console.error('加载数据失败:', err);
        })
        .finally(() => {
            hideLoading();
        });
}

function bindEvents() {
    // 主题切换
    elements.themeToggle.addEventListener('click', toggleTheme);
    
    // 刷新数据按钮
    elements.refreshBtn.addEventListener('click', refreshData);
    
    // 登出按钮
    elements.logoutBtn.addEventListener('click', handleLogout);
}

function startTimers() {
    // 时间更新
    updateTime();
    timeTimer = setInterval(updateTime, CONFIG.timeUpdateInterval);
    
    // 数据刷新
    refreshTimer = setInterval(refreshData, CONFIG.refreshInterval);
}

function updateTime() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('zh-CN', { hour12: false });
    const dateStr = now.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
    });
    
    elements.timeDisplay.querySelector('.time').textContent = timeStr;
    elements.timeDisplay.querySelector('.date').textContent = dateStr;
}

async function refreshData() {
    showLoading();
    
    try {
        const response = await fetch('/api/status');
        if (response.ok) {
            const data = await response.json();
            renderData(data);
        } else if (response.status === 401) {
            window.location.href = '/login';
        }
    } catch (e) {
        console.error('刷新数据失败:', e);
    } finally {
        hideLoading();
    }
}

function renderData(data) {
    // 版本
    elements.version.textContent = data.version || 'v?.?.?';
    
    // 状态
    const isRunning = data.status?.running;
    elements.statusBadge.classList.toggle('stopped', !isRunning);
    elements.statusBadge.querySelector('.status-text').textContent = isRunning ? '运行中' : '已停止';
    
    // 智能体
    renderAgents(data.agents || []);
    
    // 系统指标
    const metrics = data.metrics || {};
    elements.cpuMetric.textContent = metrics.cpu || '--%';
    elements.memMetric.textContent = metrics.memory || '-- MB';
    elements.diskMetric.textContent = metrics.disk || '--%';
    elements.uptimeMetric.textContent = metrics.uptime || '--';
}

function renderAgents(agents) {
    const STATUS_MAP = {
        'idle': { text: '● 空闲', class: 'status-idle' },
        'busy': { text: '● 忙碌', class: 'status-busy' },
        'error': { text: '● 异常', class: 'status-error' }
    };
    
    elements.agentsGrid.innerHTML = agents.map(agent => {
        const displayName = agent.alias || agent.name;
        const nameNote = agent.alias ? `<span class="name-note">(${agent.name})</span>` : '';
        const statusInfo = STATUS_MAP[agent.status] || STATUS_MAP['idle'];
        
        return `
        <div class="agent-card">
            <div class="agent-header">
                <div class="agent-name">
                    <span>🤖</span>
                    ${escapeHtml(displayName)} ${nameNote}
                </div>
                <span class="agent-status ${statusInfo.class}">
                    ${statusInfo.text}
                </span>
            </div>
            <div class="agent-meta">
                <span>🕐 最后活动: ${escapeHtml(agent.last_active || 'N/A')}</span>
            </div>
        </div>
    `}).join('');
    
    // 如果没有智能体
    if (agents.length === 0) {
        elements.agentsGrid.innerHTML = `
            <div class="agent-card">
                <div class="agent-header">
                    <div class="agent-name">📭 暂无智能体</div>
                </div>
                <div class="agent-meta">等待智能体启动...</div>
            </div>
        `;
    }
}

function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    applyTheme(currentTheme);
    localStorage.setItem('theme', currentTheme);
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    elements.themeIcon.textContent = theme === 'light' ? '🌙' : '☀️';
}

async function handleLogout() {
    if (!confirm('确定要退出登录吗？')) {
        return;
    }
    
    try {
        await fetch('/api/logout', { method: 'POST' });
    } catch (e) {
        console.error('登出失败:', e);
    }
    window.location.href = '/login';
}

function showLoading() {
    elements.loadingOverlay.classList.add('active');
}

function hideLoading() {
    elements.loadingOverlay.classList.remove('active');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}