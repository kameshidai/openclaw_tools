/**
 * OpenClaw Monitor - 登录页面脚本
 */

// DOM 元素
const loginForm = document.getElementById('loginForm');
const errorMsg = document.getElementById('errorMsg');

// 检查是否已登录
checkAuth();

async function checkAuth() {
    try {
        const response = await fetch('/api/check-auth');
        if (response.ok) {
            window.location.href = '/';
        }
    } catch (e) {
        // 未登录，继续显示登录页
    }
}

// 登录表单提交
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();
    
    errorMsg.style.display = 'none';
    errorMsg.textContent = '';
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            window.location.href = '/';
        } else {
            showError(data.message || '登录失败');
        }
    } catch (e) {
        showError('网络错误，请重试');
    }
});

function showError(msg) {
    errorMsg.textContent = msg;
    errorMsg.style.display = 'block';
}