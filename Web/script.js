// Global variables
let selectedFiles = [];
const API_BASE_URL = 'http://localhost:8000';

// DOM elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const filesContainer = document.getElementById('filesContainer');
const uploadBtn = document.getElementById('uploadBtn');
const clearBtn = document.getElementById('clearBtn');
const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const resultSection = document.getElementById('resultSection');

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
});

function initializeEventListeners() {
    // File input change
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop events
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    uploadArea.addEventListener('click', () => fileInput.click());
    
    // Button events
    uploadBtn.addEventListener('click', handleUpload);
    clearBtn.addEventListener('click', clearFiles);
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        document.addEventListener(eventName, preventDefaults, false);
    });
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
