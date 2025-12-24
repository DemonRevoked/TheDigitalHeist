let currentUser = null;
let currentView = 'list';
let userInvoices = [];

async function initApp() {
  // Check if user is already logged in
  try {
    const response = await fetch('/auth/current', {
      credentials: 'include'
    });
    if (response.ok) {
      const data = await response.json();
      if (data.user) {
        currentUser = data.user;
        showDashboard();
      }
    }
  } catch (e) {
    // Not logged in, show login
  }

  setupEventListeners();
  
  // Handle hash changes for invoice viewing
  window.addEventListener('hashchange', () => {
    if (currentUser && window.location.hash) {
      const invoiceId = parseInt(window.location.hash.substring(1));
      if (invoiceId) {
        currentView = 'detail';
        viewInvoice(invoiceId);
      }
    }
  });

  // Check if there's a hash on load
  if (currentUser && window.location.hash) {
    const invoiceId = parseInt(window.location.hash.substring(1));
    if (invoiceId) {
      currentView = 'detail';
      viewInvoice(invoiceId);
    }
  }
}

function setupEventListeners() {
  document.getElementById('login-btn').addEventListener('click', handleLogin);
  document.getElementById('logout-btn').addEventListener('click', handleLogout);
  document.getElementById('back-btn').addEventListener('click', () => {
    currentView = 'list';
    showInvoiceList();
    window.location.hash = '';
  });
  
  // Handle Enter key in password field
  document.getElementById('password').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      handleLogin();
    }
  });
}

async function handleLogin() {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;

  if (!username || !password) {
    showMessage('login-message', 'Please enter both username and password', 'error');
    return;
  }

  try {
    const response = await fetch('/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ username, password })
    });

    const data = await response.json();

    if (response.ok && data.success) {
      currentUser = data.user;
      showDashboard();
      clearMessage('login-message');
    } else {
      // Display error and hint if available (for SQL injection enumeration)
      const errorMsg = data.error || 'Invalid credentials';
      if (data.hint) {
        showMessage('login-message', `${errorMsg}\n${data.hint}`, 'error');
      } else {
        showMessage('login-message', errorMsg, 'error');
      }
    }
  } catch (error) {
    showMessage('login-message', 'Login failed. Please try again.', 'error');
  }
}

async function handleLogout() {
  try {
    await fetch('/auth/logout', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include'
    });
  } catch (e) {
    // Ignore errors
  }
  
  currentUser = null;
  currentView = 'list';
  document.getElementById('login-view').classList.remove('hidden');
  document.getElementById('dashboard-view').classList.add('hidden');
  document.getElementById('username').value = '';
  document.getElementById('password').value = '';
  clearMessage('login-message');
  window.location.hash = '';
}

async function showDashboard() {
  document.getElementById('login-view').classList.add('hidden');
  document.getElementById('dashboard-view').classList.remove('hidden');
  document.getElementById('user-welcome').textContent = `Welcome, ${currentUser.username}!`;
  document.getElementById('current-user').textContent = currentUser.username;
  document.getElementById('current-role').textContent = currentUser.role;
  
  showInvoiceList();
}

async function showInvoiceList() {
  document.getElementById('invoice-list-view').classList.remove('hidden');
  document.getElementById('invoice-detail-view').classList.add('hidden');
  document.getElementById('url-display').textContent = '/me';
  clearMessage('dashboard-message');
  
  try {
    const response = await fetch('/me?format=json', {
      credentials: 'include'
    });
    
    if (response.ok) {
      const data = await response.json();
      userInvoices = data.invoices || [];
      renderInvoiceList();
    } else {
      showMessage('dashboard-message', 'Failed to load invoices', 'error');
    }
  } catch (error) {
    showMessage('dashboard-message', 'Error loading invoices', 'error');
  }
}

