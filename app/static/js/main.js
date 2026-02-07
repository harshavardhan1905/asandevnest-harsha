// Asan DevNest - Main JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Mobile menu toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function () {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Auto-hide flash messages
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function (message) {
        setTimeout(function () {
            message.style.opacity = '0';
            message.style.transform = 'translateX(100px)';
            setTimeout(function () {
                message.remove();
            }, 300);
        }, 5000);
    });

    // Sidebar toggle for mobile
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('open');
        });
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Search functionality
    const searchInput = document.getElementById('global-search');
    const searchResults = document.getElementById('search-results');

    if (searchInput && searchResults) {
        let searchTimeout;

        searchInput.addEventListener('input', function () {
            clearTimeout(searchTimeout);
            const query = this.value.trim();

            if (query.length < 2) {
                searchResults.classList.add('hidden');
                return;
            }

            searchTimeout = setTimeout(function () {
                fetch(`/api/search?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        displaySearchResults(data);
                    })
                    .catch(error => console.error('Search error:', error));
            }, 300);
        });

        // Close search results when clicking outside
        document.addEventListener('click', function (e) {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.classList.add('hidden');
            }
        });
    }

    function displaySearchResults(data) {
        if (!searchResults) return;

        let html = '';

        if (data.developers && data.developers.length > 0) {
            html += '<div class="p-2"><h4 class="text-xs font-semibold text-slate-500 uppercase mb-2">Developers</h4>';
            data.developers.forEach(dev => {
                html += `
                    <a href="/developer/${dev.id}" class="block px-3 py-2 rounded-lg hover:bg-slate-100 transition">
                        <div class="font-medium text-slate-900">${dev.name}</div>
                        <div class="text-sm text-slate-500">${dev.tagline || ''}</div>
                    </a>
                `;
            });
            html += '</div>';
        }

        if (data.articles && data.articles.length > 0) {
            html += '<div class="p-2 border-t"><h4 class="text-xs font-semibold text-slate-500 uppercase mb-2">Articles</h4>';
            data.articles.forEach(article => {
                html += `
                    <a href="/community/article/${article.slug}" class="block px-3 py-2 rounded-lg hover:bg-slate-100 transition">
                        <div class="font-medium text-slate-900">${article.title}</div>
                        <div class="text-sm text-slate-500">${article.excerpt}</div>
                    </a>
                `;
            });
            html += '</div>';
        }

        if (!html) {
            html = '<div class="p-4 text-center text-slate-500">No results found</div>';
        }

        searchResults.innerHTML = html;
        searchResults.classList.remove('hidden');
    }

    // Form validation
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('border-red-500');

                    // Remove error class on input
                    field.addEventListener('input', function () {
                        this.classList.remove('border-red-500');
                    }, { once: true });
                }
            });

            if (!isValid) {
                e.preventDefault();
                showNotification('Please fill in all required fields', 'error');
            }
        });
    });

    // Notification helper
    window.showNotification = function (message, type = 'info') {
        const container = document.getElementById('flash-messages') || createFlashContainer();

        const colors = {
            success: 'bg-emerald-50/90 border-emerald-200 text-emerald-800',
            error: 'bg-red-50/90 border-red-200 text-red-800',
            warning: 'bg-amber-50/90 border-amber-200 text-amber-800',
            info: 'bg-blue-50/90 border-blue-200 text-blue-800'
        };

        const notification = document.createElement('div');
        notification.className = `flash-message px-6 py-4 rounded-xl shadow-xl backdrop-blur-lg border ${colors[type]} animate-slide-in`;
        notification.innerHTML = `
            <div class="flex items-center justify-between">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-4 opacity-50 hover:opacity-100">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        `;

        container.appendChild(notification);

        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100px)';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    };

    function createFlashContainer() {
        const container = document.createElement('div');
        container.id = 'flash-messages';
        container.className = 'fixed top-20 right-4 z-50 space-y-2';
        document.body.appendChild(container);
        return container;
    }

    // Animate elements on scroll
    const animateOnScroll = document.querySelectorAll('[data-animate]');

    if (animateOnScroll.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        animateOnScroll.forEach(el => {
            el.style.opacity = '0';
            observer.observe(el);
        });
    }

    // Tab functionality
    const tabButtons = document.querySelectorAll('[data-tab-btn]');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            const tabGroup = this.closest('[data-tab-group]');
            const targetId = this.dataset.tabBtn;

            // Update buttons
            tabGroup.querySelectorAll('[data-tab-btn]').forEach(b => {
                b.classList.remove('border-primary-500', 'text-primary-600');
                b.classList.add('border-transparent', 'text-slate-500');
            });
            this.classList.remove('border-transparent', 'text-slate-500');
            this.classList.add('border-primary-500', 'text-primary-600');

            // Update panels
            tabGroup.querySelectorAll('[data-tab-panel]').forEach(panel => {
                panel.classList.add('hidden');
            });
            tabGroup.querySelector(`[data-tab-panel="${targetId}"]`).classList.remove('hidden');
        });
    });

    // File input preview
    const fileInputs = document.querySelectorAll('input[type="file"][data-preview]');

    fileInputs.forEach(input => {
        input.addEventListener('change', function () {
            const previewId = this.dataset.preview;
            const preview = document.getElementById(previewId);

            if (preview && this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    preview.src = e.target.result;
                    preview.classList.remove('hidden');
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    });

    // Counter animation
    const counters = document.querySelectorAll('[data-counter]');

    counters.forEach(counter => {
        const target = parseInt(counter.dataset.counter);
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;

        const updateCounter = () => {
            current += step;
            if (current < target) {
                counter.textContent = Math.floor(current);
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target;
            }
        };

        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                updateCounter();
                observer.unobserve(counter);
            }
        });

        observer.observe(counter);
    });
});
