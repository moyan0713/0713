// API基础URL
const API_BASE_URL = 'http://localhost:5000/api';

// 获取DOM元素
const goodsList = document.getElementById('goodsList');
const addGoodForm = document.getElementById('addGoodForm');
const totalAmountElement = document.getElementById('totalAmount');
const categoryFilter = document.getElementById('categoryFilter');
const searchInput = document.getElementById('searchInput');
const prevPageBtn = document.getElementById('prevPage');
const nextPageBtn = document.getElementById('nextPage');
const pageInfoElement = document.getElementById('pageInfo');
const clearAllBtn = document.getElementById('clearAllBtn');
const orderDataInput = document.getElementById('orderDataInput');
const parseDataBtn = document.getElementById('parseDataBtn');
const clearDataBtn = document.getElementById('clearDataBtn');
const parseResultContainer = document.getElementById('parseResultContainer');
const parseResultList = document.getElementById('parseResultList');
const parseCount = document.getElementById('parseCount');
const parseTotalAmount = document.getElementById('parseTotalAmount');
const exportDataBtn = document.getElementById('exportDataBtn');

// 分页和筛选状态
let currentPage = 1;
const itemsPerPage = 10;
let allGoods = [];
let filteredGoods = [];

// 文件处理相关
let selectedFile = null;

// 拖放处理
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

// 文件选择处理
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

// 处理文件选择
function handleFileSelect(file) {
    // 检查文件类型
    const allowedTypes = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel'
    ];
    
    if (!allowedTypes.includes(file.type)) {
        alert('请选择Excel文件（.xlsx或.xls）');
        return;
    }

    // 检查文件大小（5MB限制）
    if (file.size > 5 * 1024 * 1024) {
        alert('文件大小不能超过5MB');
        return;
    }

    selectedFile = file;
    fileName.textContent = file.name;
    fileInfo.style.display = 'flex';
}

// 上传按钮处理
uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) {
        return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch(`${API_BASE_URL}/import`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            alert(`导入成功：${result.count}条记录`);
            resetFileUpload();
            await loadGoods();
        } else {
            alert(`导入失败：${result.error}`);
        }
    } catch (error) {
        console.error('Error importing file:', error);
        alert('导入失败');
    }
});

// 取消按钮处理
cancelBtn.addEventListener('click', resetFileUpload);

// 重置文件上传状态
function resetFileUpload() {
    selectedFile = null;
    fileInput.value = '';
    fileInfo.style.display = 'none';
}

// 加载所有货物
async function loadGoods() {
    try {
        const response = await fetch(`${API_BASE_URL}/goods`);
        allGoods = await response.json();
        updateCategoryFilter();
        filterAndDisplayGoods();
    } catch (error) {
        console.error('Error loading goods:', error);
        alert('加载货物数据失败');
    }
}

// 更新分类筛选选项
function updateCategoryFilter() {
    const categories = [...new Set(allGoods.map(good => good.category))];
    categoryFilter.innerHTML = '<option value="">所有分类</option>';
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        categoryFilter.appendChild(option);
    });
}

// 筛选和显示货物
function filterAndDisplayGoods() {
    // 应用筛选
    const searchTerm = searchInput.value.toLowerCase();
    const selectedCategory = categoryFilter.value;

    filteredGoods = allGoods.filter(good => {
        const matchesSearch = good.name.toLowerCase().includes(searchTerm) ||
                            good.category.toLowerCase().includes(searchTerm);
        const matchesCategory = !selectedCategory || good.category === selectedCategory;
        return matchesSearch && matchesCategory;
    });

    // 更新分页信息
    const totalPages = Math.ceil(filteredGoods.length / itemsPerPage);
    currentPage = Math.min(currentPage, totalPages || 1);
    
    // 更新分页按钮状态
    prevPageBtn.disabled = currentPage === 1;
    nextPageBtn.disabled = currentPage === totalPages;
    
    // 更新页码显示
    pageInfoElement.textContent = `第 ${currentPage} 页 / 共 ${totalPages} 页`;

    // 获取当前页的数据
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const currentPageData = filteredGoods.slice(startIndex, endIndex);

    // 显示数据
    displayGoods(currentPageData);
}

