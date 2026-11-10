/**
 * MS College Campus Events - Main JavaScript
 * Handles UI interactions, animations, form helpers
 */

document.addEventListener('DOMContentLoaded', function () {

  // ── Navbar scroll glassmorphism ──
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.classList.toggle('scrolled', window.scrollY > 30);
    });
  }

  // ── Mobile hamburger / nav ──
  const hamburger = document.querySelector('.hamburger');
  const navbarNav  = document.querySelector('.navbar-nav');
  const sidebar    = document.querySelector('.sidebar');
  const sidebarOverlay = document.querySelector('.sidebar-overlay');

  if (hamburger) {
    hamburger.addEventListener('click', () => {
      hamburger.classList.toggle('active');
      if (navbarNav) navbarNav.classList.toggle('mobile-open');
      if (sidebar) {
        sidebar.classList.toggle('mobile-open');
        if (sidebarOverlay) sidebarOverlay.classList.toggle('active');
      }
    });
  }

  if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', () => {
      if (sidebar) sidebar.classList.remove('mobile-open');
      sidebarOverlay.classList.remove('active');
      if (hamburger) hamburger.classList.remove('active');
    });
  }

  // ── Flash messages auto-dismiss ──
  function dismissFlash(el) {
    el.classList.add('fade-out');
    setTimeout(() => el.remove(), 450);
  }

  document.querySelectorAll('.flash-message').forEach(msg => {
    const closeBtn = msg.querySelector('.flash-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => dismissFlash(msg));
    }
    setTimeout(() => {
      if (msg.isConnected) dismissFlash(msg);
    }, 4000);
  });

  // ── Active nav link detection ──
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-link, .sidebar-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && href !== '#' && currentPath.startsWith(href) && href !== '/') {
      link.classList.add('active');
    } else if (href === '/' && currentPath === '/') {
      link.classList.add('active');
    }
  });

  // ── Smooth scroll for anchor links ──
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ── File upload drag & drop ──
  document.querySelectorAll('.file-drop-zone').forEach(zone => {
    const input = zone.querySelector('input[type="file"]') ||
                  document.getElementById(zone.dataset.for);
    const fileInfo = zone.closest('.file-upload-wrapper')?.querySelector('.file-selected');

    if (!input) return;

    zone.addEventListener('click', () => input.click());

    zone.addEventListener('dragover', e => {
      e.preventDefault();
      zone.classList.add('drag-over');
    });

    zone.addEventListener('dragleave', () => {
      zone.classList.remove('drag-over');
    });

    zone.addEventListener('drop', e => {
      e.preventDefault();
      zone.classList.remove('drag-over');
      if (e.dataTransfer.files.length) {
        input.files = e.dataTransfer.files;
        showFileSelected(input, fileInfo, zone);
      }
    });

    input.addEventListener('change', () => {
      showFileSelected(input, fileInfo, zone);
    });
  });

  function showFileSelected(input, fileInfoEl, zone) {
    if (!input.files.length) return;
    const file = input.files[0];
    const sizeKB = (file.size / 1024).toFixed(1);
    const sizeMB = (file.size / 1024 / 1024).toFixed(2);
    const sizeStr = file.size > 1024 * 1024 ? `${sizeMB} MB` : `${sizeKB} KB`;

    if (fileInfoEl) {
      fileInfoEl.style.display = 'flex';
      const nameEl = fileInfoEl.querySelector('.file-name');
      if (nameEl) nameEl.textContent = `${file.name} (${sizeStr})`;
    } else {
      // Update zone text
      const dropText = zone.querySelector('.drop-text');
      if (dropText) {
        dropText.innerHTML = `<i class="fa-solid fa-file-check" style="color:var(--success)"></i> ${file.name} <span style="color:var(--text-muted)">(${sizeStr})</span>`;
      }
    }
  }

  // ── Image preview for banner/image inputs ──
  document.querySelectorAll('input[type="file"][data-preview]').forEach(input => {
    input.addEventListener('change', function () {
      const previewId = this.dataset.preview;
      const preview = document.getElementById(previewId);
      if (preview && this.files[0]) {
        const reader = new FileReader();
        reader.onload = e => {
          preview.src = e.target.result;
          preview.style.display = 'block';
        };
        reader.readAsDataURL(this.files[0]);
      }
    });
  });

  // ── Number counter animation for stats ──
  function animateCounter(el) {
    const target = parseInt(el.dataset.target || el.textContent, 10);
    if (isNaN(target)) return;
    const duration = 1200;
    const start    = performance.now();

    function update(now) {
      const elapsed  = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased    = 1 - Math.pow(1 - progress, 3); // easeOutCubic
      el.textContent = Math.round(eased * target);
      if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
  }

  const counterObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        counterObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  document.querySelectorAll('.stat-number[data-target], .counter-number').forEach(el => {
    counterObserver.observe(el);
  });

  // ── Reveal on scroll ──
  const revealObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

  // ── Confirmation dialogs for delete ──
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', function (e) {
      const msg = this.dataset.confirm || 'Are you sure?';
      if (!confirm(msg)) {
        e.preventDefault();
        e.stopImmediatePropagation();
      }
    });
  });

  // ── Loading button state ──
  document.querySelectorAll('form[data-loading]').forEach(form => {
    form.addEventListener('submit', function () {
      const btn = this.querySelector('[type="submit"]');
      if (btn) {
        btn.classList.add('loading');
        btn.disabled = true;
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
        // Re-enable after 15s as fallback
        setTimeout(() => {
          btn.classList.remove('loading');
          btn.disabled = false;
          btn.innerHTML = originalText;
        }, 15000);
      }
    });
  });

  // ── Copy to clipboard ──
  window.copyToClipboard = function (text, btn) {
    navigator.clipboard.writeText(text).then(() => {
      const originalText = btn ? btn.innerHTML : '';
      if (btn) {
        btn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
        setTimeout(() => {
          btn.innerHTML = originalText;
        }, 2000);
      }
    });
  };

  document.querySelectorAll('[data-copy]').forEach(btn => {
    btn.addEventListener('click', function () {
      copyToClipboard(this.dataset.copy, this);
    });
  });

  // ── Filter tabs (event type filter on index page) ──
  document.querySelectorAll('.filter-tab').forEach(tab => {
    tab.addEventListener('click', function () {
      document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
      this.classList.add('active');

      const filter = this.dataset.filter;
      document.querySelectorAll('.event-card').forEach(card => {
        if (filter === 'all' || card.dataset.type === filter) {
          card.style.display = '';
          card.classList.add('animate-fadeInUp');
        } else {
          card.style.display = 'none';
        }
      });

      // Show empty state if nothing visible
      const visible = document.querySelectorAll('.event-card[style=""]').length +
                      document.querySelectorAll('.event-card:not([style])').length;
      const emptyState = document.querySelector('.events-empty-state');
      if (emptyState) {
        emptyState.style.display = visible === 0 ? 'block' : 'none';
      }
    });
  });

  // ── Search box live filter ──
  const searchInput = document.getElementById('tableSearch');
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      const q = this.value.toLowerCase();
      document.querySelectorAll('tbody tr[data-searchable]').forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  }

  // ── Tab switching ──
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const tabGroup = this.closest('[data-tab-group]')?.dataset.tabGroup ||
                       this.dataset.tabGroup;
      const target   = this.dataset.tab;

      document.querySelectorAll(`.tab-btn[data-tab-group="${tabGroup}"], .tab-btn`)
        .forEach(b => {
          if (b.closest('[data-tab-group]')?.dataset.tabGroup === tabGroup ||
              b.dataset.tabGroup === tabGroup) {
            b.classList.remove('active');
          }
        });

      this.classList.add('active');
      document.querySelectorAll(`.tab-content`).forEach(c => {
        if (c.dataset.tab === target) {
          c.classList.add('active');
        } else if (c.dataset.tabGroup === tabGroup || tabGroup) {
          c.classList.remove('active');
        }
      });
    });
  });

  // ── Dynamic team members form ──
  const addMemberBtn   = document.getElementById('addMemberBtn');
  const membersTable   = document.getElementById('membersTableBody');
  const maxMembersInput = document.getElementById('maxMembers');

  if (addMemberBtn && membersTable) {
    let memberCount = parseInt(membersTable.querySelectorAll('tr.added-member').length) || 0;

    addMemberBtn.addEventListener('click', function () {
      const max = maxMembersInput ? parseInt(maxMembersInput.value) : 6;
      const current = membersTable.querySelectorAll('tr').length;
      if (current >= max) {
        showToast(`Maximum ${max} members allowed`, 'warning');
        return;
      }
      memberCount++;
      const idx = memberCount;
      const row = document.createElement('tr');
      row.className = 'added-member animate-fadeInUp';
      row.innerHTML = `
        <td>${current + 1}</td>
        <td><input type="text"   class="form-control form-control-sm" name="member_name_${idx}"   placeholder="Full Name" required></td>
        <td><input type="text"   class="form-control form-control-sm" name="member_roll_${idx}"   placeholder="Roll No"   required></td>
        <td><input type="text"   class="form-control form-control-sm" name="member_dept_${idx}"   placeholder="Dept"      required></td>
        <td><input type="text"   class="form-control form-control-sm" name="member_section_${idx}" placeholder="Sec"      required></td>
        <td><button type="button" class="btn btn-danger btn-sm remove-member-btn">
              <i class="fa-solid fa-times"></i>
            </button></td>
      `;
      membersTable.appendChild(row);

      row.querySelector('.remove-member-btn').addEventListener('click', function () {
        row.classList.add('animate-shake');
        setTimeout(() => row.remove(), 300);
      });
    });
  }

  // ── Attendance toggle buttons ──
  document.querySelectorAll('.attendance-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const registrationId = this.dataset.id;
      const currentStatus  = this.dataset.status;
      const newStatus      = currentStatus === 'present' ? 'absent' :
                             currentStatus === 'absent'  ? 'present' : 'present';

      this.disabled = true;
      this.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';

      fetch('/staff/attendance/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ registration_id: registrationId, status: newStatus })
      })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          this.dataset.status = newStatus;
          this.className = `attendance-btn ${newStatus}`;
          this.innerHTML = newStatus === 'present'
            ? '<i class="fa-solid fa-check"></i> Present'
            : '<i class="fa-solid fa-times"></i> Absent';
        } else {
          this.innerHTML = currentStatus === 'present' ? '<i class="fa-solid fa-check"></i> Present'
                                                        : '<i class="fa-solid fa-times"></i> Absent';
          showToast(data.message || 'Error updating attendance', 'danger');
        }
        this.disabled = false;
      })
      .catch(() => {
        this.disabled = false;
        this.innerHTML = 'Error';
        showToast('Network error. Please try again.', 'danger');
      });
    });
  });

  // ── Publish toggle ──
  document.querySelectorAll('.publish-toggle').forEach(toggle => {
    toggle.addEventListener('change', function () {
      const eventId  = this.dataset.event;
      const published = this.checked;

      fetch(`/admin/event/${eventId}/publish`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ published })
      })
      .then(r => r.json())
      .then(data => {
        showToast(
          data.success ? (published ? 'Event published!' : 'Event unpublished.') : (data.message || 'Error'),
          data.success ? 'success' : 'danger'
        );
        if (!data.success) this.checked = !published;
      })
      .catch(() => {
        this.checked = !published;
        showToast('Network error.', 'danger');
      });
    });
  });

  // ── Bulk select checkboxes ──
  const selectAll = document.getElementById('selectAll');
  if (selectAll) {
    selectAll.addEventListener('change', function () {
      document.querySelectorAll('.row-checkbox').forEach(cb => {
        cb.checked = this.checked;
      });
      updateBulkActions();
    });

    document.querySelectorAll('.row-checkbox').forEach(cb => {
      cb.addEventListener('change', updateBulkActions);
    });
  }

  function updateBulkActions() {
    const selected = document.querySelectorAll('.row-checkbox:checked').length;
    const bulkBar  = document.querySelector('.bulk-actions');
    if (bulkBar) {
      const countEl = bulkBar.querySelector('.selected-count');
      if (countEl) countEl.textContent = `${selected} selected`;
      bulkBar.style.display = selected > 0 ? 'flex' : 'none';
    }
    const bulkBtn = document.getElementById('issueCertificatesBtn');
    if (bulkBtn) bulkBtn.disabled = selected === 0;
  }

  // ── Issue certificates bulk ──
  const issueCertBtn = document.getElementById('issueCertificatesBtn');
  if (issueCertBtn) {
    issueCertBtn.addEventListener('click', function () {
      const selected = Array.from(document.querySelectorAll('.row-checkbox:checked'))
                            .map(cb => cb.value);
      if (!selected.length) return;
      if (!confirm(`Issue certificates to ${selected.length} participant(s)?`)) return;

      this.classList.add('loading');
      this.disabled = true;

      fetch('/admin/certificates/issue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ registration_ids: selected })
      })
      .then(r => r.json())
      .then(data => {
        showToast(data.message || 'Certificates issued!', data.success ? 'success' : 'danger');
        if (data.success) setTimeout(() => location.reload(), 1500);
      })
      .catch(() => showToast('Network error.', 'danger'))
      .finally(() => {
        this.classList.remove('loading');
        this.disabled = false;
      });
    });
  }

  // ── Multi-step create event form ──
  const stepForm    = document.getElementById('createEventForm');
  const stepPanels  = document.querySelectorAll('.step-panel');
  const nextBtns    = document.querySelectorAll('.step-next');
  const prevBtns    = document.querySelectorAll('.step-prev');
  const stepIndicators = document.querySelectorAll('.step-indicator');
  let currentStep = 0;

  function goToStep(step) {
    stepPanels.forEach((p, i) => p.classList.toggle('active', i === step));
    stepIndicators.forEach((ind, i) => {
      ind.classList.toggle('active', i === step);
      ind.classList.toggle('completed', i < step);
    });
    currentStep = step;
  }

  nextBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      if (currentStep < stepPanels.length - 1) goToStep(currentStep + 1);
    });
  });

  prevBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      if (currentStep > 0) goToStep(currentStep - 1);
    });
  });

  // Show/hide step 3 based on event type
  document.querySelectorAll('input[name="event_type"]').forEach(radio => {
    radio.addEventListener('change', function () {
      const step3Indicator = document.getElementById('step3Indicator');
      const isSymposium    = this.value === 'symposium';
      if (step3Indicator) step3Indicator.style.display = isSymposium ? '' : 'none';

      // Update event type card UI
      document.querySelectorAll('.event-type-card').forEach(card => {
        card.classList.toggle('selected', card.dataset.type === this.value);
      });
    });
  });

  document.querySelectorAll('.event-type-card').forEach(card => {
    card.addEventListener('click', function () {
      const radio = this.querySelector('input[type="radio"]');
      if (radio) radio.click();
    });
  });

  // ── Add sub-event row ──
  const addSubEventBtn = document.getElementById('addSubEventBtn');
  const subEventsContainer = document.getElementById('subEventsContainer');
  let subEventCount = 1;

  if (addSubEventBtn && subEventsContainer) {
    addSubEventBtn.addEventListener('click', function () {
      subEventCount++;
      const div = document.createElement('div');
      div.className = 'card mb-16 animate-fadeInUp sub-event-entry';
      div.innerHTML = `
        <div class="d-flex justify-between align-center mb-16">
          <h4 class="card-title">Sub-event ${subEventCount}</h4>
          <button type="button" class="btn btn-ghost btn-sm remove-subevent">
            <i class="fa-solid fa-trash"></i> Remove
          </button>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Sub-event Name <span class="required">*</span></label>
            <input type="text" class="form-control" name="sub_name_${subEventCount}" required>
          </div>
          <div class="form-group">
            <label class="form-label">Allowed Teams</label>
            <input type="number" class="form-control" name="sub_teams_${subEventCount}" min="1" value="10">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Min Team Size</label>
            <input type="number" class="form-control" name="sub_min_${subEventCount}" min="1" value="1">
          </div>
          <div class="form-group">
            <label class="form-label">Max Team Size</label>
            <input type="number" class="form-control" name="sub_max_${subEventCount}" min="1" value="4">
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Description</label>
          <textarea class="form-control" name="sub_desc_${subEventCount}" rows="2"></textarea>
        </div>
      `;
      subEventsContainer.appendChild(div);
      div.querySelector('.remove-subevent')?.addEventListener('click', () => {
        div.classList.add('animate-shake');
        setTimeout(() => div.remove(), 300);
      });
    });
  }

  // ── Toast notification utility ──
  window.showToast = function (message, type = 'info') {
    const icons = {
      success: 'fa-circle-check',
      danger:  'fa-circle-xmark',
      warning: 'fa-triangle-exclamation',
      info:    'fa-circle-info',
    };
    const container = document.querySelector('.flash-container') ||
                      (() => {
                        const c = document.createElement('div');
                        c.className = 'flash-container';
                        document.body.appendChild(c);
                        return c;
                      })();

    const flash = document.createElement('div');
    flash.className = `flash-message ${type}`;
    flash.innerHTML = `
      <i class="fa-solid ${icons[type] || icons.info} flash-icon"></i>
      <span class="flash-text">${message}</span>
      <button class="flash-close"><i class="fa-solid fa-xmark"></i></button>
    `;
    container.appendChild(flash);
    flash.querySelector('.flash-close').addEventListener('click', () => dismissFlash(flash));
    setTimeout(() => { if (flash.isConnected) dismissFlash(flash); }, 4000);
  };

  // ── Tooltips ──
  document.querySelectorAll('[data-tooltip]').forEach(el => {
    // CSS-only tooltips defined in style.css — no JS needed unless complex
  });

  // ── Password visibility toggle ──
  document.querySelectorAll('.toggle-password').forEach(btn => {
    btn.addEventListener('click', function () {
      const input = document.getElementById(this.dataset.target);
      if (!input) return;
      const isText = input.type === 'text';
      input.type = isText ? 'password' : 'text';
      this.querySelector('i')?.classList.toggle('fa-eye', isText);
      this.querySelector('i')?.classList.toggle('fa-eye-slash', !isText);
    });
  });

  // ── Password strength indicator ──
  const passwordInput = document.getElementById('password');
  const strengthBar   = document.getElementById('passwordStrength');
  if (passwordInput && strengthBar) {
    passwordInput.addEventListener('input', function () {
      const val = this.value;
      let strength = 0;
      if (val.length >= 8)                     strength++;
      if (/[A-Z]/.test(val))                   strength++;
      if (/[0-9]/.test(val))                   strength++;
      if (/[^A-Za-z0-9]/.test(val))           strength++;

      const colors  = ['#e63946', '#f39c12', '#3498db', '#2ecc71'];
      const widths  = ['25%', '50%', '75%', '100%'];
      const labels  = ['Weak', 'Fair', 'Good', 'Strong'];

      if (val.length === 0) {
        strengthBar.style.display = 'none';
      } else {
        strengthBar.style.display = 'block';
        const bar  = strengthBar.querySelector('.strength-fill');
        const text = strengthBar.querySelector('.strength-text');
        if (bar)  { bar.style.width = widths[strength - 1] || '0%'; bar.style.background = colors[strength - 1] || '#e63946'; }
        if (text)  text.textContent = labels[strength - 1] || '';
      }
    });
  }

  // ── Confirm password match ──
  const confirmPwInput = document.getElementById('confirm_password');
  if (confirmPwInput && passwordInput) {
    confirmPwInput.addEventListener('input', function () {
      if (this.value && this.value !== passwordInput.value) {
        this.classList.add('is-invalid');
        let err = this.nextElementSibling;
        if (!err || !err.classList.contains('form-error')) {
          err = document.createElement('span');
          err.className = 'form-error';
          err.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> Passwords do not match';
          this.parentNode.insertBefore(err, this.nextSibling);
        }
      } else {
        this.classList.remove('is-invalid');
        const err = this.nextElementSibling;
        if (err && err.classList.contains('form-error')) err.remove();
      }
    });
  }

  // ── Sub-event radio selection highlight ──
  document.querySelectorAll('.sub-event-option').forEach(option => {
    option.addEventListener('click', function () {
      document.querySelectorAll('.sub-event-option').forEach(o => o.classList.remove('selected'));
      this.classList.add('selected');
      const max = this.dataset.maxTeam;
      if (max && maxMembersInput) maxMembersInput.value = max;
    });
  });

  // ── Mobile: close nav on link click ──
  document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
    link.addEventListener('click', () => {
      if (navbarNav) navbarNav.classList.remove('mobile-open');
      if (hamburger) hamburger.classList.remove('active');
    });
  });

  // ── Page load animation ──
  document.body.classList.add('page-enter');

}); // end DOMContentLoaded
