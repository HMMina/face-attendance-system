/**
 * Admin Dashboard JavaScript
 * Face Attendance System Management
 */

// Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';
let currentEmployee = null;
let employees = [];
let departments = [];

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    loadEmployees();
    loadDepartments();
    setupEventListeners();
});

// Initialize Dashboard
function initializeDashboard() {
    console.log('🚀 Admin Dashboard initialized');
    
    // Show employees panel by default
    showPanel('employees');
    
    // Setup navigation
    setupNavigation();
}

// Setup Navigation
function setupNavigation() {
    const navLinks = document.querySelectorAll('.list-group-item a');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active-menu'));
            
            // Add active class to clicked link
            this.classList.add('active-menu');
            
            // Show corresponding panel
            const panelId = this.getAttribute('href').substring(1);
            showPanel(panelId);
        });
    });
}

// Show Panel
function showPanel(panelId) {
    // Hide all panels
    const panels = document.querySelectorAll('.content-panel');
    panels.forEach(panel => panel.classList.add('d-none'));
    
    // Show selected panel
    const selectedPanel = document.getElementById(`${panelId}-panel`);
    if (selectedPanel) {
        selectedPanel.classList.remove('d-none');
    }
}

// Setup Event Listeners
function setupEventListeners() {
    // Search functionality
    document.getElementById('searchEmployee').addEventListener('input', filterEmployees);
    document.getElementById('departmentFilter').addEventListener('change', filterEmployees);
    document.getElementById('faceStatusFilter').addEventListener('change', filterEmployees);
    
    // Employee form validation
    const employeeForm = document.getElementById('employeeForm');
    employeeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        saveEmployee();
    });
}

// Load Employees
async function loadEmployees() {
    try {
        showLoading('Đang tải danh sách nhân viên...');
        
        const response = await fetch(`${API_BASE_URL}/employees/`);
        if (!response.ok) throw new Error('Failed to load employees');
        
        employees = await response.json();
        console.log(`📋 Loaded ${employees.length} employees`);
        
        // Load face status for each employee
        for (let employee of employees) {
            try {
                const faceResponse = await fetch(`${API_BASE_URL}/employees/${employee.id}/face-embeddings`);
                if (faceResponse.ok) {
                    const faceData = await faceResponse.json();
                    employee.faceCount = faceData.face_count;
                    employee.faces = faceData.faces || [];
                } else {
                    employee.faceCount = 0;
                    employee.faces = [];
                }
            } catch (error) {
                console.warn(`Failed to load face data for employee ${employee.employee_id}:`, error);
                employee.faceCount = 0;
                employee.faces = [];
            }
        }
        
        renderEmployeesTable();
        hideLoading();
        
    } catch (error) {
        console.error('❌ Error loading employees:', error);
        hideLoading();
        showAlert('Không thể tải danh sách nhân viên. Vui lòng thử lại.', 'danger');
    }
}

// Load Departments
async function loadDepartments() {
    try {
        const response = await fetch(`${API_BASE_URL}/employees/departments`);
        if (!response.ok) throw new Error('Failed to load departments');
        
        departments = await response.json();
        
        // Update department filter
        const departmentFilter = document.getElementById('departmentFilter');
        departmentFilter.innerHTML = '<option value="">Tất cả phòng ban</option>';
        
        departments.forEach(dept => {
            const option = document.createElement('option');
            option.value = dept;
            option.textContent = dept;
            departmentFilter.appendChild(option);
        });
        
        // Update department datalist in modal
        const departmentsList = document.getElementById('departmentsList');
        departmentsList.innerHTML = '';
        
        departments.forEach(dept => {
            const option = document.createElement('option');
            option.value = dept;
            departmentsList.appendChild(option);
        });
        
    } catch (error) {
        console.error('❌ Error loading departments:', error);
    }
}

