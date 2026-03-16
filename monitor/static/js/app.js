/**
 * OpenClaw Monitor - 主应用脚本
 */

// 配置
const CONFIG = {
    refreshInterval: 2 * 60 * 1000, // 2分钟刷新
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
    restartBtn: document.getElementById('restartBtn'),
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
    
    // 重启按钮
    elements.restartBtn.addEventListener('click', handleRestart);
    
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
    elements.agentsGrid.innerHTML = agents.map(agent => `
        <div class="agent-card">
            <div class="agent-header">
                <div class="agent-name">
                    <span>🤖</span>
                    ${escapeHtml(agent.name)}
                </div>
                <span class="agent-status ${agent.status}">
                    ${agent.status === 'running' ? '● 运行中' : '○ 已停止'}
                </span>
            </div>
            <div class="agent-meta">
                <span>🕐 最后活动: ${escapeHtml(agent.last_active || 'N/A')}</span>
            </div>
        </div>
    `).join('');
    
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

async function handleRestart() {
    if (!confirm('确定要重启 OpenClaw 吗？')) {
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/restart', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            alert('OpenClaw 正在重启...');
            // 3秒后刷新页面
            setTimeout(() => location.reload(), 3000);
        } else {
            alert('重启失败: ' + (data.error || '未知错误'));
        }
    } catch (e) {
        alert('请求失败，请重试');
    } finally {
        hideLoading();
    }
}

async function handleLogout() {
    if (!confirm('确定要退出登录吗？')) {
        return;
    }
    
    try {
        await fetch('/api/logout', { method: 'POST' });
        window.location.href = '/login';
    } catch (e) {
        window.location.href = '/login';
    }
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