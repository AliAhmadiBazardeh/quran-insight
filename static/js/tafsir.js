function selectAyah(ayah) {
//    if (searchInput) searchInput.value = `${ayah.surah_name} - آیه ${ayah.ayah_number}`;
    if (searchResultsDiv) searchResultsDiv.classList.add('hidden');
    loadTafsir(ayah.id);
}

async function loadTafsir(ayahId) {
    if (!tafsirSection || !tafsirContent || !tafsirLoadingSpinner) return;
    tafsirSection.classList.add('hidden');
    tafsirLoadingSpinner.classList.remove('hidden');

    try {
        const response = await fetch(`/api/tafsir/?ayah_id=${ayahId}`);
        if (!response.ok) throw new Error('خطا در دریافت تفسیر');
        const data = await response.json();
        renderTafsir(data);
        currentAyahId = ayahId;
    } catch (error) {
        console.error('Error loading tafsir:', error);
        tafsirContent.innerHTML = `
            <div class="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                خطا در بارگذاری تفسیر. لطفاً مجدداً تلاش کنید.
            </div>
        `;
        tafsirSection.classList.remove('hidden');
    } finally {
        tafsirLoadingSpinner.classList.add('hidden');
    }
}

function renderTafsir(data) {
    if (!tafsirContent || !tafsirSection) return;
    const tafsirs = data.tafsirs;
    const ayah = data.ayah;
    const count = data.count;

    let html = `
        <div class="space-y-6">
            <div class="bg-slate-50 rounded-lg p-4 border-r-4 border-slate-500">
                <p class="text-gray-700 font-medium">
                    سوره ${escapeHtml(ayah.surah_name)} -
                    آیه ${ayah.ayah_number}
                </p>
                <p class="text-gray-600 mt-2 text-base">${escapeHtml(ayah.text || '')}</p>
            </div>
    `;

    if (count > 0)
    {
        html += `
        <h2 class="text-xl font-semibold text-gray-800 mb-4">📖 ${count} تفسیر یافت شد</h2>`;
    }

    if (!tafsirs || tafsirs.length === 0) {
        html += `
            <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-yellow-700">
                ⚠️ تفسیری برای این آیه یافت نشد.
            </div>
        `;
        tafsirContent.innerHTML = html;
        tafsirSection.classList.remove('hidden');
        return;
    }

    tafsirs.forEach(tafsir => {
        html += `
            <div class="border-b border-gray-100 pb-4 last:border-b-0">
                <h3 class="font-bold text-gray-800 text-lg mb-2">
                    📚 ${escapeHtml(tafsir.source)}
                </h3>
                <div class="tafsir-text-container">
                    <div class="text-gray-700 leading-relaxed whitespace-pre-line line-clamp-3">
                            ${escapeHtml(tafsir.text)}
                    </div>
                    <button class="text-blue-600 hover:text-blue-800 text-sm mt-2 toggle-tafsir">
                        مشاهده بیشتر ←
                    </button>
                </div>
            </div>
        `;
    });

    html += `</div>`;
    tafsirContent.innerHTML = html;
    tafsirSection.classList.remove('hidden');
}

document.addEventListener('click', function(e) {
    if (e.target.classList.contains('toggle-tafsir')) {
        const textDiv = e.target.previousElementSibling;
        const isExpanded = textDiv.classList.contains('expanded');
        
        if (isExpanded) {
            textDiv.classList.remove('expanded');
            e.target.textContent = 'مشاهده بیشتر ←';
        } else {
            textDiv.classList.add('expanded');
            e.target.textContent = 'بستن ↑';
        }
    }
});
