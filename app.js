/**
 * AI EDU IDEAS - Main Application Script
 * Handles data loading, filtering, and interactive UI
 */

document.addEventListener('DOMContentLoaded', () => {
    // State management
    let ideas = [];
    let filteredIdeas = [];
    let activeCategory = 'all';
    let selectedTags = new Set();
    let searchQuery = '';

    // Constants
    // Modality Tag Icons/Emoji colors
    const MODALITY_STYLES = {
        'Visual': 'text-cyan-400 bg-cyan-400/10 border-cyan-400/20',
        'Textual': 'text-amber-400 bg-amber-400/10 border-amber-400/20',
        'Conversational': 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20',
        'Functional': 'text-rose-400 bg-rose-400/10 border-rose-400/20'
    };

    // Normalized tag mapping - maps raw context phrases to clean tags
    const TAG_NORMALIZATION = {
        'higher education': 'Higher Education',
        'education': 'Education',
        'professional development': 'Professional Development',
        'k-12': 'K-12',
        'k12': 'K-12',
        'students': 'Students',
        'formative assessment': 'Formative Assessment',
        'summative assessment': 'Summative Assessment',
        'assessment': 'Assessment',
        'research': 'Research',
        'any discipline': 'Any Discipline',
        'secondary': 'Secondary Education',
        'foundation year': 'Foundation Year',
        'year 1': 'Year 1',
        'undergraduate': 'Undergraduate',
        'postgraduate': 'Postgraduate'
    };

    // DOM Elements
    const ideasGrid = document.getElementById('ideasGrid');
    const tagContainer = document.getElementById('tagContainer');
    const searchInput = document.getElementById('searchInput');
    const mobileSearchInput = document.getElementById('mobileSearchInput');
    const categoryTabs = document.querySelectorAll('.category-tab');
    const clearFiltersBtn = document.getElementById('clearFilters');
    const emptyState = document.getElementById('emptyState');

    // Modal Elements
    const modal = document.getElementById('modal');
    const modalBackdrop = document.getElementById('modalBackdrop');
    const closeModalBtn = document.getElementById('closeModal');

    /**
     * Normalizes context string into clean, short tags
     */
    function parseContextTags(contextStr) {
        if (!contextStr) return [];

        const tags = new Set();
        const lowerContext = contextStr.toLowerCase();

        // Check for known tag patterns
        for (const [pattern, normalizedTag] of Object.entries(TAG_NORMALIZATION)) {
            if (lowerContext.includes(pattern)) {
                tags.add(normalizedTag);
            }
        }

        // If no tags found, try splitting by comma but only keep short phrases (< 30 chars)
        if (tags.size === 0) {
            const parts = contextStr.split(',').map(t => t.trim()).filter(t => t && t.length < 30);
            parts.forEach(p => tags.add(p));
        }

        return Array.from(tags);
    }

    // Initialization
    async function init() {
        try {
            const response = await fetch('data/ideas.json');
            ideas = await response.json();

            // Format ideas with categories and parsed tags
            ideas = ideas.map(idea => {
                const contextTags = parseContextTags(idea.context);
                return {
                    ...idea,
                    category: idea.theme || 'Teaching Support',
                    contextTags: contextTags,
                    modalityTags: idea.tags || []
                };
            });

            renderTags();
            filterAndRender();
            lucide.createIcons();
        } catch (error) {
            console.error('Error loading ideas:', error);
            ideasGrid.innerHTML = `<div class="col-span-full py-20 text-center text-red-400">Error loading database. Please check if data/ideas.json exists.</div>`;
        }
    }

    /**
     * Renders all unique context tags (limited to top tags for usability)
     */
    function renderTags() {
        // Count tag frequency
        const tagCounts = {};
        ideas.forEach(idea => {
            idea.contextTags.forEach(tag => {
                tagCounts[tag] = (tagCounts[tag] || 0) + 1;
            });
        });

        // Sort by frequency and take top 15
        const sortedTags = Object.entries(tagCounts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 15)
            .map(([tag]) => tag);

        tagContainer.innerHTML = '';
        sortedTags.forEach(tag => {
            const btn = document.createElement('button');
            btn.className = 'context-tag';
            btn.textContent = tag;
            btn.onclick = () => toggleTag(tag, btn);
            tagContainer.appendChild(btn);
        });
    }

    /**
     * Toggles a tag in the filter set
     */
    function toggleTag(tag, element) {
        if (selectedTags.has(tag)) {
            selectedTags.delete(tag);
            element.classList.remove('selected');
        } else {
            selectedTags.add(tag);
            element.classList.add('selected');
        }
        updateClearFiltersBtn();
        filterAndRender();
    }

    /**
     * Updates visibility of the "Clear all filters" button and counter
     */
    function updateClearFiltersBtn() {
        if (selectedTags.size > 0 || activeCategory !== 'all' || searchQuery.length > 0) {
            clearFiltersBtn.classList.remove('hidden');
        } else {
            clearFiltersBtn.classList.add('hidden');
        }
    }

    /**
     * Updates the idea count in the header
     */
    function updateCounter() {
        const counterEl = document.getElementById('ideaCounter');
        if (counterEl) {
            counterEl.textContent = `${filteredIdeas.length} IDEAS`;
        }
    }

    /**
     * Filters ideas based on current state and renders them
     */
    function filterAndRender() {
        filteredIdeas = ideas.filter(idea => {
            // Category filter
            const matchesCategory = activeCategory === 'all' || idea.category === activeCategory;

            // Tag filter (Any match - OR logic)
            const matchesTags = selectedTags.size === 0 ||
                Array.from(selectedTags).some(tag => idea.contextTags.includes(tag));

            // Search filter
            const searchStr = (idea.title + ' ' + idea.author + ' ' + idea.my_idea).toLowerCase();
            const matchesSearch = !searchQuery || searchStr.includes(searchQuery.toLowerCase());

            return matchesCategory && matchesTags && matchesSearch;
        });

        updateCounter();
        renderGrid();
    }

    /**
     * Renders the grid of cards
     */
    function renderGrid() {
        ideasGrid.innerHTML = '';

        if (filteredIdeas.length === 0) {
            emptyState.classList.remove('hidden');
            return;
        }

        emptyState.classList.add('hidden');

        filteredIdeas.forEach((idea, index) => {
            const card = document.createElement('div');
            card.className = 'idea-card group cursor-pointer animate-slide-up';
            card.style.animationDelay = `${(index % 9) * 0.05}s`;

            const initials = idea.author ? idea.author.split(' ').map(n => n[0]).join('').substring(0, 2) : 'AI';

            // Build context tag badges (max 2)
            const tagBadges = idea.contextTags.slice(0, 2).map(tag =>
                `<span class="text-[9px] px-2 py-0.5 bg-violet-500/10 border border-violet-500/20 rounded-md text-violet-400/80">${tag}</span>`
            ).join('');

            // Build modality tag badges
            const modalityBadges = idea.modalityTags.map(tag => {
                const style = MODALITY_STYLES[tag] || 'bg-white/5 border-white/10 text-white/40';
                return `<span class="text-[8px] uppercase tracking-wider font-bold px-1.5 py-0.5 rounded-sm border ${style}">${tag}</span>`;
            }).join('');

            card.innerHTML = `
                <div class="idea-card-inner">
                    <div class="flex items-center justify-between mb-4">
                        <span class="text-xs font-black text-white/20 italic tracking-tighter group-hover:text-violet-500/50 transition-colors">#${idea.idea_number}</span>
                        <div class="flex gap-1 items-center">
                            ${modalityBadges}
                        </div>
                    </div>
                    
                    <h3 class="text-lg font-bold mb-2 leading-tight group-hover:text-violet-400 transition-colors line-clamp-2">${idea.title}</h3>
                    <p class="text-white/40 text-sm mb-4 line-clamp-3 leading-relaxed">${idea.my_idea}</p>
                    
                    <!-- Context Tag Badges -->
                    <div class="flex flex-wrap gap-1 mb-4">
                        ${tagBadges}
                    </div>
                    
                    <div class="mt-auto flex items-center justify-between pt-4 border-t border-white/5">
                        <div class="flex items-center gap-2">
                            <div class="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-[10px] font-bold text-white/60 group-hover:bg-violet-500/20 group-hover:text-violet-400 transition-all">
                                ${initials}
                            </div>
                            <div class="flex flex-col">
                                <span class="text-xs font-semibold text-white/80">${idea.author || 'Anonymous'}</span>
                                <span class="text-[10px] text-white/30 truncate max-w-[120px]">${idea.institution_organisation || ''}</span>
                            </div>
                        </div>
                        <i data-lucide="arrow-right" class="w-4 h-4 text-white/20 group-hover:text-violet-400 group-hover:translate-x-1 transition-all"></i>
                    </div>
                </div>
            `;

            card.onclick = () => openModal(idea);
            ideasGrid.appendChild(card);
        });

        lucide.createIcons();
    }

    /**
     * Modal Operations
     */
    function openModal(idea) {
        document.getElementById('modalNumber').textContent = `#${idea.idea_number}`;
        document.getElementById('modalTitle').textContent = idea.title;
        document.getElementById('modalAuthor').textContent = idea.author || 'Anonymous';
        document.getElementById('modalInstitution').textContent = idea.institution_organisation || '';
        document.getElementById('modalRole').textContent = idea.role || 'Contributor';
        document.getElementById('modalIdea').textContent = idea.my_idea;
        document.getElementById('modalAim').textContent = idea.what_i_aim_to_achieve;
        document.getElementById('modalInspiration').textContent = idea.where_the_inspiration_comes_from;
        document.getElementById('modalToolsUsed').textContent = `Tools: ${idea.tools_used || 'N/A'}`;

        const initials = idea.author ? idea.author.split(' ').map(n => n[0]).join('').substring(0, 2) : 'AI';
        document.getElementById('modalAvatar').textContent = initials;

        const tagsContainer = document.getElementById('modalTags');
        tagsContainer.innerHTML = '';

        // Add Category tag
        const catBadge = document.createElement('span');
        catBadge.className = 'px-3 py-1 bg-violet-500/20 border border-violet-500/30 text-violet-400 rounded-full text-xs font-bold uppercase tracking-wider';
        catBadge.textContent = idea.category;
        tagsContainer.appendChild(catBadge);

        // Add Context tags
        idea.contextTags.forEach(tag => {
            const badge = document.createElement('span');
            badge.className = 'px-3 py-1 bg-white/5 border border-white/10 text-white/60 rounded-full text-xs';
            badge.textContent = tag;
            tagsContainer.appendChild(badge);
        });

        // Add Modality tags
        idea.modalityTags.forEach(tag => {
            const style = MODALITY_STYLES[tag] || 'bg-white/5 border-white/10 text-white/40';
            const badge = document.createElement('span');
            badge.className = `px-3 py-1 ${style} rounded-full text-xs font-bold uppercase tracking-wider`;
            badge.textContent = tag;
            tagsContainer.appendChild(badge);
        });

        const contactLink = document.getElementById('modalContact');
        if (idea.contact_details && idea.contact_details.includes('@')) {
            contactLink.href = `mailto:${idea.contact_details}`;
            contactLink.classList.remove('hidden');
        } else {
            contactLink.classList.add('hidden');
        }

        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        lucide.createIcons();
    }

    function closeModal() {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }

    // Event Listeners
    searchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value;
        updateClearFiltersBtn();
        filterAndRender();
    });

    mobileSearchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value;
        updateClearFiltersBtn();
        filterAndRender();
    });

    categoryTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            categoryTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            activeCategory = tab.dataset.category;
            updateClearFiltersBtn();
            filterAndRender();
        });
    });

    clearFiltersBtn.onclick = () => {
        selectedTags.clear();
        activeCategory = 'all';
        searchQuery = '';
        searchInput.value = '';
        mobileSearchInput.value = '';
        categoryTabs.forEach(t => t.classList.remove('active'));
        categoryTabs[0].classList.add('active');
        document.querySelectorAll('.context-tag').forEach(t => t.classList.remove('selected'));
        updateClearFiltersBtn();
        filterAndRender();
    };

    closeModalBtn.onclick = closeModal;
    modalBackdrop.onclick = closeModal;

    // Keyboard support
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });

    // Mobile Search Toggle
    const mobileSearchBtn = document.getElementById('mobileSearchBtn');
    const mobileSearchContainer = document.getElementById('mobileSearchContainer');

    mobileSearchBtn.addEventListener('click', () => {
        mobileSearchContainer.classList.toggle('hidden');
        if (!mobileSearchContainer.classList.contains('hidden')) {
            mobileSearchInput.focus();
        }
    });

    // Start!
    init();
});