// Render Employees Table
function renderEmployeesTable() {
    const tbody = document.querySelector('#employeesTable tbody');
    tbody.innerHTML = '';
    
    if (employees.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-4">
                    <i class="fas fa-users fa-3x text-muted mb-3"></i>
                    <p class="text-muted">Chưa có nhân viên nào trong hệ thống</p>
                    <button class="btn btn-primary" onclick="showAddEmployeeModal()">
                        <i class="fas fa-plus"></i> Thêm nhân viên đầu tiên
                    </button>
                </td>
            </tr>
        `;
        return;
    }
    
    employees.forEach(employee => {
        const row = document.createElement('tr');
        
        // Face status
        let faceStatus = '';
        if (employee.faceCount === 0) {
            faceStatus = '<span class="status-badge status-no-face"><i class="fas fa-times"></i> Chưa có ảnh</span>';
        } else if (employee.faceCount === 1) {
            faceStatus = '<span class="status-badge status-has-face"><i class="fas fa-check"></i> Đã có ảnh</span>';
        } else {
            faceStatus = `<span class="status-badge status-multiple-faces"><i class="fas fa-exclamation-triangle"></i> ${employee.faceCount} ảnh</span>`;
        }
        
        row.innerHTML = `
            <td><strong>${employee.employee_id}</strong></td>
            <td>${employee.name}</td>
            <td>${employee.department || '<em class="text-muted">Chưa xác định</em>'}</td>
            <td>${employee.position || '<em class="text-muted">Chưa xác định</em>'}</td>
            <td>${employee.email || '<em class="text-muted">Chưa có</em>'}</td>
            <td>${faceStatus}</td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button class="btn btn-outline-primary" onclick="editEmployee('${employee.employee_id}')" 
                            title="Chỉnh sửa">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-outline-success" onclick="manageFaces('${employee.employee_id}')" 
                            title="Quản lý ảnh">
                        <i class="fas fa-camera"></i>
                    </button>
                    <button class="btn btn-outline-danger" onclick="deleteEmployee('${employee.employee_id}')" 
                            title="Xóa">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

// Filter Employees
function filterEmployees() {
    const searchTerm = document.getElementById('searchEmployee').value.toLowerCase();
    const departmentFilter = document.getElementById('departmentFilter').value;
    const faceStatusFilter = document.getElementById('faceStatusFilter').value;
    
    const filteredEmployees = employees.filter(employee => {
        // Search filter
        const matchesSearch = !searchTerm || 
            employee.name.toLowerCase().includes(searchTerm) ||
            employee.employee_id.toLowerCase().includes(searchTerm) ||
            (employee.email && employee.email.toLowerCase().includes(searchTerm));
        
        // Department filter
        const matchesDepartment = !departmentFilter || employee.department === departmentFilter;
        
        // Face status filter
        let matchesFaceStatus = true;
        if (faceStatusFilter === 'has_face') {
            matchesFaceStatus = employee.faceCount > 0;
        } else if (faceStatusFilter === 'no_face') {
            matchesFaceStatus = employee.faceCount === 0;
        }
        
        return matchesSearch && matchesDepartment && matchesFaceStatus;
    });
    
    // Temporarily replace employees array for rendering
    const originalEmployees = employees;
    employees = filteredEmployees;
    renderEmployeesTable();
    employees = originalEmployees;
}

// Clear Filters
function clearFilters() {
    document.getElementById('searchEmployee').value = '';
    document.getElementById('departmentFilter').value = '';
    document.getElementById('faceStatusFilter').value = '';
    filterEmployees();
}

// Show Add Employee Modal
function showAddEmployeeModal() {
    console.log('Opening Add Employee Modal...');
    currentEmployee = null;
    document.getElementById('employeeModalTitle').textContent = 'Thêm nhân viên mới';
    
    // Reset form
    const form = document.getElementById('employeeForm');
    if (form) {
        form.reset();
        form.classList.remove('was-validated');
    }
    
    // Reset file upload
    resetFaceUpload();
    
    // Show modal with both jQuery and Bootstrap 5 methods
    const modalElement = document.getElementById('employeeModal');
    if (modalElement) {
        // Try Bootstrap 5 method first
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
        
        // Fallback to jQuery method
        $('#employeeModal').modal('show');
        
        console.log('Modal should be visible now');
    } else {
        console.error('Modal element not found!');
    }
}

// Edit Employee
async function editEmployee(employeeId) {
    try {
        const employee = employees.find(emp => emp.employee_id === employeeId);
        if (!employee) {
            showAlert('Không tìm thấy nhân viên', 'danger');
            return;
        }
        
        currentEmployee = employee;
        document.getElementById('employeeModalTitle').textContent = `Chỉnh sửa: ${employee.name}`;
        
        // Populate form
        document.getElementById('employeeId').value = employee.employee_id;
        document.getElementById('employeeName').value = employee.name;
        document.getElementById('employeeDepartment').value = employee.department || '';
        document.getElementById('employeePosition').value = employee.position || '';
        document.getElementById('employeeEmail').value = employee.email || '';
        document.getElementById('employeePhone').value = employee.phone || '';
        
        // Disable employee ID field for editing
        document.getElementById('employeeId').disabled = true;
        
        // Reset file upload
        resetFaceUpload();
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('employeeModal'));
        modal.show();
        
    } catch (error) {
        console.error('❌ Error editing employee:', error);
        showAlert('Không thể chỉnh sửa nhân viên', 'danger');
    }
}

// Save Employee
async function saveEmployee() {
    const form = document.getElementById('employeeForm');
    
    // Validate form
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return;
    }
    
    try {
        showLoading('Đang lưu thông tin nhân viên...');
        
        const faceFile = document.getElementById('faceUpload').files[0];
        
        if (!currentEmployee && faceFile) {
            // Create new employee with photo using FormData
            const formData = new FormData();
            formData.append('name', document.getElementById('employeeName').value);
            formData.append('department', document.getElementById('employeeDepartment').value || '');
            formData.append('position', document.getElementById('employeePosition').value || '');
            formData.append('email', document.getElementById('employeeEmail').value || '');
            formData.append('phone', document.getElementById('employeePhone').value || '');
            formData.append('employee_id', document.getElementById('employeeId').value || '');
            formData.append('photo', faceFile);
            
            const response = await fetch(`${API_BASE_URL}/employees/with-photo`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to create employee with photo');
            }
            
            const result = await response.json();
            console.log('✅ Employee created with photo:', result);
            
            // Show detailed result
            showEmployeeCreationResult(result);
            
        } else {
            // Standard employee creation/update without photo or update existing
            const employeeData = {
                employee_id: document.getElementById('employeeId').value,
                name: document.getElementById('employeeName').value,
                department: document.getElementById('employeeDepartment').value,
                position: document.getElementById('employeePosition').value,
                email: document.getElementById('employeeEmail').value,
                phone: document.getElementById('employeePhone').value
            };
            
            let response;
            if (currentEmployee) {
                // Update existing employee
                response = await fetch(`${API_BASE_URL}/employees/${currentEmployee.employee_id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(employeeData)
                });
            } else {
                // Create new employee without photo
                response = await fetch(`${API_BASE_URL}/employees/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(employeeData)
                });
            }
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to save employee');
            }
            
            const savedEmployee = await response.json();
            console.log('✅ Employee saved:', savedEmployee);
            
            // Handle face upload for existing employee
            if (faceFile && currentEmployee) {
                await uploadAdditionalPhoto(savedEmployee.employee_id, faceFile);
            }
        }
        
        // Close modal and refresh data
        bootstrap.Modal.getInstance(document.getElementById('employeeModal')).hide();
        await loadEmployees();
        
        hideLoading();
        
    } catch (error) {
        console.error('❌ Error saving employee:', error);
        hideLoading();
        showAlert(`Không thể lưu thông tin nhân viên: ${error.message}`, 'danger');
    }
}

