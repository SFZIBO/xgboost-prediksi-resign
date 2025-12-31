$(document).ready(function() {
    // Handle form submission
    $('#prediction-form').on('submit', function(e) {
        e.preventDefault();
        
        // Show loading state
        const submitBtn = $('button[type="submit"]');
        const originalText = submitBtn.html();
        submitBtn.html('<span class="spinner-border spinner-border-sm me-2" role="status"></span>Memproses...');
        submitBtn.prop('disabled', true);
        
        // Get form data
        const formData = $(this).serialize();
        
        // Send AJAX request
        $.ajax({
            url: '/predict',
            type: 'POST',
            data: formData,
            success: function(response) {
                if (response.error) {
                    showError('Terjadi kesalahan: ' + response.error);
                } else {
                    showResult(response);
                }
            },
            error: function(xhr, status, error) {
                showError('Error: ' + error);
            },
            complete: function() {
                // Restore button state
                submitBtn.html(originalText);
                submitBtn.prop('disabled', false);
            }
        });
    });
    
    function showError(message) {
        $('#prediction-result').html(`
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <strong>Error!</strong> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `);
    }
    
    function showResult(result) {
        const riskBadge = `<span class="risk-badge" style="background-color: ${result.risk_color}20; color: ${result.risk_color}; border: 1px solid ${result.risk_color}">${result.risk_level}</span>`;
        
        let recommendationHtml = '';
        if (result.recommendation && result.recommendation.length > 0) {
            recommendationHtml = `
                <div class="mt-4">
                    <h5 class="text-primary">${result.recommendation[0]}</h5>
                    <ul class="recommendation-list text-muted">
                        ${result.recommendation.slice(1).map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        $('#prediction-result').html(`
            <div class="prediction-card">
                <div class="text-center mb-4">
                    <div class="display-1 fw-bold mb-3" style="color: ${result.risk_color}">
                        ${result.prediction === 'Yes' ? '⚠️' : '✅'}
                    </div>
                    <h2 class="mb-4">${result.prediction === 'Yes' ? 'Kemungkinan Resign Tinggi' : 'Kemungkinan Resign Rendah'}</h2>
                </div>
                
                <div class="mb-4">
                    <div class="d-flex justify-content-between mb-2">
                        <span class="fw-bold">Probabilitas Resign:</span>
                        <span class="fw-bold fs-5" style="color: ${result.risk_color}">${result.probability}</span>
                    </div>
                    <div class="progress">
                        <div class="progress-bar" role="progressbar" 
                             style="width: ${parseFloat(result.probability)}; background-color: ${result.risk_color}"
                             aria-valuenow="${parseFloat(result.probability)}" 
                             aria-valuemin="0" 
                             aria-valuemax="100"></div>
                    </div>
                    <small class="text-muted d-block mt-1 text-center">
                        ${result.prediction === 'Yes' 
                            ? 'Di atas 50% - Perlu perhatian segera' 
                            : 'Di bawah 50% - Karyawan cenderung bertahan'}
                    </small>
                </div>
                
                <div class="mb-4 p-3 bg-light rounded">
                    <div class="d-flex align-items-center mb-2">
                        <span class="me-2">🚩</span>
                        <span class="fw-bold">Tingkat Risiko:</span>
                        <span class="ms-2">${riskBadge}</span>
                    </div>
                    <p class="text-muted mb-0">
                        ${result.prediction === 'Yes' 
                            ? 'Karyawan ini memiliki risiko resign yang signifikan' 
                            : 'Karyawan ini memiliki tingkat retensi yang baik'}
                    </p>
                </div>
                
                ${recommendationHtml}
                
                <div class="feature-importance mt-4 p-3 bg-white border rounded">
                    <h5 class="mb-3 text-primary">🔍 Faktor Penentu</h5>
                    <div class="d-flex justify-content-between mb-2">
                        <span>Kepuasan Pekerjaan</span>
                        <span class="badge bg-primary">Penting</span>
                    </div>
                    <div class="d-flex justify-content-between mb-2">
                        <span>Penghasilan Bulanan</span>
                        <span class="badge bg-primary">Penting</span>
                    </div>
                    <div class="d-flex justify-content-between">
                        <span>Lama di Perusahaan</span>
                        <span class="badge bg-secondary">Sedang</span>
                    </div>
                    <small class="text-muted mt-2 d-block">
                        * Berdasarkan analisis faktor yang paling berpengaruh pada model
                    </small>
                </div>
            </div>
        `);
        
        // Animate progress bar
        $('.progress-bar').css('width', '0%').animate({
            width: `${parseFloat(result.probability)}`
        }, 1000);
    }
});