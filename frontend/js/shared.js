/**
 * shared.js — Shared navbar HTML, WhatsApp widget, greeting
 * Injected into every page on DOMContentLoaded
 */

const WHATSAPP_NUMBER = '918604996636';
const WHATSAPP_MSG    = encodeURIComponent('Hello Primora Support! I need help with my Purchase Order.');
const APP_TAGLINE     = 'Smart Purchase Order & Vendor Management System';

function getUsername() {
  try {
    const auth = JSON.parse(sessionStorage.getItem('poms_auth') || '{}');
    return auth.user || 'User';
  } catch { return 'User'; }
}

function injectNavbar(activePage) {
  const user = getUsername();
  const nav = document.getElementById('main-navbar');
  if (!nav) return;
  nav.innerHTML = `
    <a href="/" class="nav-brand">
      <img src="/static/assets/primora_logo.png" class="logo-img" alt="Primora Logo" />
      <div>
        <span class="brand-name">PRIMORA</span>
        <span class="brand-sub">ERP · Purchase Orders</span>
      </div>
    </a>
    <div class="nav-right">
      <span class="nav-greeting">Hi, <strong>${user}</strong> 👋</span>
      <ul class="nav-links">
        <li><a href="/dashboard" ${activePage==='dashboard'?'class="active"':''}>Dashboard</a></li>
        <li><a href="/create-po" ${activePage==='create-po'?'class="active"':''}>Create PO</a></li>
        <li><a href="/api/docs" target="_blank">API Docs</a></li>
      </ul>
    </div>
  `;
}

function injectWhatsApp() {
  const el = document.createElement('div');
  el.className = 'whatsapp-widget';
  el.innerHTML = `
    <a href="https://wa.me/${WHATSAPP_NUMBER}?text=${WHATSAPP_MSG}"
       target="_blank" class="whatsapp-btn" title="Chat with Primora Support">
      <svg class="whatsapp-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15
                 -.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075
                 -.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059
                 -.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52
                 .149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52
                 -.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51
                 -.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372
                 -.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074
                 .149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625
                 .712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413
                 .248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/>
        <path d="M12 0C5.373 0 0 5.373 0 12c0 2.123.553 4.116 1.522 5.847L.057 23.882
                 a.75.75 0 00.921.921l6.035-1.465A11.945 11.945 0 0012 24c6.627 0 12-5.373
                 12-12S18.627 0 12 0zm0 22c-1.891 0-3.667-.497-5.2-1.367l-.373-.214
                 -3.865.939.939-3.865-.214-.373A9.944 9.944 0 012 12C2 6.477 6.477 2 12 2
                 s10 4.477 10 10-4.477 10-10 10z"/>
      </svg>
      Support
    </a>
  `;
  document.body.appendChild(el);
}

function renderStars(rating) {
  let html = '<div class="star-rating">';
  for (let i = 1; i <= 5; i++) {
    html += `<span class="star ${i <= rating ? 'filled' : 'empty'}">★</span>`;
  }
  return html + '</div>';
}

const APP_REVIEWS = [
  { name: 'Rajesh Sharma', role: 'Procurement Head, TechMart', rating: 5, text: 'Primora completely transformed our purchase order workflow. What used to take days now takes minutes.', date: 'March 2026', color: '#3b82f6' },
  { name: 'Priya Mehta', role: 'Operations Manager, BuildFast', rating: 5, text: 'The vendor management and stock tracking features are outstanding. Highly recommend to any growing business.', date: 'February 2026', color: '#2dd4bf' },
  { name: 'Arjun Patel', role: 'Supply Chain Lead, InfraCo', rating: 4, text: 'Very intuitive interface. The auto tax calculation saves us so much manual work every single day.', date: 'February 2026', color: '#f5a623' },
  { name: 'Sunita Rao', role: 'Finance Director, ManuTech', rating: 5, text: 'Excellent system! Real-time stock validation has eliminated over-ordering completely for our team.', date: 'January 2026', color: '#4ade80' },
  { name: 'Vikram Singh', role: 'CEO, PrimeSource Ltd.', rating: 5, text: 'Primora gives us full visibility into our procurement pipeline. The receipt system is particularly impressive.', date: 'January 2026', color: '#a78bfa' },
  { name: 'Neha Gupta', role: 'Purchase Officer, LogiSupply', rating: 4, text: 'Clean, fast and reliable. The WhatsApp support is very responsive too. Great product overall!', date: 'December 2025', color: '#f43f5e' },
];

function renderReviewsSection(containerId) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = `
    <div class="page-header" style="margin-bottom:1.5rem;">
      <div class="page-title" style="font-size:1.8rem;">Customer <span>Reviews</span></div>
      <div class="page-subtitle">What our clients say about Primora</div>
    </div>
    <div class="reviews-grid">
      ${APP_REVIEWS.map(r => `
        <div class="review-card">
          <div class="review-header">
            <div class="review-avatar" style="background:${r.color};">${r.name.charAt(0)}</div>
            <div>
              <div class="review-name">${r.name}</div>
              <div class="review-role">${r.role}</div>
            </div>
          </div>
          ${renderStars(r.rating)}
          <div class="review-text">${r.text}</div>
          <div class="review-date">${r.date}</div>
        </div>
      `).join('')}
    </div>
  `;
}

function injectFooter() {
  const el = document.createElement('footer');
  el.className = 'footer';
  el.innerHTML = `
    <div class="footer-brand">PRIMORA</div>
    <div class="footer-tagline">${APP_TAGLINE}</div>
    <div style="font-size:0.75rem; color:var(--text-muted);">
      Customer Care: 
      <a href="https://wa.me/${WHATSAPP_NUMBER}" target="_blank"
         style="color:var(--whatsapp); text-decoration:none;">
        📱 +91 86049 96636
      </a>
      &nbsp;·&nbsp; © 2026 Primora. All rights reserved.
    </div>
  `;
  document.body.appendChild(el);
}
