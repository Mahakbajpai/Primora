/**
 * api.js - Shared API utility and helper functions
 * All fetch calls go through these functions for consistent error handling.
 */

const API_BASE = '/api';  // Relative URL — works locally and in prod

// ─────────────────────────────────────────────
// CORE FETCH WRAPPER
// ─────────────────────────────────────────────

async function apiFetch(path, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      const message = data.detail || `HTTP ${res.status}: ${res.statusText}`;
      throw new Error(message);
    }

    return data;
  } catch (err) {
    console.error(`[API] ${options.method || 'GET'} ${path}`, err.message);
    throw err;
  }
}

// ─────────────────────────────────────────────
// API FUNCTIONS
// ─────────────────────────────────────────────

const API = {
  // Vendors
  getVendors: (search = '') =>
    apiFetch(`/vendors${search ? `?search=${encodeURIComponent(search)}` : ''}`),

  createVendor: (data) =>
    apiFetch('/vendors', { method: 'POST', body: JSON.stringify(data) }),

  // Products
  getProducts: () => apiFetch('/products'),

  createProduct: (data) =>
    apiFetch('/products', { method: 'POST', body: JSON.stringify(data) }),

  getAIDescription: (productName, category = 'General') =>
    apiFetch('/products/ai-description', {
      method: 'POST',
      body: JSON.stringify({ product_name: productName, category })
    }),

  // Purchase Orders
  getPurchaseOrders: () => apiFetch('/purchase-orders'),

  getPurchaseOrder: (id) => apiFetch(`/purchase-orders/${id}`),

  createPurchaseOrder: (data) =>
    apiFetch('/purchase-orders', { method: 'POST', body: JSON.stringify(data) }),
};

// ─────────────────────────────────────────────
// TOAST NOTIFICATIONS
// ─────────────────────────────────────────────

function showToast(message, type = 'info', duration = 3500) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const icons = { success: '✓', error: '✕', info: 'i' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span style="font-weight:600; font-size:0.9rem;">${icons[type] || '•'}</span>
    <span>${message}</span>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ─────────────────────────────────────────────
// FORMATTING HELPERS
// ─────────────────────────────────────────────

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2
  }).format(amount);
}

function formatDate(isoString) {
  if (!isoString) return '—';
  return new Date(isoString).toLocaleDateString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
}

function statusBadge(status) {
  const cls = {
    'Pending': 'badge-pending',
    'Approved': 'badge-approved',
    'Completed': 'badge-completed'
  }[status] || 'badge-pending';
  return `<span class="badge ${cls}">${status}</span>`;
}

// ─────────────────────────────────────────────
// ACTIVE NAV LINK
// ─────────────────────────────────────────────

function setActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach(a => {
    a.classList.remove('active');
    if (a.getAttribute('href') === path) a.classList.add('active');
  });
}

document.addEventListener('DOMContentLoaded', setActiveNav);