function renderInvoiceList() {
  const container = document.getElementById('invoices-container');

  if (userInvoices.length === 0) {
    container.innerHTML = '<p style="color: #666; text-align: center;">No invoices found.</p>';
    return;
  }

  container.innerHTML = userInvoices.map(invoice => `
    <div class="invoice-item" data-id="${invoice.id}">
      <h4>Invoice #${invoice.id}</h4>
      <p><strong>Amount:</strong> ₹${invoice.amount}</p>
      <p><strong>Note:</strong> ${invoice.note.substring(0, 50)}${invoice.note.length > 50 ? '...' : ''}</p>
    </div>
  `).join('');

  container.querySelectorAll('.invoice-item').forEach(item => {
    item.addEventListener('click', () => {
      const invoiceId = parseInt(item.dataset.id);
      currentView = 'detail';
      viewInvoice(invoiceId);
    });
  });
}

async function viewInvoice(invoiceId) {
  try {
    const response = await fetch(`/invoices/${invoiceId}?format=json`, {
      credentials: 'include'
    });

    if (!response.ok) {
      showMessage('dashboard-message', 'Invoice not found', 'error');
      return;
    }

    const data = await response.json();
    const invoice = data.invoice;

    document.getElementById('invoice-list-view').classList.add('hidden');
    document.getElementById('invoice-detail-view').classList.remove('hidden');
    document.getElementById('url-display').textContent = `/invoices/${invoiceId}`;
    window.location.hash = invoiceId;

    const detailContainer = document.getElementById('invoice-detail-container');
    
    const isOwnedByUser = invoice.user_id === currentUser.id;
    const isAdmin = currentUser.role === 'admin';
    const isUnauthorizedAccess = !isOwnedByUser && !isAdmin;

    detailContainer.innerHTML = `
      <div class="invoice-detail">
        <h3>Invoice #${invoice.id}</h3>
        <div class="detail-row">
          <span class="label">Amount:</span>
          <span class="value">₹${invoice.amount}</span>
        </div>
        <div class="detail-row">
          <span class="label">Owner:</span>
          <span class="value">${invoice.owner}</span>
        </div>
        <div class="detail-row">
          <span class="label">Note:</span>
          <span class="value" style="text-align: left; word-break: break-word;">${invoice.note}</span>
        </div>
      </div>
    `;

    // Check if this is the flag invoice (ID 1057) and user doesn't own it
    if (invoice.id === 1057 && isUnauthorizedAccess) {
      // Extract flag and key from note (format: "Quarterly billing note: FLAG{...} | Key: <key>")
      const flagMatch = invoice.note.match(/FLAG\{[^}]+\}|TDHCTF\{[^}]+\}/);
      const keyMatch = invoice.note.match(/Key:\s*([^\s|]+)/);
      
      if (flagMatch || keyMatch) {
        let successHTML = `
          <div class="flag-found">
            <h3>🎉 Congratulations!</h3>
            <p>You've successfully exploited the IDOR vulnerability!</p>
        `;
        
        if (flagMatch) {
          successHTML += `<div style="margin: 10px 0;"><strong>FLAG:</strong><br><code>${flagMatch[0]}</code></div>`;
        }
        
        if (keyMatch) {
          successHTML += `<div style="margin: 10px 0;"><strong>CHALLENGE KEY:</strong><br><code>${keyMatch[1]}</code></div>`;
        }
        
        successHTML += `</div>`;
        detailContainer.innerHTML += successHTML;
      }
    }

    // Show security warning if accessing someone else's invoice
    if (isUnauthorizedAccess) {
      const hint = document.createElement('div');
      hint.className = 'hint-section';
      hint.innerHTML = `
        <h4>⚠️ Security Issue Detected!</h4>
        <p>You're viewing an invoice that doesn't belong to you.</p>
        <p>This is an <strong>IDOR (Insecure Direct Object Reference)</strong> vulnerability.</p>
        <p>The application failed to verify that you own this invoice before displaying it.</p>
      `;
      detailContainer.appendChild(hint);
    }
  } catch (error) {
    showMessage('dashboard-message', 'Error loading invoice', 'error');
  }
}

function showMessage(elementId, message, type) {
  const messageDiv = document.getElementById(elementId);
  messageDiv.className = type === 'error' ? 'error-message' : 'success-message';
  // Use innerHTML to support line breaks and better formatting
  messageDiv.innerHTML = message.replace(/\n/g, '<br>');
  messageDiv.classList.remove('hidden');
}

function clearMessage(elementId) {
  const messageDiv = document.getElementById(elementId);
  messageDiv.textContent = '';
  messageDiv.className = '';
}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}

