function selectAyah(ayah) {
    if (searchInput) searchInput.value = `${ayah.surah_name} - آیه ${ayah.ayah_number}`;
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

    if (!tafsirs || tafsirs.length === 0) {
        tafsirContent.innerHTML = `
            <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-yellow-700">
                ⚠️ تفسیری برای این آیه یافت نشد.
            </div>
        `;
        tafsirSection.classList.remove('hidden');
        return;
    }

    let html = `
        <div class="space-y-6">
            <div class="bg-emerald-50 rounded-lg p-4 border-r-4 border-emerald-500">
                <p class="text-gray-700 font-medium">
                    سوره <span class="text-emerald-700">${escapeHtml(ayah.surah_name)}</span> -
                    آیه <span class="text-emerald-700">${ayah.ayah_number}</span>
                </p>
                <p class="text-gray-600 mt-2 text-base">${escapeHtml(ayah.text_prefix || '')}...</p>
            </div>
    `;

    tafsirs.forEach(tafsir => {
        html += `
            <div class="border-b border-gray-100 pb-4 last:border-b-0">
                <h3 class="font-bold text-gray-800 text-lg mb-2">
                    📚 ${escapeHtml(tafsir.source)}
                    ${tafsir.order_priority === 1 ? '<span class="text-xs bg-emerald-100 text-emerald-700 px-2 py-1 rounded mr-2">اصلی</span>' : ''}
                </h3>
                <div class="text-gray-700 leading-relaxed whitespace-pre-wrap">
                    ${escapeHtml(tafsir.text)}
                </div>
            </div>
        `;
    });

    html += `</div>`;
    tafsirContent.innerHTML = html;
    tafsirSection.classList.remove('hidden');
}