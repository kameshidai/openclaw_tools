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
    restartBtn: document.getElementById('restartBtn'),
    logoutBtn: document.getElementById('logoutBtn'),
    agentsGrid: document.getElementById('agentsGrid'),
    cpuMetric: document.getElementById('cpuMetric'),
    memMetric: document.getElementById('memMetric'),
    diskMetric: document.getElementById('diskMetric'),
    uptimeMetric: document.getElementById('uptimeMetric'),
    // Modal elements
    restartModal: document.getElementById('restartModal'),
    confirmInput: document.getElementById('confirmInput'),
    cancelRestart: document.getElementById('cancelRestart'),
    confirmRestart: document.getElementById('confirmRestart')
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
    
    // 重启按钮 - 显示确认对话框
    elements.restartBtn.addEventListener('click', () => {
        showRestartModal();
    });
    
    // 取消重启
    elements.cancelRestart.addEventListener('click', hideRestartModal);
    
    // 确认输入框 - 实时验证
    elements.confirmInput.addEventListener('input', (e) => {
        const value = e.target.value.trim().toLowerCase();
        elements.confirmRestart.disabled = value !== 'checkok';
    });
    
    // 确认重启
    elements.confirmRestart.addEventListener('click', executeRestart);
    
    // 点击遮罩关闭
    elements.restartModal.addEventListener('click', (e) => {
        if (e.target === elements.restartModal) {
            hideRestartModal();
        }
    });
    
    // 回车确认
    elements.confirmInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && elements.confirmInput.value.trim().toLowerCase() === 'checkok') {
            executeRestart();
        }
    });
    
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
    elements.agentsGrid.innerHTML = agents.map(agent => {
        const displayName = agent.alias || agent.name;
        const nameNote = agent.alias ? `<span class="name-note">(${agent.name})</span>` : '';
        return `
        <div class="agent-card">
            <div class="agent-header">
                <div class="agent-name">
                    <span>🤖</span>
                    ${escapeHtml(displayName)} ${nameNote}
                </div>
                <span class="agent-status ${agent.status}">
                    ${agent.status === 'running' ? '● 运行中' : '○ 已停止'}
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

function showRestartModal() {
    elements.restartModal.style.display = 'flex';
    elements.confirmInput.value = '';
    elements.confirmRestart.disabled = true;
    elements.confirmInput.focus();
}

function hideRestartModal() {
    elements.restartModal.style.display = 'none';
    elements.confirmInput.value = '';
    elements.confirmRestart.disabled = true;
}

async function executeRestart() {
    const confirmValue = elements.confirmInput.value.trim().toLowerCase();
    if (confirmValue !== 'checkok') {
        alert('请输入正确的确认文字');
        return;
    }
    
    hideRestartModal();
    showLoading();
    
    try {
        const response = await fetch('/api/restart', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            alert('✅ OpenClaw 正在重启，页面将在 5 秒后刷新...');
            setTimeout(() => location.reload(), 5000);
        } else {
            alert('❌ 重启失败: ' + (data.error || '未知错误'));
        }
    } catch (e) {
        alert('❌ 请求失败，请重试');
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