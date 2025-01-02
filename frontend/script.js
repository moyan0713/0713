// API基础URL
const API_BASE_URL = 'http://localhost:5000/api';

// 获取DOM元素
const goodsList = document.querySelector('#goodsTable tbody');
const addForm = document.getElementById('addForm');
const orderData = document.getElementById('orderData');
const parseBtn = document.getElementById('parseBtn');

// 初始化事件监听
document.addEventListener('DOMContentLoaded', () => {
    // 加载货物列表
    loadGoods();

    // 解析数据按钮点击事件
    if (parseBtn) {
        parseBtn.addEventListener('click', async () => {
            try {
                const data = orderData.value.trim();
                if (!data) {
                    showError('请输入要解析的数据', 'pasteError');
                    return;
                }

                showLoading(parseBtn);
                const response = await fetch(`${API_BASE_URL}/parse`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ data })
                });

                const result = await response.json();
                if (response.ok) {
                    showMessage('解析成功');
                    await loadGoods(); // 重新加载货物列表
                    orderData.value = ''; // 清空输入框
                } else {
                    throw new Error(result.error || '解析失败');
                }
            } catch (error) {
                console.error('Error parsing data:', error);
                showError(error.message || '解析失败', 'pasteError');
            } finally {
                hideLoading(parseBtn);
            }
        });
    }

    // 添加新货物表单提交事件
    if (addForm) {
        addForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = addForm.querySelector('button[type="submit"]');
            
            try {
                showLoading(submitBtn);
                const formData = {
                    name: document.getElementById('name').value,
                    category: document.getElementById('category').value,
                    quantity: parseInt(document.getElementById('quantity').value),
                    unit_price: parseFloat(document.getElementById('unitPrice').value),
                    arrival_date: document.getElementById('arrivalDate').value
                };

                const response = await fetch(`${API_BASE_URL}/goods`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                const result = await response.json();
                if (response.ok) {
                    showMessage('添加成功');
                    addForm.reset();
                    await loadGoods();
                } else {
                    throw new Error(result.error || '添加失败');
                }
            } catch (error) {
                console.error('Error adding good:', error);
                showError(error.message || '添加失败', 'addError');
            } finally {
                hideLoading(submitBtn);
            }
        });
    }
});

// 加载所有货物
async function loadGoods() {
    try {
        const response = await fetch(`${API_BASE_URL}/goods`);
        if (!response.ok) {
            throw new Error('加载货物失败');
        }
        const goods = await response.json();
        displayGoods(goods);
    } catch (error) {
        console.error('Error loading goods:', error);
        showError('加载货物失败', 'tableError');
    }
}

// 显示货物列表
function displayGoods(goods) {
    if (!goodsList) return;
    
    goodsList.innerHTML = '';
    
    if (goods.length === 0) {
        goodsList.innerHTML = `
            <tr>
                <td colspan="7" class="empty-state">
                    <p>暂无货物数据</p>
                    <p>您可以添加新货物或导入Excel文件</p>
                </td>
            </tr>
        `;
        return;
    }

    goods.forEach(good => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${good.name}</td>
            <td>${good.category}</td>
            <td>${good.quantity}</td>
            <td>￥${good.unit_price.toFixed(2)}</td>
            <td>￥${(good.quantity * good.unit_price).toFixed(2)}</td>
            <td>${good.arrival_date || '待补充'}</td>
            <td>
                <button class="btn btn-danger btn-sm" onclick="deleteGood(${good.id})">删除</button>
            </td>
        `;
        goodsList.appendChild(row);
    });
}

// 删除货物
async function deleteGood(id) {
    if (!confirm('确定要删除这个货物吗？')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/goods/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showMessage('删除成功');
            await loadGoods();
        } else {
            throw new Error('删除失败');
        }
    } catch (error) {
        console.error('Error deleting good:', error);
        showError('删除失败', 'tableError');
    }
}

// 显示错误信息
function showError(message, elementId) {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
}

// 显示成功消息
function showMessage(message) {
    const messageContainer = document.getElementById('messageContainer');
    if (!messageContainer) return;

    const messageElement = document.createElement('div');
    messageElement.className = 'message success';
    messageElement.textContent = message;
    
    messageContainer.appendChild(messageElement);
    setTimeout(() => messageElement.remove(), 3000);
}

// 显示加载状态
function showLoading(element) {
    if (element) {
        element.disabled = true;
        element.classList.add('loading');
    }
}

// 隐藏加载状态
function hideLoading(element) {
    if (element) {
        element.disabled = false;
        element.classList.remove('loading');
    }
} 