// Upload Employee Face
async function uploadEmployeeFace(employeeId, file) {
    try {
        showUploadStatus('Đang xử lý ảnh khuôn mặt...');
        
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE_URL}/employees/${employeeId}/upload-face`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || 'Failed to upload face');
        }
        
        console.log('✅ Face uploaded successfully:', result);
        showUploadResult(result, 'success');
        
    } catch (error) {
        console.error('❌ Error uploading face:', error);
        showUploadResult({ message: error.message }, 'error');
    }
}

// Preview Face Image
function previewFaceImage(input) {
    const file = input.files[0];
    if (!file) {
        document.getElementById('imagePreview').classList.add('d-none');
        return;
    }
    
    // Validate file
    if (!file.type.startsWith('image/')) {
        showAlert('Vui lòng chọn file ảnh hợp lệ', 'warning');
        input.value = '';
        return;
    }
    
    if (file.size > 5 * 1024 * 1024) { // 5MB
        showAlert('Kích thước file không được vượt quá 5MB', 'warning');
        input.value = '';
        return;
    }
    
    // Show preview
    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.getElementById('imagePreview');
        const img = document.getElementById('previewImg');
        const info = document.getElementById('imageInfo');
        
        img.src = e.target.result;
        info.textContent = `${file.name} (${formatFileSize(file.size)})`;
        
        preview.classList.remove('d-none');
    };
    reader.readAsDataURL(file);
}

// Reset Face Upload
function resetFaceUpload() {
    document.getElementById('faceUpload').value = '';
    document.getElementById('imagePreview').classList.add('d-none');
    document.getElementById('uploadStatus').classList.add('d-none');
    document.getElementById('uploadResult').classList.add('d-none');
    
    // Re-enable employee ID field
    document.getElementById('employeeId').disabled = false;
}

// Show Upload Status
function showUploadStatus(message) {
    const statusDiv = document.getElementById('uploadStatus');
    statusDiv.innerHTML = `
        <div class="alert alert-info">
            <i class="fas fa-spinner fa-spin"></i> ${message}
        </div>
    `;
    statusDiv.classList.remove('d-none');
}

// Show Upload Result
function showUploadResult(result, type) {
    const resultDiv = document.getElementById('uploadResult');
    
    if (type === 'success') {
        resultDiv.innerHTML = `
            <div class="alert alert-success">
                <h6><i class="fas fa-check-circle"></i> Upload thành công!</h6>
                <ul class="mb-0">
                    <li>Nhân viên: <strong>${result.employee_name}</strong></li>
                    <li>Độ tin cậy: <strong>${(result.confidence * 100).toFixed(1)}%</strong></li>
                    <li>Chất lượng ảnh: <strong>${result.face_quality}</strong></li>
                    ${result.is_primary ? '<li><span class="badge bg-success">Ảnh chính</span></li>' : ''}
                </ul>
            </div>
        `;
    } else {
        resultDiv.innerHTML = `
            <div class="alert alert-danger">
                <h6><i class="fas fa-exclamation-triangle"></i> Upload thất bại!</h6>
                <p class="mb-0">${result.message}</p>
            </div>
        `;
    }
    
    resultDiv.classList.remove('d-none');
    document.getElementById('uploadStatus').classList.add('d-none');
}

// Manage Faces
async function manageFaces(employeeId) {
    try {
        const employee = employees.find(emp => emp.employee_id === employeeId);
        if (!employee) {
            showAlert('Không tìm thấy nhân viên', 'danger');
            return;
        }
        
        // Load face data
        showLoading('Đang tải thông tin ảnh...');
        
        const response = await fetch(`${API_BASE_URL}/employees/${employee.id}/face-embeddings`);
        if (!response.ok) throw new Error('Failed to load face data');
        
        const faceData = await response.json();
        
        // Update modal
        document.getElementById('faceModalTitle').textContent = `Quản lý ảnh: ${employee.name}`;
        
        const content = document.getElementById('faceManagementContent');
        
        if (faceData.face_count === 0) {
            content.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-camera fa-3x text-muted mb-3"></i>
                    <h5>Chưa có ảnh khuôn mặt</h5>
                    <p class="text-muted">Nhân viên này chưa có ảnh nào trong hệ thống</p>
                    <button class="btn btn-primary" onclick="uploadFaceForEmployee('${employeeId}')">
                        <i class="fas fa-upload"></i> Upload ảnh mới
                    </button>
                </div>
            `;
        } else {
            let facesHtml = `
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h6>Tổng cộng: ${faceData.face_count} ảnh</h6>
                    <button class="btn btn-sm btn-primary" onclick="uploadFaceForEmployee('${employeeId}')">
                        <i class="fas fa-plus"></i> Thêm ảnh
                    </button>
                </div>
                <div class="row">
            `;
            
            faceData.faces.forEach(face => {
                facesHtml += `
                    <div class="col-md-4 mb-3">
                        <div class="card face-card ${face.is_primary ? 'primary' : ''}">
                            <div class="card-body text-center">
                                <i class="fas fa-user-circle fa-3x text-muted mb-2"></i>
                                <h6 class="card-title">ID: ${face.id}</h6>
                                <p class="card-text small">
                                    <strong>Độ tin cậy:</strong> ${(face.confidence * 100).toFixed(1)}%<br>
                                    <strong>Nguồn:</strong> ${face.source}<br>
                                    <strong>Ngày tạo:</strong> ${new Date(face.created_at).toLocaleDateString('vi-VN')}
                                    ${face.is_primary ? '<br><span class="badge bg-success">Ảnh chính</span>' : ''}
                                </p>
                                <button class="btn btn-sm btn-outline-danger" 
                                        onclick="deleteFaceEmbedding('${employeeId}', ${face.id})">
                                    <i class="fas fa-trash"></i> Xóa
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            facesHtml += '</div>';
            content.innerHTML = facesHtml;
        }
        
        hideLoading();
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('faceModal'));
        modal.show();
        
    } catch (error) {
        console.error('❌ Error managing faces:', error);
        hideLoading();
        showAlert('Không thể tải thông tin ảnh', 'danger');
    }
}

// Upload Face for Employee
function uploadFaceForEmployee(employeeId) {
    // Close face modal and open employee edit modal with focus on upload
    bootstrap.Modal.getInstance(document.getElementById('faceModal')).hide();
    
    setTimeout(() => {
        editEmployee(employeeId);
        
        setTimeout(() => {
            document.getElementById('faceUpload').focus();
            document.getElementById('faceUpload').scrollIntoView({ behavior: 'smooth' });
        }, 500);
    }, 300);
}

// Delete Face Embedding
async function deleteFaceEmbedding(employeeId, embeddingId) {
    if (!confirm('Bạn có chắc chắn muốn xóa ảnh này?')) {
        return;
    }
    
    try {
        showLoading('Đang xóa ảnh...');
        
        const response = await fetch(`${API_BASE_URL}/employees/${employeeId}/face-embeddings/${embeddingId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to delete face');
        }
        
        hideLoading();
        showAlert('Đã xóa ảnh thành công', 'success');
        
        // Refresh face management modal
        manageFaces(employeeId);
        
        // Refresh employees list
        await loadEmployees();
        
    } catch (error) {
        console.error('❌ Error deleting face:', error);
        hideLoading();
        showAlert(`Không thể xóa ảnh: ${error.message}`, 'danger');
    }
}

// Delete Employee
async function deleteEmployee(employeeId) {
    const employee = employees.find(emp => emp.employee_id === employeeId);
    if (!employee) {
        showAlert('Không tìm thấy nhân viên', 'danger');
        return;
    }
    
    if (!confirm(`Bạn có chắc chắn muốn xóa nhân viên "${employee.name}"?\n\nHành động này sẽ xóa tất cả dữ liệu và ảnh của nhân viên.`)) {
        return;
    }
    
    try {
        showLoading('Đang xóa nhân viên...');
        
        const response = await fetch(`${API_BASE_URL}/employees/${employeeId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to delete employee');
        }
        
        hideLoading();
        showAlert(`Đã xóa nhân viên ${employee.name} thành công`, 'success');
        
        // Refresh employees list
        await loadEmployees();
        
    } catch (error) {
        console.error('❌ Error deleting employee:', error);
        hideLoading();
        showAlert(`Không thể xóa nhân viên: ${error.message}`, 'danger');
    }
}

// Utility Functions

// Show Loading
function showLoading(message = 'Đang xử lý...') {
    const existingOverlay = document.querySelector('.loading-overlay');
    if (existingOverlay) {
        existingOverlay.remove();
    }
    
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="text-center text-white">
            <div class="loading-spinner mb-3"></div>
            <p>${message}</p>
        </div>
    `;
    document.body.appendChild(overlay);
}

// Hide Loading
function hideLoading() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}

// Show Alert
function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert-auto-dismiss');
    existingAlerts.forEach(alert => alert.remove());
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show alert-auto-dismiss`;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Show Employee Creation Result
function showEmployeeCreationResult(result) {
    const uploadResult = document.getElementById('uploadResult');
    uploadResult.classList.remove('d-none');
    
    let alertClass = 'success';
    let icon = 'fas fa-check-circle';
    
    if (!result.face_recognition?.face_detected) {
        alertClass = 'warning';
        icon = 'fas fa-exclamation-triangle';
    }
    
    uploadResult.innerHTML = `
        <div class="alert alert-${alertClass}">
            <h6><i class="${icon}"></i> Kết quả xử lý</h6>
            <ul class="mb-0">
                <li><strong>Nhân viên:</strong> ${result.employee?.name} (${result.employee?.employee_id})</li>
                <li><strong>Ảnh đã lưu:</strong> ${result.photo?.stored_locally ? 'Có' : 'Không'}</li>
                ${result.photo?.file_size ? `<li><strong>Kích thước:</strong> ${formatFileSize(result.photo.file_size)}</li>` : ''}
                ${result.photo?.dimensions ? `<li><strong>Kích thước ảnh:</strong> ${result.photo.dimensions}</li>` : ''}
                <li><strong>Phát hiện khuôn mặt:</strong> ${result.face_recognition?.face_detected ? 'Có' : 'Không'}</li>
                ${result.face_recognition?.face_quality ? `<li><strong>Chất lượng khuôn mặt:</strong> ${Math.round(result.face_recognition.face_quality * 100)}%</li>` : ''}
                <li><strong>Embedding lưu trữ:</strong> ${result.face_recognition?.embedding_stored ? 'Có' : 'Không'}</li>
                ${result.face_recognition?.processing_time ? `<li><strong>Thời gian xử lý:</strong> ${Math.round(result.face_recognition.processing_time * 1000)}ms</li>` : ''}
            </ul>
        </div>
    `;
    
    // Auto hide after success
    if (alertClass === 'success') {
        setTimeout(() => {
            uploadResult.classList.add('d-none');
        }, 5000);
    }
}

// Upload Additional Photo
async function uploadAdditionalPhoto(employeeId, file) {
    try {
        showUploadStatus('Đang tải ảnh bổ sung...');
        
        const formData = new FormData();
        formData.append('photo', file);
        
        const response = await fetch(`${API_BASE_URL}/employees/${employeeId}/photos/upload`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || 'Failed to upload photo');
        }
        
        console.log('✅ Additional photo uploaded:', result);
        showEmployeeCreationResult(result);
        
    } catch (error) {
        console.error('❌ Error uploading additional photo:', error);
        showUploadResult({ message: error.message }, 'error');
    }
}

// Show Upload Status
function showUploadStatus(message) {
    const statusDiv = document.getElementById('uploadStatus');
    statusDiv.classList.remove('d-none');
    statusDiv.innerHTML = `
        <div class="alert alert-info">
            <i class="fas fa-spinner fa-spin"></i> ${message}
        </div>
    `;
}

// Hide Upload Status
function hideUploadStatus() {
    document.getElementById('uploadStatus').classList.add('d-none');
}

// Show Upload Result
function showUploadResult(result, type) {
    hideUploadStatus();
    
    const resultDiv = document.getElementById('uploadResult');
    resultDiv.classList.remove('d-none');
    
    let alertClass = type === 'success' ? 'success' : 'danger';
    let icon = type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle';
    
    resultDiv.innerHTML = `
        <div class="alert alert-${alertClass}">
            <h6><i class="${icon}"></i> ${type === 'success' ? 'Thành công' : 'Lỗi'}</h6>
            <p class="mb-0">${result.message || 'Có lỗi xảy ra'}</p>
        </div>
    `;
    
    // Auto hide after 3 seconds
    setTimeout(() => {
        resultDiv.classList.add('d-none');
    }, 3000);
}

// Format File Size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Export functions for global access
window.showAddEmployeeModal = showAddEmployeeModal;
window.editEmployee = editEmployee;
window.manageFaces = manageFaces;
window.deleteEmployee = deleteEmployee;
window.deleteFaceEmbedding = deleteFaceEmbedding;
window.uploadFaceForEmployee = uploadFaceForEmployee;
window.previewFaceImage = previewFaceImage;
window.saveEmployee = saveEmployee;
window.clearFilters = clearFilters;
