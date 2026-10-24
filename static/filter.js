document.addEventListener('DOMContentLoaded', () => {
    // 1. Dark Mode Toggle
    const themeToggle = document.getElementById('themeToggle');
    const html = document.documentElement;

    // Check system preference first
    if (localStorage.getItem('theme')) {
        html.setAttribute('data-theme', localStorage.getItem('theme'));
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        html.setAttribute('data-theme', 'dark');
    }

    themeToggle.addEventListener('click', () => {
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });

    // 2. Category Filtering
    const filterBtns = document.querySelectorAll('.filter-btn');
    const headlineCards = document.querySelectorAll('.headline-card');
    const listItems = document.querySelectorAll('.list-item');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all
            filterBtns.forEach(b => b.classList.remove('active'));
            // Add active to current
            btn.classList.add('active');

            const category = btn.getAttribute('data-category');

            filterItems(category, headlineCards);
            filterItems(category, listItems);

            // Smooth scroll to top content
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    });

    function filterItems(category, items) {
        items.forEach(item => {
            const itemCat = item.getAttribute('data-category');
            if (category === 'all' || itemCat === category) {
                item.style.display = ''; // Restore to default (flex/grid)
                // Trigger reflow for animation
                setTimeout(() => item.style.opacity = '1', 10);
            } else {
                item.style.display = 'none';
                item.style.opacity = '0';
            }
        });
    }

    // 3. Back to Top Button
    const backToTopBtn = document.getElementById('backToTop');

    window.addEventListener('scroll', () => {
        if (window.scrollY > 500) {
            backToTopBtn.classList.add('visible');
        } else {
            backToTopBtn.classList.remove('visible');
        }
    });

    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});
