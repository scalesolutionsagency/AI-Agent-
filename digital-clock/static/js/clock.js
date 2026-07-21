/**
 * Digital Clock Web Interface
 * Real-time clock updates for multiple time zones
 */

class DigitalClock {
    constructor() {
        this.gridElement = document.getElementById('clocksGrid');
        this.lastUpdateElement = document.getElementById('lastUpdate');
        this.themeToggle = document.getElementById('themeToggle');
        this.formatToggle = document.getElementById('formatToggle');
        this.refreshBtn = document.getElementById('refreshBtn');
        
        this.use24Hour = true;
        this.isDarkMode = this.detectDarkMode();
        
        this.init();
    }
    
    init() {
        // Event listeners
        this.themeToggle.addEventListener('click', () => this.toggleTheme());
        this.formatToggle.addEventListener('click', () => this.toggleFormat());
        this.refreshBtn.addEventListener('click', () => this.updateClocks());
        
        // Load initial data
        this.updateClocks();
        
        // Auto-refresh every second
        setInterval(() => this.updateClocks(), 1000);
    }
    
    detectDarkMode() {
        const saved = localStorage.getItem('darkMode');
        if (saved !== null) {
            return saved === 'true';
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    
    toggleTheme() {
        this.isDarkMode = !this.isDarkMode;
        document.body.classList.toggle('dark-mode', this.isDarkMode);
        localStorage.setItem('darkMode', this.isDarkMode);
        this.themeToggle.textContent = this.isDarkMode ? '☀️ Light Mode' : '🌙 Dark Mode';
    }
    
    toggleFormat() {
        this.use24Hour = !this.use24Hour;
        this.formatToggle.textContent = this.use24Hour ? '12/24 Hour' : '24/12 Hour';
        this.updateClocks();
    }
    
    async updateClocks() {
        try {
            const response = await fetch('/api/time');
            const data = await response.json();
            
            this.renderClocks(data.clocks);
            this.lastUpdateElement.textContent = new Date().toLocaleTimeString();
        } catch (error) {
            console.error('Error fetching time data:', error);
            this.gridElement.innerHTML = '<div class="loading"><p>Error loading clocks</p></div>';
        }
    }
    
    renderClocks(clocks) {
        if (clocks.length === 0) {
            this.gridElement.innerHTML = '<div class="loading"><p>No clocks to display</p></div>';
            return;
        }
        
        this.gridElement.innerHTML = clocks.map(clock => this.createClockCard(clock)).join('');
    }
    
    createClockCard(clock) {
        const timeDisplay = this.use24Hour ? clock.time : clock.time_12h;
        const dstClass = clock.is_dst ? 'active' : '';
        const dstText = clock.is_dst ? 'DST' : 'STD';
        
        return `
            <div class="clock-card">
                <div class="timezone-name">${this.escapeHtml(clock.timezone)}</div>
                <div class="digital-time">${timeDisplay}</div>
                <div class="time-info">
                    <div class="info-item">
                        <span class="info-label">Date</span>
                        <span class="info-value">${clock.date}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Day</span>
                        <span class="info-value">${clock.day}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">UTC</span>
                        <span class="info-value">${clock.utc_offset}</span>
                    </div>
                </div>
                <div class="dst-badge ${dstClass}">${dstText}</div>
            </div>
        `;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new DigitalClock();
});
