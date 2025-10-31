function switchTab(tabName) {
  document.querySelectorAll('.tab-content').forEach(tab => tab.classList.add('hidden'));
  document.getElementById(tabName).classList.remove('hidden');
  document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
  event.target.classList.add('active');
}

function toggleCustomerDetails() {
  const select = document.getElementById('customerSelect');
  const details = document.getElementById('customerDetails');
  if (select.value === 'new') {
    details.style.display = 'block';
    document.getElementById('customerName').required = true;
    document.getElementById('customerPhone').required = true;
  } else {
    details.style.display = 'none';
    document.getElementById('customerName').required = false;
    document.getElementById('customerPhone').required = false;
  }
}

function toggleTableDetails() {
  const dineIn = document.getElementById('orderTypeDineIn').checked;
  document.getElementById('tableDetails').style.display = dineIn ? 'block' : 'none';
}

function updateStatus(orderId, status) {
  if (status) {
    window.location.href = `/update_status/${orderId}/${status}`;
  }
}

function filterOrders() {
  const status = document.getElementById('statusFilter').value;
  const type = document.getElementById('typeFilter').value;
  const url = new URL(window.location);
  url.searchParams.set('status', status);
  url.searchParams.set('order_type', type);
  window.location.href = url.toString();
}

function filterMenu() {
  const term = document.getElementById('menuSearch').value.toLowerCase();
  document.querySelectorAll('.menu-item-card').forEach(card => {
    const name = card.getAttribute('data-item-name');
    card.style.display = name.includes(term) ? 'block' : 'none';
  });
  
  // Hide/show category titles
  document.querySelectorAll('.menu-category').forEach(category => {
    const visibleItems = category.querySelectorAll('.menu-item-card[style="display: block;"]');
    const hasVisible = Array.from(category.querySelectorAll('.menu-item-card')).some(card => 
      card.style.display !== 'none'
    );
    category.style.display = hasVisible ? 'block' : 'none';
  });
}

function updateOrderSummary() {
  const checked = document.querySelectorAll('input[name="items"]:checked');
  const list = document.getElementById('selectedItemsList');
  const totalEl = document.getElementById('orderTotal');
  let total = 0;
  let html = '';

  if (checked.length === 0) {
    list.innerHTML = '<div style="color:#999; font-style:italic; text-align:center; padding:10px;">No items selected</div>';
    totalEl.textContent = '₹0.00';
    return;
  }

  checked.forEach(cb => {
    const card = cb.closest('.menu-item-card');
    const name = card.querySelector('.menu-item-name').textContent;
    const price = parseFloat(card.querySelector('.menu-item-price').textContent.replace('₹', ''));
    total += price;
    html += `<div style="display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #f0f0f0; align-items:center;">
      <span style="font-weight:500; color:#333;">${name}</span>
      <span style="color:#28a745; font-weight:700;">₹${price.toFixed(2)}</span>
    </div>`;
  });

  list.innerHTML = html;
  totalEl.textContent = `₹${total.toFixed(2)}`;
}

function resetForm() {
  document.getElementById('orderForm').reset();
  toggleCustomerDetails();
  toggleTableDetails();
  updateOrderSummary();
}

document.addEventListener('DOMContentLoaded', () => {
  toggleCustomerDetails();
  toggleTableDetails();
  updateOrderSummary();

  const form = document.getElementById('orderForm');
  if (form) {
    form.addEventListener('submit', e => {
      const items = document.querySelectorAll('input[name="items"]:checked').length;
      if (items === 0) {
        alert('Please select at least one item');
        e.preventDefault();
      }
    });
  }

  // Auto-hide flash with smoother animation
  setTimeout(() => {
    document.querySelectorAll('.flash-message').forEach(m => {
      m.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      m.style.opacity = '0';
      m.style.transform = 'translateY(-10px)';
      setTimeout(() => m.remove(), 500);
    });
  }, 5000);
});