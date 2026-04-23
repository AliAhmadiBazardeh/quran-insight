let searchInput, searchResultsDiv, resultsList, noResultsMsg, loadingSpinner;
let tafsirSection, tafsirContent, tafsirLoadingSpinner;
let currentAyahId = null;

// تابع اولیه برای مقداردهی پس از آماده شدن DOM
function initSearch() {
    searchInput = document.getElementById('searchInput');
    searchResultsDiv = document.getElementById('searchResults');
    resultsList = document.getElementById('resultsList');
    noResultsMsg = document.getElementById('noResultsMsg');
    loadingSpinner = document.getElementById('loadingSpinner');
    tafsirSection = document.getElementById('tafsirSection');
    tafsirContent = document.getElementById('tafsirContent');
    tafsirLoadingSpinner = document.getElementById('tafsirLoadingSpinner');

    if (!searchInput) return;

    // اضافه کردن event listener با debounce
    const debouncedSearch = debounce((event) => {
        const query = event.target.value;
        performSearch(query);
    }, 300);

    searchInput.addEventListener('input', debouncedSearch);

    // بستن dropdown با کلیک خارج از آن
    document.addEventListener('click', function(event) {
        if (searchResultsDiv && !searchResultsDiv.contains(event.target) && event.target !== searchInput) {
            searchResultsDiv.classList.add('hidden');
        }
    });
}

function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

async function performSearch(query) {
    if (!query.trim()) {
        if (searchResultsDiv) searchResultsDiv.classList.add('hidden');
        return;
    }

    if (loadingSpinner) loadingSpinner.classList.remove('hidden');

    try {
        const response = await fetch(`/api/search/?q=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('خطا در دریافت نتایج');
        const data = await response.json();
        renderResults(data.results);
    } catch (error) {
        console.error('Error:', error);
        if (resultsList) resultsList.innerHTML = '';
        if (noResultsMsg) {
            noResultsMsg.classList.remove('hidden');
            noResultsMsg.innerText = 'خطا در ارتباط با سرور';
        }
        if (searchResultsDiv) searchResultsDiv.classList.remove('hidden');
    } finally {
        if (loadingSpinner) loadingSpinner.classList.add('hidden');
    }
}

function renderResults(results) {
    if (!resultsList || !noResultsMsg || !searchResultsDiv) return;
    resultsList.innerHTML = '';

    if (!results || results.length === 0) {
        noResultsMsg.classList.remove('hidden');
        resultsList.classList.add('hidden');
    } else {
        noResultsMsg.classList.add('hidden');
        resultsList.classList.remove('hidden');

        results.forEach(item => {
            const li = document.createElement('li');
            li.className = 'px-4 py-3 hover:bg-emerald-50 cursor-pointer transition duration-150';
            li.innerHTML = `
                <div class="flex justify-between items-center">
                    <span class="font-medium text-emerald-800">${escapeHtml(item.surah_name)} - آیه ${item.ayah_number}</span>
                    <span class="text-xs text-gray-500">${item.surah_number}:${item.ayah_number}</span>
                </div>
                <div class="text-sm text-gray-600 mt-1">${escapeHtml(item.text_prefix || '')}...</div>
            `;
            li.addEventListener('click', () => selectAyah(item));
            resultsList.appendChild(li);
        });
    }
    searchResultsDiv.classList.remove('hidden');
}




function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// اجرای تابع مقداردهی اولیه پس از لود کامل DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSearch);
} else {
    initSearch();
}