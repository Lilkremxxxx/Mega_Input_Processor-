// Global variables
const API_BASE_URL = 'http://localhost:8000';

// ShortInfo elements
let shortinfoFiles = [];
const shortinfoUploadArea = document.getElementById('shortinfoUploadArea');
const shortinfoFileInput = document.getElementById('shortinfoFileInput');
const shortinfoBrowseBtn = document.getElementById('shortinfoBrowseBtn');
const shortinfoFilesContainer = document.getElementById('shortinfoFilesContainer');
const shortinfoUploadBtn = document.getElementById('shortinfoUploadBtn');
const shortinfoClearBtn = document.getElementById('shortinfoClearBtn');

// RichInfo elements
let richinfoFiles = [];
const richinfoUploadArea = document.getElementById('richinfoUploadArea');
const richinfoFileInput = document.getElementById('richinfoFileInput');
const richinfoBrowseBtn = document.getElementById('richinfoBrowseBtn');
const richinfoFilesContainer = document.getElementById('richinfoFilesContainer');
const richinfoUploadBtn = document.getElementById('richinfoUploadBtn');
const richinfoClearBtn = document.getElementById('richinfoClearBtn');

// Common elements
const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const resultSection = document.getElementById('resultSection');

document.addEventListener('DOMContentLoaded', function() {
    // Tạo database button
    const createDatabaseBtn = document.getElementById('createDatabaseBtn');
    const deleteDatabaseBtn = document.getElementById('deleteDatabaseBtn');
    let username = localStorage.getItem('currentUser');
    let groupId = '';
    
    function updateDbButtons() {
        username = localStorage.getItem('currentUser');
        // Lấy groupId mới nhất từ localStorage
        let latest_groupId = localStorage.getItem('groupId_' + username) || '';
        groupId = latest_groupId;
        localStorage.setItem('groupId', groupId);
        
        if (groupId) {
            createDatabaseBtn.disabled = true;
            createDatabaseBtn.innerHTML = `<i class="fas fa-check"></i> Đã tạo xong: ${groupId}`;
            
            // Hiển thị nút xóa
            deleteDatabaseBtn.style.display = '';
            deleteDatabaseBtn.disabled = false;
            deleteDatabaseBtn.innerHTML = '<i class="fas fa-trash"></i> Xóa Database';
        } else {
            createDatabaseBtn.disabled = false;
            createDatabaseBtn.innerHTML = '<i class="fas fa-database"></i> Tạo Database';
            deleteDatabaseBtn.style.display = 'none';
            deleteDatabaseBtn.disabled = true;
        }
    }
    if (createDatabaseBtn && deleteDatabaseBtn) {
        // Thiết lập nút ban đầu
        function setupInitialButtons() {
            username = localStorage.getItem('currentUser');
            let latest_groupId = localStorage.getItem('groupId_' + username) || '';
            groupId = latest_groupId;
            localStorage.setItem('groupId', groupId);
            
            if (groupId) {
                createDatabaseBtn.disabled = true;
                createDatabaseBtn.innerHTML = `<i class="fas fa-check"></i> Đã tạo database: ${groupId}`;
                
                // Hiển thị và kích hoạt nút xóa
                deleteDatabaseBtn.style.display = '';
                deleteDatabaseBtn.disabled = false;
                deleteDatabaseBtn.innerHTML = '<i class="fas fa-trash"></i> Xóa Database';
            } else {
                createDatabaseBtn.disabled = false;
                createDatabaseBtn.innerHTML = '<i class="fas fa-database"></i> Tạo Database';
                deleteDatabaseBtn.style.display = 'none';
                deleteDatabaseBtn.disabled = true;
            }
        }
        
        // Thiết lập ban đầu
        setupInitialButtons();
        
        // Event handler cho nút tạo database
        createDatabaseBtn.onclick = async function() {
            username = localStorage.getItem('currentUser');
            if (!username) {
                alert('Bạn cần đăng nhập trước!');
                return;
            }
            
            // Cập nhật nút tạo database
            createDatabaseBtn.disabled = true;
            createDatabaseBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang tạo database...';
            
            try {
                const res = await fetch(API_BASE_URL + '/create_database', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username })
                });
                const data = await res.json();
                
                if (res.ok && data.success) {
                    // Sau khi tạo, gọi lại API /signin để lấy trạng thái database mới nhất
                    const res2 = await fetch(API_BASE_URL + '/signin', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, password: document.getElementById('password').value })
                    });
                    const data2 = await res2.json();
                    
                    if (res2.ok && data2.success) {
                        localStorage.setItem('groupId_' + username, data2.database || '');
                        localStorage.setItem('groupId', data2.database || '');
                        
                        // Đổi trạng thái nút tạo database
                        createDatabaseBtn.disabled = true;
                        createDatabaseBtn.innerHTML = `<i class="fas fa-check"></i> Đã tạo xong: ${data2.database}`;
                        
                        // Đảm bảo nút xóa được hiển thị đúng
                        deleteDatabaseBtn.style.display = '';
                        deleteDatabaseBtn.disabled = false;
                        deleteDatabaseBtn.innerHTML = '<i class="fas fa-trash"></i> Xóa Database';
                    } else {
                        setupInitialButtons();
                    }
                } else {
                    createDatabaseBtn.disabled = false;
                    createDatabaseBtn.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${data.detail || 'Tạo database thất bại!'}`;
                }
            } catch (err) {
                console.error("Lỗi khi tạo database:", err);
                createDatabaseBtn.disabled = false;
                createDatabaseBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Server error!';
            }
        };
        
        // Event handler cho nút xóa database
        deleteDatabaseBtn.onclick = async function() {
            username = localStorage.getItem('currentUser');
            // Lấy lại groupId mới nhất trước khi xóa
            let latest_groupId = localStorage.getItem('groupId_' + username) || '';
            groupId = latest_groupId;
            
            if (!username || !groupId || deleteDatabaseBtn.disabled) {
                return;
            }
            deleteDatabaseBtn.disabled = true;
            deleteDatabaseBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xóa database...';
            
            try {
                const res = await fetch(API_BASE_URL + '/delete_database', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username })
                });
                const data = await res.json();
                
                if (res.ok && data.success) {
                    // Sau khi xóa, gọi lại API /signin để lấy trạng thái database mới nhất
                    const res2 = await fetch(API_BASE_URL + '/signin', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, password: document.getElementById('password').value })
                    });
                    const data2 = await res2.json();
                    
                    if (res2.ok && data2.success) {
                        localStorage.setItem('groupId_' + username, data2.database || '');
                        localStorage.setItem('groupId', data2.database || '');
                    }
                    
                    // Sau khi xóa thành công, cập nhật localStorage
                    localStorage.setItem('groupId_' + username, '');
                    localStorage.setItem('groupId', '');
                    
                    // Cập nhật giao diện
                    updateDbButtons();
                } else {
                    // Xóa thất bại, trả lại trạng thái nút
                    deleteDatabaseBtn.disabled = false;
                    deleteDatabaseBtn.innerHTML = '<i class="fas fa-trash"></i> Xóa Database';
                    alert(data.detail || 'Không thể xóa database!');
                }
            } catch (err) {
                console.error('Lỗi khi xóa database:', err);
                deleteDatabaseBtn.disabled = false;
                deleteDatabaseBtn.innerHTML = '<i class="fas fa-trash"></i> Xóa Database';
                alert('Lỗi kết nối server!');
            }
        };
    }
    
    // Sign In logic
    const signinForm = document.getElementById('signinForm');
    const signinSection = document.getElementById('signinSection');
    const mainSection = document.getElementById('mainSection');
    const signinError = document.getElementById('signinError');

    if (signinForm) {
        signinForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            signinError.style.display = 'none';
            try {
                const res = await fetch(API_BASE_URL + '/signin', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                const data = await res.json();
                console.log('SignIn response:', data);
                if (res.ok && data.success) {
                    localStorage.setItem('currentUser', username);
                    // Khi đăng nhập, lấy đúng database của user này từ backend
                    localStorage.setItem('groupId_' + username, data.database || '');
                    localStorage.setItem('groupId', data.database || '');
                    
                    // Reset trạng thái đang xử lý khi đăng nhập
                    isProcessingDelete = false;
                    
                    // Cập nhật trạng thái các nút
                    if (typeof updateDbButtons === 'function') updateDbButtons();
                    
                    signinSection.style.display = 'none';
                    mainSection.style.display = '';
                } else {
                    signinError.textContent = data.detail || 'Sign in failed!';
                    signinError.style.display = 'block';
                }
            } catch (err) {
                signinError.textContent = 'Server error!';
                signinError.style.display = 'block';
            }
        });
    }
    // ShortInfo events
    if (shortinfoBrowseBtn && shortinfoFileInput) {
        shortinfoBrowseBtn.addEventListener('click', function() {
            shortinfoFileInput.click();
        });
        shortinfoFileInput.addEventListener('change', handleShortinfoFileSelect);
    }
    if (shortinfoUploadArea) {
        shortinfoUploadArea.addEventListener('dragover', e => handleDragOver(e, 'shortinfo'));
        shortinfoUploadArea.addEventListener('dragleave', e => handleDragLeave(e, 'shortinfo'));
        shortinfoUploadArea.addEventListener('drop', e => handleDrop(e, 'shortinfo'));
    }
    if (shortinfoUploadBtn) shortinfoUploadBtn.addEventListener('click', handleShortinfoUpload);
    if (shortinfoClearBtn) shortinfoClearBtn.addEventListener('click', clearShortinfoFiles);

    // RichInfo events
    if (richinfoBrowseBtn && richinfoFileInput) {
        richinfoBrowseBtn.addEventListener('click', function() {
            richinfoFileInput.click();
        });
        richinfoFileInput.addEventListener('change', handleRichinfoFileSelect);
    }
    if (richinfoUploadArea) {
        richinfoUploadArea.addEventListener('dragover', e => handleDragOver(e, 'richinfo'));
        richinfoUploadArea.addEventListener('dragleave', e => handleDragLeave(e, 'richinfo'));
        richinfoUploadArea.addEventListener('drop', e => handleDrop(e, 'richinfo'));
    }
    if (richinfoUploadBtn) richinfoUploadBtn.addEventListener('click', handleRichinfoUpload);
    if (richinfoClearBtn) richinfoClearBtn.addEventListener('click', clearRichinfoFiles);

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        document.addEventListener(eventName, preventDefaults, false);
    });

    // Delete table buttons
    const deleteShortinfoTableBtn = document.getElementById('deleteShortinfoTableBtn');
    const deleteRichinfoTableBtn = document.getElementById('deleteRichinfoTableBtn');

    if (deleteShortinfoTableBtn) {
        deleteShortinfoTableBtn.addEventListener('click', handleDeleteShortinfoTable);
    }

    if (deleteRichinfoTableBtn) {
        deleteRichinfoTableBtn.addEventListener('click', handleDeleteRichinfoTable);
    }
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleDragOver(e, type) {
    e.preventDefault();
    if (type === 'shortinfo') shortinfoUploadArea.classList.add('dragover');
    else richinfoUploadArea.classList.add('dragover');
}

function handleDragLeave(e, type) {
    e.preventDefault();
    if (type === 'shortinfo') shortinfoUploadArea.classList.remove('dragover');
    else richinfoUploadArea.classList.remove('dragover');
}

function handleDrop(e, type) {
    e.preventDefault();
    if (type === 'shortinfo') shortinfoUploadArea.classList.remove('dragover');
    else richinfoUploadArea.classList.remove('dragover');
    const files = Array.from(e.dataTransfer.files);
    if (type === 'shortinfo') addShortinfoFiles(files);
    else addRichinfoFiles(files);
}

function handleShortinfoFileSelect(e) {
    const files = Array.from(e.target.files);
    addShortinfoFiles(files);
}

function handleRichinfoFileSelect(e) {
    const files = Array.from(e.target.files);
    addRichinfoFiles(files);
}

function addShortinfoFiles(files) {
    files.forEach(file => {
        const exists = shortinfoFiles.some(f => f.name === file.name && f.size === file.size);
        if (!exists) shortinfoFiles.push(file);
    });
    updateShortinfoFilesList();
    updateShortinfoUploadButton();
    hideResult();
}

function addRichinfoFiles(files) {
    files.forEach(file => {
        const exists = richinfoFiles.some(f => f.name === file.name && f.size === file.size);
        if (!exists) richinfoFiles.push(file);
    });
    updateRichinfoFilesList();
    updateRichinfoUploadButton();
    hideResult();
}

function updateShortinfoFilesList() {
    shortinfoFilesContainer.innerHTML = '';
    if (shortinfoFiles.length === 0) {
        shortinfoFilesContainer.innerHTML = '<p class="no-files">No files selected</p>';
    } else {
        shortinfoFiles.forEach((file, idx) => {
            const div = document.createElement('div');
            div.className = 'file-item';
            let ext = file.name.split('.').pop().toLowerCase();
            let icon = '';
            if (ext === 'csv') icon = '<i class="fas fa-file-csv"></i>';
            else if (ext === 'xlsx') icon = '<i class="fas fa-file-excel"></i>';
            else if (ext === 'jpg' || ext === 'jpeg' || ext === 'png') icon = '<i class="fas fa-file-image"></i>';
            else if (ext === 'docx') icon = '<i class="fas fa-file-word"></i>';
            else if (ext === 'txt') icon = '<i class="fas fa-file-alt"></i>';
            else if (ext === 'pdf') icon = '<i class="fas fa-file-pdf"></i>';
            else icon = '<i class="fas fa-file"></i>';
            // Nút xóa
            const removeBtn = document.createElement('button');
            removeBtn.innerHTML = '<i class="fas fa-times"></i>';
            removeBtn.style.background = 'none';
            removeBtn.style.border = 'none';
            removeBtn.style.color = '#d32f2f';
            removeBtn.style.fontSize = '1.1em';
            removeBtn.style.cursor = 'pointer';
            removeBtn.style.marginLeft = 'auto';
            removeBtn.title = 'Bỏ chọn file';
            removeBtn.onclick = () => {
                shortinfoFiles.splice(idx, 1);
                updateShortinfoFilesList();
                updateShortinfoUploadButton();
            };
            div.innerHTML = `<span style='display:flex;align-items:center;gap:8px;'>${icon}<span>${file.name}</span></span>`;
            div.style.display = 'flex';
            div.style.alignItems = 'center';
            div.appendChild(removeBtn);
            shortinfoFilesContainer.appendChild(div);
        });
    }
}

function updateRichinfoFilesList() {
    richinfoFilesContainer.innerHTML = '';
    if (richinfoFiles.length === 0) {
        richinfoFilesContainer.innerHTML = '<p class="no-files">No files selected</p>';
    } else {
        richinfoFiles.forEach((file, idx) => {
            const div = document.createElement('div');
            div.className = 'file-item';
            let ext = file.name.split('.').pop().toLowerCase();
            let icon = '';
            if (ext === 'csv') icon = '<i class="fas fa-file-csv"></i>';
            else if (ext === 'xlsx') icon = '<i class="fas fa-file-excel"></i>';
            else if (ext === 'jpg' || ext === 'jpeg' || ext === 'png') icon = '<i class="fas fa-file-image"></i>';
            else if (ext === 'docx') icon = '<i class="fas fa-file-word"></i>';
            else if (ext === 'txt') icon = '<i class="fas fa-file-alt"></i>';
            else if (ext === 'pdf') icon = '<i class="fas fa-file-pdf"></i>';
            else icon = '<i class="fas fa-file"></i>';
            // Nút xóa
            const removeBtn = document.createElement('button');
            removeBtn.innerHTML = '<i class="fas fa-times"></i>';
            removeBtn.style.background = 'none';
            removeBtn.style.border = 'none';
            removeBtn.style.color = '#d32f2f';
            removeBtn.style.fontSize = '1.1em';
            removeBtn.style.cursor = 'pointer';
            removeBtn.style.marginLeft = 'auto';
            removeBtn.title = 'Bỏ chọn file';
            removeBtn.onclick = () => {
                richinfoFiles.splice(idx, 1);
                updateRichinfoFilesList();
                updateRichinfoUploadButton();
            };
            div.innerHTML = `<span style='display:flex;align-items:center;gap:8px;'>${icon}<span>${file.name}</span></span>`;
            div.style.display = 'flex';
            div.style.alignItems = 'center';
            div.appendChild(removeBtn);
            richinfoFilesContainer.appendChild(div);
        });
    }
}

function updateShortinfoUploadButton() {
    shortinfoUploadBtn.disabled = shortinfoFiles.length === 0;
}

function updateRichinfoUploadButton() {
    richinfoUploadBtn.disabled = richinfoFiles.length === 0;
}
Ư
function clearShortinfoFiles() {
    shortinfoFiles = [];
    updateShortinfoFilesList();
    updateShortinfoUploadButton();
    hideResult();
}

function clearRichinfoFiles() {
    richinfoFiles = [];
    updateRichinfoFilesList();
    updateRichinfoUploadButton();
    hideResult();
}

function hideResult() {
    resultSection.innerHTML = '';
}

async function handleShortinfoUpload() {
    if (shortinfoFiles.length === 0) return;
    await uploadFiles(shortinfoFiles, '/upload_shortinfo');
    clearShortinfoFiles();
}

async function handleRichinfoUpload() {
    if (richinfoFiles.length === 0) return;
    await uploadFiles(richinfoFiles, '/upload_richinfo');
    clearRichinfoFiles();
}

async function uploadFiles(files, endpoint) {
    progressSection.style.display = 'block';
    progressFill.style.width = '0%';
    progressText.textContent = 'Uploading... 0%';
    resultSection.innerHTML = '';
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    
    // Thêm username vào formData - MUST HAVE
    const username = localStorage.getItem('currentUser');  // FIX: Đúng key là currentUser
    console.log('Username from localStorage:', username);
    if (!username) {
        alert('Vui lòng đăng nhập trước khi upload!');
        progressSection.style.display = 'none';
        return;
    }
    formData.append('username', username);
    
    // Sử dụng XMLHttpRequest để lấy tiến trình upload
    const xhr = new XMLHttpRequest();
    xhr.open('POST', API_BASE_URL + endpoint, true);
    xhr.upload.onprogress = function(e) {
        if (e.lengthComputable) {
            const percent = Math.round((e.loaded / e.total) * 100);
            progressFill.style.width = percent + '%';
            progressText.textContent = 'Uploading... ' + percent + '%';
        }
    };
    xhr.onload = function() {
        progressFill.style.width = '100%';
        progressText.textContent = 'Completed!';
        // Hiển thị thông báo xanh đẹp mắt kèm tên file
        let fileNames = files.map(f => f.name).join(', ');
        let message = `Đã upload + xử lý thành công file: ${fileNames}`;
        const notifyDiv = document.createElement('div');
        notifyDiv.style.background = '#4BB543';
        notifyDiv.style.color = 'white';
        notifyDiv.style.padding = '16px';
        notifyDiv.style.borderRadius = '8px';
        notifyDiv.style.margin = '24px auto';
        notifyDiv.style.textAlign = 'center';
        notifyDiv.style.maxWidth = '500px';
        notifyDiv.style.fontSize = '1.1em';
        notifyDiv.textContent = message;
        resultSection.innerHTML = '';
        resultSection.appendChild(notifyDiv);
        setTimeout(() => {
            progressSection.style.display = 'none';
            resultSection.innerHTML = '';
        }, 5000);
    };
    xhr.onerror = function() {
        progressText.textContent = 'Upload failed!';
        resultSection.innerHTML = `<pre>Upload failed</pre>`;
        setTimeout(() => {
            progressSection.style.display = 'none';
        }, 2000);
    };
    xhr.send(formData);
}

// Hàm xóa table ShortInfo
async function handleDeleteShortinfoTable() {
    console.log('handleDeleteShortinfoTable called');
    const groupId = localStorage.getItem('groupId');
    console.log('groupId:', groupId);
    
    if (!groupId) {
        alert('Vui lòng đăng nhập và tạo database trước!');
        return;
    }

    if (!confirm('Bạn có chắc chắn muốn xóa toàn bộ table ShortInfo? Hành động này không thể hoàn tác!')) {
        return;
    }

    const deleteBtn = document.getElementById('deleteShortinfoTableBtn');
    deleteBtn.disabled = true;
    deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xóa...';

    try {
        console.log('Calling API delete_tb_shortinfo with groupId:', groupId);
        const res = await fetch(API_BASE_URL + '/delete_tb_shortinfo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ groupId })
        });

        const data = await res.json();
        console.log('Response:', data);

        if (res.ok && data.success) {
            // Hiển thị thông báo thành công
            const notifyDiv = document.createElement('div');
            notifyDiv.style.background = '#4BB543';
            notifyDiv.style.color = 'white';
            notifyDiv.style.padding = '16px';
            notifyDiv.style.borderRadius = '8px';
            notifyDiv.style.margin = '24px auto';
            notifyDiv.style.textAlign = 'center';
            notifyDiv.style.maxWidth = '500px';
            notifyDiv.style.fontSize = '1.1em';
            notifyDiv.textContent = data.message || 'Đã xóa table ShortInfo thành công!';
            resultSection.innerHTML = '';
            resultSection.appendChild(notifyDiv);

            setTimeout(() => {
                resultSection.innerHTML = '';
            }, 3000);
        } else {
            alert(data.detail || 'Xóa table thất bại!');
        }
    } catch (err) {
        console.error('Lỗi khi xóa table:', err);
        alert('Lỗi kết nối server: ' + err.message);
    } finally {
        deleteBtn.disabled = false;
        deleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i> Xóa Table ShortInfo';
    }
}

// Hàm xóa table RichInfo
async function handleDeleteRichinfoTable() {
    console.log('handleDeleteRichinfoTable called');
    const groupId = localStorage.getItem('groupId');
    console.log('groupId:', groupId);
    
    if (!groupId) {
        alert('Vui lòng đăng nhập và tạo database trước!');
        return;
    }

    if (!confirm('Bạn có chắc chắn muốn xóa toàn bộ table RichInfo? Hành động này không thể hoàn tác!')) {
        return;
    }

    const deleteBtn = document.getElementById('deleteRichinfoTableBtn');
    deleteBtn.disabled = true;
    deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xóa...';

    try {
        console.log('Calling API delete_tb_richinfo with groupId:', groupId);
        const res = await fetch(API_BASE_URL + '/delete_tb_richinfo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ groupId })
        });

        const data = await res.json();
        console.log('Response:', data);

        if (res.ok && data.success) {
            // Hiển thị thông báo thành công
            const notifyDiv = document.createElement('div');
            notifyDiv.style.background = '#4BB543';
            notifyDiv.style.color = 'white';
            notifyDiv.style.padding = '16px';
            notifyDiv.style.borderRadius = '8px';
            notifyDiv.style.margin = '24px auto';
            notifyDiv.style.textAlign = 'center';
            notifyDiv.style.maxWidth = '500px';
            notifyDiv.style.fontSize = '1.1em';
            notifyDiv.textContent = data.message || 'Đã xóa table RichInfo thành công!';
            resultSection.innerHTML = '';
            resultSection.appendChild(notifyDiv);

            setTimeout(() => {
                resultSection.innerHTML = '';
            }, 3000);
        } else {
            alert(data.detail || 'Xóa table thất bại!');
        }
    } catch (err) {
        console.error('Lỗi khi xóa table:', err);
        alert('Lỗi kết nối server: ' + err.message);
    } finally {
        deleteBtn.disabled = false;
        deleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i> Xóa Table RichInfo';
    }
}
