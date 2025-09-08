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
