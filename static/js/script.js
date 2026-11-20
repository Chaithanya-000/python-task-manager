/**
 * TaskMaster Pro - Frontend Application Logic
 * REST API client, dynamic DOM rendering, and interactive dashboard state.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Application State
    const state = {
        tasks: [],
        filterStatus: 'All',       // 'All', 'Pending', 'Completed'
        filterPriority: 'All',     // 'All', 'High', 'Medium', 'Low'
        searchQuery: '',
        viewMode: 'table',        // 'table' or 'grid'
        loading: false
    };

    // DOM Elements
    const taskTableBody = document.getElementById('taskTableBody');
    const taskCardsRow = document.getElementById('taskCardsRow');
    const tableViewContainer = document.getElementById('tableViewContainer');
    const gridViewContainer = document.getElementById('gridViewContainer');
    const emptyStateContainer = document.getElementById('emptyStateContainer');
    const loadingStateContainer = document.getElementById('loadingStateContainer');
    const filteredTasksCount = document.getElementById('filteredTasksCount');
    const activeFiltersContainer = document.getElementById('activeFiltersContainer');

    // Stats Elements
    const totalTasksCount = document.getElementById('totalTasksCount');
    const pendingTasksCount = document.getElementById('pendingTasksCount');
    const completedTasksCount = document.getElementById('completedTasksCount');
    const completionRateText = document.getElementById('completionRateText');
    const completionProgressBar = document.getElementById('completionProgressBar');
    const rateSummaryLabel = document.getElementById('rateSummaryLabel');
    const statBadgeTotal = document.getElementById('statBadgeTotal');
    const statBadgePending = document.getElementById('statBadgePending');
    const statBadgeCompleted = document.getElementById('statBadgeCompleted');

    // Controls
    const taskSearchInput = document.getElementById('taskSearchInput');
    const headerSearchInput = document.getElementById('headerSearchInput');
    const clearSearchBtn = document.getElementById('clearSearchBtn');
    const tableViewBtn = document.getElementById('tableViewBtn');
    const gridViewBtn = document.getElementById('gridViewBtn');
    const refreshTasksBtn = document.getElementById('refreshTasksBtn');
    const currentPriorityLabel = document.getElementById('currentPriorityLabel');

    // Modals & Bootstrap Instances
    const addTaskModalEl = document.getElementById('addTaskModal');
    const addTaskModal = new bootstrap.Modal(addTaskModalEl);
    const addTaskForm = document.getElementById('addTaskForm');

    const editTaskModalEl = document.getElementById('editTaskModal');
    const editTaskModal = new bootstrap.Modal(editTaskModalEl);
    const editTaskForm = document.getElementById('editTaskForm');

    const deleteTaskModalEl = document.getElementById('deleteTaskModal');
    const deleteTaskModal = new bootstrap.Modal(deleteTaskModalEl);
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');

    const viewTaskModalEl = document.getElementById('viewTaskModal');
    const viewTaskModal = new bootstrap.Modal(viewTaskModalEl);

    // Toast Notification Instance
    const liveToastEl = document.getElementById('liveToast');
    const toastMessage = document.getElementById('toastMessage');
    const toastIcon = document.getElementById('toastIcon');
    const toastText = document.getElementById('toastText');
    const toast = new bootstrap.Toast(liveToastEl, { delay: 4000 });

    /**
     * Show Toast notification
     */
    function showNotification(message, type = 'success') {
        liveToastEl.classList.remove('bg-success', 'bg-danger', 'bg-warning', 'bg-info', 'bg-slate-900');

        if (type === 'success') {
            liveToastEl.classList.add('bg-success');
            toastIcon.className = 'bi bi-check-circle-fill fs-5';
        } else if (type === 'danger' || type === 'error') {
            liveToastEl.classList.add('bg-danger');
            toastIcon.className = 'bi bi-exclamation-triangle-fill fs-5';
        } else if (type === 'warning') {
            liveToastEl.classList.add('bg-warning');
            toastIcon.className = 'bi bi-exclamation-circle-fill fs-5';
        } else {
            liveToastEl.classList.add('bg-slate-900');
            toastIcon.className = 'bi bi-info-circle-fill fs-5';
        }

        toastText.textContent = message;
        toast.show();
    }

    /**
     * Helper to safely escape HTML
     */
    function escapeHtml(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return String(text).replace(/[&<>"']/g, m => map[m]);
    }

    /**
     * Fetch & Update Statistics from /api/stats
     */
    async function fetchStats() {
        try {
            const res = await fetch('/api/stats');
            if (!res.ok) throw new Error('Failed to fetch statistics');
            const data = await res.json();

            totalTasksCount.textContent = data.total;
            pendingTasksCount.textContent = data.pending;
            completedTasksCount.textContent = data.completed;
            completionRateText.textContent = `${data.completion_percentage}%`;

            completionProgressBar.style.width = `${data.completion_percentage}%`;
            completionProgressBar.setAttribute('aria-valuenow', data.completion_percentage);
            rateSummaryLabel.textContent = `${data.completed} / ${data.total} completed`;

            statBadgeTotal.textContent = data.total;
            statBadgePending.textContent = `${data.pending} Pending`;
            statBadgeCompleted.textContent = `${data.completed} Done`;
        } catch (err) {
            console.error('Error fetching stats:', err);
        }
    }

    /**
     * Fetch Tasks from /api/tasks based on current filters
     */
    async function fetchTasks() {
        setLoading(true);
        try {
            const params = new URLSearchParams();
            if (state.filterStatus && state.filterStatus !== 'All') {
                params.append('status', state.filterStatus);
            }
            if (state.filterPriority && state.filterPriority !== 'All') {
                params.append('priority', state.filterPriority);
            }
            if (state.searchQuery) {
                params.append('search', state.searchQuery);
            }

            const res = await fetch(`/api/tasks?${params.toString()}`);
            if (!res.ok) throw new Error('Failed to fetch tasks');
            const data = await res.json();

            state.tasks = data.tasks || [];
            renderTasks();
            updateFilterChips();
        } catch (err) {
            console.error('Error fetching tasks:', err);
            showNotification('Could not load tasks from server', 'danger');
        } finally {
            setLoading(false);
        }
    }

    /**
     * Set loading state in UI
     */
    function setLoading(isLoading) {
        state.loading = isLoading;
        if (isLoading) {
            loadingStateContainer.classList.remove('d-none');
            tableViewContainer.classList.add('d-none');
            gridViewContainer.classList.add('d-none');
            emptyStateContainer.classList.add('d-none');
        } else {
            loadingStateContainer.classList.add('d-none');
        }
    }

    /**
     * Render Priority Badge HTML
     */
    function renderPriorityBadge(priority) {
        const p = priority || 'Medium';
        if (p === 'High') {
            return `<span class="badge-priority-high"><span class="dot-indicator bg-danger"></span>High</span>`;
        } else if (p === 'Medium') {
            return `<span class="badge-priority-medium"><span class="dot-indicator bg-warning"></span>Medium</span>`;
        } else {
            return `<span class="badge-priority-low"><span class="dot-indicator bg-primary"></span>Low</span>`;
        }
    }

    /**
     * Render Status Badge HTML
     */
    function renderStatusBadge(status) {
        if (status === 'Completed') {
            return `<span class="badge-status-completed"><i class="bi bi-check-circle-fill"></i>Completed</span>`;
        } else {
            return `<span class="badge-status-pending"><i class="bi bi-clock-fill"></i>Pending</span>`;
        }
    }

    /**
     * Render Tasks (Table or Grid View)
     */
    function renderTasks() {
        const count = state.tasks.length;
        filteredTasksCount.textContent = count;

        if (count === 0) {
            tableViewContainer.classList.add('d-none');
            gridViewContainer.classList.add('d-none');
            emptyStateContainer.classList.remove('d-none');
            return;
        }

        emptyStateContainer.classList.add('d-none');

        if (state.viewMode === 'table') {
            renderTableView();
            tableViewContainer.classList.remove('d-none');
            gridViewContainer.classList.add('d-none');
        } else {
            renderGridView();
            gridViewContainer.classList.remove('d-none');
            tableViewContainer.classList.add('d-none');
        }
    }

    /**
     * Render Table Rows
     */
    function renderTableView() {
        taskTableBody.innerHTML = '';
        state.tasks.forEach(task => {
            const isCompleted = task.status === 'Completed';
            const tr = document.createElement('tr');
            tr.className = `task-row ${isCompleted ? 'is-completed' : ''}`;
            tr.dataset.id = task.id;

            tr.innerHTML = `
                <td class="text-center">
                    <button type="button" class="task-check-btn ${isCompleted ? 'checked' : ''}" data-action="toggle" data-id="${task.id}" title="${isCompleted ? 'Mark Pending' : 'Mark Completed'}">
                        <i class="bi bi-check-lg"></i>
                    </button>
                </td>
                <td class="text-slate-400 font-monospace small">#${task.id}</td>
                <td>
                    <div class="fw-semibold text-slate-800 task-title cursor-pointer" data-action="view" data-id="${task.id}">${escapeHtml(task.title)}</div>
                    ${task.description ? `<div class="small text-slate-500 task-desc text-truncate" style="max-width: 380px;">${escapeHtml(task.description)}</div>` : ''}
                </td>
                <td>${renderPriorityBadge(task.priority)}</td>
                <td>${renderStatusBadge(task.status)}</td>
                <td class="text-slate-500 small">
                    <i class="bi bi-calendar3 me-1 text-slate-400"></i>${task.created_at || 'Recently'}
                </td>
                <td class="text-end pe-4">
                    <div class="d-inline-flex gap-1">
                        <button type="button" class="action-btn" data-action="view" data-id="${task.id}" title="View Details">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button type="button" class="action-btn" data-action="edit" data-id="${task.id}" title="Edit Task">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button type="button" class="action-btn delete-btn" data-action="delete" data-id="${task.id}" title="Delete Task">
                            <i class="bi bi-trash3"></i>
                        </button>
                    </div>
                </td>
            `;
            taskTableBody.appendChild(tr);
        });
    }

    /**
     * Render Grid Cards
     */
    function renderGridView() {
        taskCardsRow.innerHTML = '';
        state.tasks.forEach(task => {
            const isCompleted = task.status === 'Completed';
            const col = document.createElement('div');
            col.className = 'col-12 col-md-6 col-xl-4';
            col.innerHTML = `
                <div class="card task-card-item h-100 p-3 ${isCompleted ? 'is-completed' : ''}" data-id="${task.id}">
                    <div class="d-flex align-items-start justify-content-between mb-2">
                        <span class="badge bg-slate-100 text-slate-500 font-monospace">#${task.id}</span>
                        <div class="d-flex gap-1">
                            ${renderPriorityBadge(task.priority)}
                            ${renderStatusBadge(task.status)}
                        </div>
                    </div>
                    <h6 class="fw-bold text-slate-900 mb-1 task-title cursor-pointer" data-action="view" data-id="${task.id}">${escapeHtml(task.title)}</h6>
                    <p class="text-slate-500 small mb-3 flex-grow-1 text-break" style="min-height: 40px;">
                        ${escapeHtml(task.description || 'No description provided.')}
                    </p>
                    <div class="d-flex align-items-center justify-content-between pt-2 border-top border-slate-100 small text-slate-400">
                        <span><i class="bi bi-calendar3 me-1"></i>${task.created_at || 'Recent'}</span>
                        <div class="d-flex gap-1">
                            <button type="button" class="action-btn" data-action="toggle" data-id="${task.id}" title="${isCompleted ? 'Mark Pending' : 'Mark Completed'}">
                                <i class="bi ${isCompleted ? 'bi-arrow-counterclockwise text-warning' : 'bi-check-circle-fill text-emerald'}"></i>
                            </button>
                            <button type="button" class="action-btn" data-action="edit" data-id="${task.id}" title="Edit Task">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button type="button" class="action-btn delete-btn" data-action="delete" data-id="${task.id}" title="Delete Task">
                                <i class="bi bi-trash3"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
            taskCardsRow.appendChild(col);
        });
    }

    /**
     * Filter Chips Display
     */
    function updateFilterChips() {
        activeFiltersContainer.innerHTML = '';
        if (state.filterStatus !== 'All') {
            const chip = document.createElement('span');
            chip.className = 'badge bg-slate-200 text-slate-700 d-inline-flex align-items-center gap-1';
            chip.innerHTML = `Status: ${state.filterStatus} <i class="bi bi-x cursor-pointer ms-1"></i>`;
            chip.querySelector('i').addEventListener('click', () => {
                setStatusFilter('All');
            });
            activeFiltersContainer.appendChild(chip);
        }

        if (state.filterPriority !== 'All') {
            const chip = document.createElement('span');
            chip.className = 'badge bg-slate-200 text-slate-700 d-inline-flex align-items-center gap-1';
            chip.innerHTML = `Priority: ${state.filterPriority} <i class="bi bi-x cursor-pointer ms-1"></i>`;
            chip.querySelector('i').addEventListener('click', () => {
                setPriorityFilter('All');
            });
            activeFiltersContainer.appendChild(chip);
        }

        if (state.searchQuery) {
            const chip = document.createElement('span');
            chip.className = 'badge bg-slate-200 text-slate-700 d-inline-flex align-items-center gap-1';
            chip.innerHTML = `Search: "${escapeHtml(state.searchQuery)}" <i class="bi bi-x cursor-pointer ms-1"></i>`;
            chip.querySelector('i').addEventListener('click', () => {
                clearSearch();
            });
            activeFiltersContainer.appendChild(chip);
        }
    }

    /**
     * Set Status Filter
     */
    function setStatusFilter(status) {
        state.filterStatus = status;
        document.querySelectorAll('.filter-status-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.status === status);
        });
        document.querySelectorAll('.sidebar-link[data-filter]').forEach(link => {
            link.classList.toggle('active', link.dataset.filter === status);
        });
        fetchTasks();
    }

    /**
     * Set Priority Filter
     */
    function setPriorityFilter(priority) {
        state.filterPriority = priority;
        currentPriorityLabel.textContent = priority === 'All' ? 'All Priorities' : `${priority} Priority`;
        document.querySelectorAll('.filter-priority-opt').forEach(opt => {
            opt.classList.toggle('active', opt.dataset.priority === priority);
        });
        fetchTasks();
    }

    /**
     * Clear Search
     */
    function clearSearch() {
        state.searchQuery = '';
        taskSearchInput.value = '';
        headerSearchInput.value = '';
        clearSearchBtn.classList.add('d-none');
        fetchTasks();
    }

    // -------------------------------------------------------------
    // Event Listeners: Search & Filters
    // -------------------------------------------------------------
    let debounceTimer;
    function handleSearchInput(e) {
        const query = e.target.value.trim();
        taskSearchInput.value = query;
        headerSearchInput.value = query;
        clearSearchBtn.classList.toggle('d-none', !query);

        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            state.searchQuery = query;
            fetchTasks();
        }, 300);
    }

    taskSearchInput.addEventListener('input', handleSearchInput);
    headerSearchInput.addEventListener('input', handleSearchInput);
    clearSearchBtn.addEventListener('click', clearSearch);

    // Status Filter Buttons
    document.querySelectorAll('.filter-status-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            setStatusFilter(btn.dataset.status);
        });
    });

    // Priority Dropdown Options
    document.querySelectorAll('.filter-priority-opt').forEach(opt => {
        opt.addEventListener('click', (e) => {
            e.preventDefault();
            setPriorityFilter(opt.dataset.priority);
        });
    });

    // Sidebar Links
    document.querySelectorAll('.sidebar-link[data-filter]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            setStatusFilter(link.dataset.filter);
        });
    });

    document.querySelectorAll('.sidebar-link[data-priority]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            setPriorityFilter(link.dataset.priority);
        });
    });

    // View Mode Toggles
    tableViewBtn.addEventListener('click', () => {
        state.viewMode = 'table';
        tableViewBtn.classList.add('active');
        gridViewBtn.classList.remove('active');
        renderTasks();
    });

    gridViewBtn.addEventListener('click', () => {
        state.viewMode = 'grid';
        gridViewBtn.classList.add('active');
        tableViewBtn.classList.remove('active');
        renderTasks();
    });

    // Refresh Tasks
    refreshTasksBtn.addEventListener('click', () => {
        fetchTasks();
        fetchStats();
        showNotification('Task list refreshed', 'info');
    });

    // -------------------------------------------------------------
    // Task Actions Delegator (Toggle, Edit, Delete, View)
    // -------------------------------------------------------------
    document.addEventListener('click', async (e) => {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        const action = target.dataset.action;
        const taskId = target.dataset.id;
        if (!taskId) return;

        if (action === 'toggle') {
            await handleToggleStatus(taskId);
        } else if (action === 'edit') {
            await openEditModal(taskId);
        } else if (action === 'delete') {
            openDeleteModal(taskId);
        } else if (action === 'view') {
            await openViewModal(taskId);
        }
    });

    /**
     * Toggle Task Status
     */
    async function handleToggleStatus(taskId) {
        try {
            const res = await fetch(`/api/tasks/${taskId}/status`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Failed to toggle status');

            showNotification(data.message || 'Status updated', 'success');
            await fetchStats();
            await fetchTasks();
        } catch (err) {
            console.error('Toggle error:', err);
            showNotification(err.message, 'danger');
        }
    }

    /**
     * Open Edit Modal
     */
    async function openEditModal(taskId) {
        try {
            const res = await fetch(`/api/tasks/${taskId}`);
            if (!res.ok) throw new Error('Task not found');
            const task = await res.json();

            document.getElementById('editTaskId').value = task.id;
            document.getElementById('editTaskIdLabel').textContent = task.id;
            document.getElementById('editTaskTitle').value = task.title;
            document.getElementById('editTaskDesc').value = task.description || '';
            document.getElementById('editTaskPriority').value = task.priority;
            document.getElementById('editTaskStatus').value = task.status;

            editTaskModal.show();
        } catch (err) {
            console.error('Fetch task error:', err);
            showNotification(err.message, 'danger');
        }
    }

    /**
     * Open Delete Modal
     */
    function openDeleteModal(taskId) {
        const task = state.tasks.find(t => t.id == taskId);
        const title = task ? task.title : `#${taskId}`;
        document.getElementById('deleteTaskId').value = taskId;
        document.getElementById('deleteTaskTitleSpan').textContent = `"${title}"`;
        deleteTaskModal.show();
    }

    /**
     * Open View Modal
     */
    async function openViewModal(taskId) {
        try {
            const res = await fetch(`/api/tasks/${taskId}`);
            if (!res.ok) throw new Error('Task not found');
            const task = await res.json();

            document.getElementById('viewTaskId').textContent = task.id;
            document.getElementById('viewTaskTitle').textContent = task.title;
            document.getElementById('viewTaskDesc').textContent = task.description || 'No description provided.';
            document.getElementById('viewTaskCreated').textContent = task.created_at || 'N/A';
            document.getElementById('viewTaskUpdated').textContent = task.updated_at || 'N/A';

            document.getElementById('viewTaskPriorityBadge').innerHTML = renderPriorityBadge(task.priority);
            document.getElementById('viewTaskStatusBadge').innerHTML = renderStatusBadge(task.status);

            const shortcutBtn = document.getElementById('viewEditShortcutBtn');
            shortcutBtn.onclick = () => {
                viewTaskModal.hide();
                openEditModal(task.id);
            };

            viewTaskModal.show();
        } catch (err) {
            console.error('View task error:', err);
            showNotification(err.message, 'danger');
        }
    }

    // -------------------------------------------------------------
    // Form Submissions
    // -------------------------------------------------------------

    // Add Task Form Submit
    addTaskForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const titleInput = document.getElementById('taskTitleInput');
        const descInput = document.getElementById('taskDescInput');
        const prioritySelect = document.getElementById('taskPrioritySelect');
        const statusSelect = document.getElementById('taskStatusSelect');

        const title = titleInput.value.trim();
        if (!title) {
            titleInput.classList.add('is-invalid');
            return;
        }
        titleInput.classList.remove('is-invalid');

        const payload = {
            title: title,
            description: descInput.value.trim(),
            priority: prioritySelect.value,
            status: statusSelect.value
        };

        const saveBtn = document.getElementById('saveTaskBtn');
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Saving...';

        try {
            const res = await fetch('/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Failed to create task');

            addTaskModal.hide();
            addTaskForm.reset();
            showNotification('Task created successfully!', 'success');
            await fetchStats();
            await fetchTasks();
        } catch (err) {
            console.error('Create task error:', err);
            showNotification(err.message, 'danger');
        } finally {
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="bi bi-check-lg me-1"></i> Save Task';
        }
    });

    // Edit Task Form Submit
    editTaskForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('editTaskId').value;
        const titleInput = document.getElementById('editTaskTitle');
        const descInput = document.getElementById('editTaskDesc');
        const prioritySelect = document.getElementById('editTaskPriority');
        const statusSelect = document.getElementById('editTaskStatus');

        const title = titleInput.value.trim();
        if (!title) {
            titleInput.classList.add('is-invalid');
            return;
        }
        titleInput.classList.remove('is-invalid');

        const payload = {
            title: title,
            description: descInput.value.trim(),
            priority: prioritySelect.value,
            status: statusSelect.value
        };

        const updateBtn = document.getElementById('updateTaskBtn');
        updateBtn.disabled = true;
        updateBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Updating...';

        try {
            const res = await fetch(`/api/tasks/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Failed to update task');

            editTaskModal.hide();
            showNotification('Task updated successfully!', 'success');
            await fetchStats();
            await fetchTasks();
        } catch (err) {
            console.error('Update task error:', err);
            showNotification(err.message, 'danger');
        } finally {
            updateBtn.disabled = false;
            updateBtn.innerHTML = '<i class="bi bi-save me-1"></i> Update Task';
        }
    });

    // Confirm Delete Button Click
    confirmDeleteBtn.addEventListener('click', async () => {
        const taskId = document.getElementById('deleteTaskId').value;
        if (!taskId) return;

        confirmDeleteBtn.disabled = true;
        confirmDeleteBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Deleting...';

        try {
            const res = await fetch(`/api/tasks/${taskId}`, {
                method: 'DELETE'
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Failed to delete task');

            deleteTaskModal.hide();
            showNotification('Task deleted successfully', 'success');
            await fetchStats();
            await fetchTasks();
        } catch (err) {
            console.error('Delete error:', err);
            showNotification(err.message, 'danger');
        } finally {
            confirmDeleteBtn.disabled = false;
            confirmDeleteBtn.innerHTML = 'Delete';
        }
    });

    /**
     * Check System Health on initialization
     */
    async function checkHealth() {
        try {
            const res = await fetch('/health');
            const data = await res.json();
            const badge = document.getElementById('sidebarHealthBadge');
            if (badge && res.ok && data.status === 'healthy') {
                badge.textContent = 'Healthy';
                badge.className = 'badge bg-emerald-subtle text-emerald border border-emerald-subtle';
            } else if (badge) {
                badge.textContent = 'Degraded';
                badge.className = 'badge bg-warning-subtle text-warning border border-warning-subtle';
            }
        } catch (err) {
            const badge = document.getElementById('sidebarHealthBadge');
            if (badge) {
                badge.textContent = 'Offline';
                badge.className = 'badge bg-danger-subtle text-danger border border-danger-subtle';
            }
        }
    }

    // -------------------------------------------------------------
    // Application Initialization
    // -------------------------------------------------------------
    checkHealth();
    fetchStats();
    fetchTasks();
});
