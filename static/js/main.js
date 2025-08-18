document.addEventListener('DOMContentLoaded', function() {
    // Initialisation des tooltips Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Gestion des boutons de présence
    document.querySelectorAll('.attendance-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const studentId = this.dataset.studentId;
            const date = this.dataset.date;
            const status = this.dataset.status;
            
            // Mettre à jour l'interface utilisateur
            updateAttendanceUI(studentId, date, status);
            
            // Ici, vous pourriez ajouter une requête AJAX pour sauvegarder le statut
        });
    });
    
    // Fonction pour mettre à jour l'interface utilisateur
    function updateAttendanceUI(studentId, date, status) {
        const container = document.querySelector(`.attendance-actions[data-student-id="${studentId}"][data-date="${date}"]`);
        if (!container) return;
        
        // Mettre à jour tous les boutons dans le container
        container.querySelectorAll('.btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.status === status) {
                btn.classList.add('active');
            }
        });
        
        // Mettre à jour le badge de statut
        const statusBadge = document.querySelector(`.attendance-status[data-student-id="${studentId}"][data-date="${date}"]`);
        if (statusBadge) {
            statusBadge.className = `attendance-badge badge-${status}`;
            statusBadge.textContent = status === 'present' ? 'Présent' : 
                                      status === 'absent' ? 'Absent' : 'Retard';
        }
    }
});