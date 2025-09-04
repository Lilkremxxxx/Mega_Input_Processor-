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
        shortinfoFiles.forEach(file => {
            const div = document.createElement('div');
            div.className = 'file-item';
            div.textContent = file.name;
            shortinfoFilesContainer.appendChild(div);
        });
    }
}

function updateRichinfoFilesList() {
    richinfoFilesContainer.innerHTML = '';
    if (richinfoFiles.length === 0) {
        richinfoFilesContainer.innerHTML = '<p class="no-files">No files selected</p>';
    } else {
        richinfoFiles.forEach(file => {
            const div = document.createElement('div');
            div.className = 'file-item';
            div.textContent = file.name;
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
    progressText.textContent = 'Uploading...';
    resultSection.innerHTML = '';
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    try {
        const response = await fetch(API_BASE_URL + endpoint, {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        progressFill.style.width = '100%';
        progressText.textContent = 'Upload complete!';
        resultSection.innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;
    } catch (error) {
        progressText.textContent = 'Upload failed!';
        resultSection.innerHTML = `<pre>${error}</pre>`;
    }
    setTimeout(() => {
        progressSection.style.display = 'none';
    }, 2000);
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = Array.from(e.dataTransfer.files);
    addFiles(files);
}

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    addFiles(files);
}

function addFiles(files) {
    files.forEach(file => {
        // Check if file already exists
        const exists = selectedFiles.some(f => f.name === file.name && f.size === file.size);
        if (!exists) {
            selectedFiles.push(file);
        }
    });
    
    updateFilesList();
    updateUploadButton();
    hideResult();
}

function updateFilesList() {
    if (selectedFiles.length === 0) {
        filesContainer.innerHTML = '<p class="no-files">No files selected</p>';
        return;
    }
    
    const filesHTML = selectedFiles.map((file, index) => {
        const fileSize = formatFileSize(file.size);
        const fileIcon = getFileIcon(file.name);
        const fileIconClass = getFileIconClass(file.name);
        
        return `
            <div class="file-item">
                <div class="file-info">
                    <i class="fas ${fileIcon} file-icon ${fileIconClass}"></i>
                    <div class="file-details">
                        <h4>${file.name}</h4>
                        <p>${fileSize} • ${file.type || 'Unknown type'}</p>
                    </div>
                </div>
                <button class="remove-file" onclick="removeFile(${index})">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    }).join('');
    
    filesContainer.innerHTML = filesHTML;
}

function getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const iconMap = {
        'csv': 'fa-file-csv',
        'jpg': 'fa-file-image',
        'jpeg': 'fa-file-image',
        'png': 'fa-file-image',
        'gif': 'fa-file-image',
        'pdf': 'fa-file-pdf',
        'doc': 'fa-file-word',
        'docx': 'fa-file-word',
        'xls': 'fa-file-excel',
        'xlsx': 'fa-file-excel',
        'txt': 'fa-file-alt',
        'zip': 'fa-file-archive',
        'rar': 'fa-file-archive'
    };
    
    return iconMap[ext] || 'fa-file';
}

function getFileIconClass(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    return `file-${ext}` || 'file-default';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFilesList();
    updateUploadButton();
    
    // Reset file input
    fileInput.value = '';
}

function clearFiles() {
    selectedFiles = [];
    fileInput.value = '';
    updateFilesList();
    updateUploadButton();
    hideProgress();
    hideResult();
}

function updateUploadButton() {
    uploadBtn.disabled = selectedFiles.length === 0;
}

async function handleUpload() {
    if (selectedFiles.length === 0) {
        showResult('Please select files to upload.', 'error');
        return;
    }
    
    const formData = new FormData();
    selectedFiles.forEach(file => {
        formData.append('files', file);
    });
    
    try {
        showProgress();
        uploadBtn.disabled = true;
        
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showResult(`✅ ${result.message}`, 'success');
            
            // Show uploaded files list
            if (result.files && result.files.length > 0) {
                const filesList = result.files.map(file => `<li>${file}</li>`).join('');
                showResult(`
                    ✅ ${result.message}
                    <br><br><strong>Uploaded files:</strong>
                    <ul style="margin-top: 10px; padding-left: 20px;">
                        ${filesList}
                    </ul>
                `, 'success');
            }
            
            // Clear files after successful upload
            setTimeout(() => {
                clearFiles();
            }, 2000);
            
        } else {
            showResult(`❌ Upload failed: ${result.detail || 'Unknown error'}`, 'error');
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        showResult(`❌ Upload failed: ${error.message}`, 'error');
    } finally {
        hideProgress();
        uploadBtn.disabled = false;
        updateUploadButton();
    }
}

function showProgress() {
    progressSection.style.display = 'block';
    let progress = 0;
    
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        
        progressFill.style.width = progress + '%';
        progressText.textContent = `Uploading... ${Math.round(progress)}%`;
    }, 200);
    
    // Store interval ID for cleanup
    progressSection.dataset.intervalId = interval;
}

function hideProgress() {
    const intervalId = progressSection.dataset.intervalId;
    if (intervalId) {
        clearInterval(intervalId);
    }
    
    progressSection.style.display = 'none';
    progressFill.style.width = '0%';
    progressText.textContent = 'Uploading...';
}

function showResult(message, type) {
    resultSection.innerHTML = message;
    resultSection.className = `result-section result-${type}`;
    resultSection.style.display = 'block';
    
    // Auto hide success messages after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            hideResult();
        }, 5000);
    }
}

function hideResult() {
    resultSection.style.display = 'none';
    resultSection.innerHTML = '';
    resultSection.className = 'result-section';
}

// Utility function to check server status
async function checkServerStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/docs`);
        if (response.ok) {
            showResult('✅ Server is running and ready!', 'info');
        }
    } catch (error) {
        showResult('⚠️ Server is not running. Please start the FastAPI server first.', 'error');
    }
}

// Check server status on page load
window.addEventListener('load', () => {
    setTimeout(checkServerStatus, 1000);
});