// 显示货物列表
function displayGoods(goods) {
    goodsList.innerHTML = '';
    
    if (goods.length === 0) {
        goodsList.innerHTML = `
            <tr>
                <td colspan="6" class="empty-state">
                    <p>暂无货物数据</p>
                    <p>您可以添加新货物或导入Excel文件</p>
                </td>
            </tr>
        `;
        totalAmountElement.textContent = '￥0.00';
        return;
    }

    let totalAmount = 0;

    goods.forEach(good => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${good.name}</td>
            <td>${good.arrival_date || '待补充'}</td>
            <td>
                <span class="category-tag ${good.category}">${good.category}</span>
            </td>
            <td>￥${good.unit_price.toFixed(2)}</td>
            <td>${good.quantity}</td>
            <td>￥${good.amount.toFixed(2)}</td>
            <td>
                <button class="delete-btn" onclick="deleteGood(${good.id})">删除</button>
            </td>
        `;
        goodsList.appendChild(row);
        totalAmount += good.amount;
    });

    // 更新总金额（使用所有过滤后的商品，而不仅仅是当前页面的）
    const filteredTotal = filteredGoods.reduce((sum, good) => sum + good.amount, 0);
    totalAmountElement.textContent = `￥${filteredTotal.toFixed(2)}`;
}

// 添加新货物
addGoodForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = {
        name: document.getElementById('name').value,
        arrival_date: document.getElementById('arrival_date').value,
        category: document.getElementById('category').value,
        unit_price: parseFloat(document.getElementById('unit_price').value),
        quantity: parseInt(document.getElementById('quantity').value)
    };

    try {
        const response = await fetch(`${API_BASE_URL}/goods`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            addGoodForm.reset();
            await loadGoods();
            showSuccess('添加成功');
        } else {
            throw new Error('添加货物失败');
        }
    } catch (error) {
        console.error('Error adding good:', error);
        showError('添加货物失败');
    }
});

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
            await loadGoods();
            showSuccess('删除成功');
        } else {
            throw new Error('删除货物失败');
        }
    } catch (error) {
        console.error('Error deleting good:', error);
        showError('删除货物失败');
    }
}

// 分页事件处理
prevPageBtn.addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        filterAndDisplayGoods();
    }
});

nextPageBtn.addEventListener('click', () => {
    const totalPages = Math.ceil(filteredGoods.length / itemsPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        filterAndDisplayGoods();
    }
});

// 筛选事件处理
categoryFilter.addEventListener('change', () => {
    currentPage = 1;
    filterAndDisplayGoods();
});

searchInput.addEventListener('input', () => {
    currentPage = 1;
    filterAndDisplayGoods();
});

// 清除所有货物
async function clearAllGoods() {
    if (!confirm('确定要清除所有货物吗？此操作不可恢复！')) {
        return;
    }

    clearAllBtn.disabled = true;
    clearAllBtn.textContent = '正在清除...';

    try {
        const response = await fetch(`${API_BASE_URL}/clear-goods`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (response.ok) {
            await loadGoods();
            showSuccess(`成功清除了 ${result.count} 条记录`);
        } else {
            throw new Error(result.error || '清除失败');
        }
    } catch (error) {
        console.error('Error clearing goods:', error);
        showError('清除失败: ' + error.message);
    } finally {
        clearAllBtn.disabled = false;
        clearAllBtn.innerHTML = '<span class="btn-icon">🗑️</span>清除所有货物';
    }
}

// 添加清除按钮事件监听
clearAllBtn.addEventListener('click', clearAllGoods);

// 显示错误信息
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    const container = document.querySelector('.container');
    const existingError = container.querySelector('.error-message');
    if (existingError) {
        container.removeChild(existingError);
    }
    
    container.insertBefore(errorDiv, container.firstChild);
    setTimeout(() => errorDiv.classList.add('show'), 10);
    
    setTimeout(() => {
        errorDiv.classList.remove('show');
        setTimeout(() => container.removeChild(errorDiv), 300);
    }, 3000);
}

// 显示成功提示
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;
    
    const container = document.querySelector('.container');
    const existingSuccess = container.querySelector('.success-message');
    if (existingSuccess) {
        container.removeChild(existingSuccess);
    }
    
    container.insertBefore(successDiv, container.firstChild);
    setTimeout(() => successDiv.classList.add('show'), 10);
    
    setTimeout(() => {
        successDiv.classList.remove('show');
        setTimeout(() => container.removeChild(successDiv), 300);
    }, 3000);
}

// 页面加载时获取货物列表
document.addEventListener('DOMContentLoaded', loadGoods);

// 菜单切换功能
const menuItems = document.querySelectorAll('.menu-item');
const sections = document.querySelectorAll('.section-container');

// 初始化时设置第一个section为活动状态
document.addEventListener('DOMContentLoaded', () => {
    const firstSection = document.querySelector('.section-container');
    if (firstSection) {
        firstSection.classList.add('active');
    }
});

menuItems.forEach(item => {
    item.addEventListener('click', () => {
        // 移除所有菜单项的active类
        menuItems.forEach(i => i.classList.remove('active'));
        // 为当前点击的菜单项添加active类
        item.classList.add('active');

        // 获取目标section的id
        const targetId = item.getAttribute('data-target');
        
        // 处理section切换
        sections.forEach(section => {
            if (section.id === targetId) {
                section.classList.add('active');
            } else {
                section.classList.remove('active');
            }
        });
    });
}); 