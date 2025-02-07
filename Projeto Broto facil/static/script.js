// static/script.js

document.addEventListener('DOMContentLoaded', function() {
    const toggleModeButton = document.getElementById('toggle-mode');
    const toggleViewButton = document.getElementById('toggle-view');
    let isDarkMode = localStorage.getItem('isDarkMode') === 'true';
    let isMobileView = localStorage.getItem('isMobileView') === 'true';

    // Aplica as preferências salvas
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        toggleModeButton.innerText = 'Modo Claro';
    }

    if (isMobileView) {
        document.body.classList.add('mobile-view');
        toggleViewButton.innerText = 'Versão Web';
    }

    // Função para atualizar os dados em tempo real
    function updateData() {
        fetch('/get_sensor_data')
            .then(response => response.json())
            .then(data => {
                document.getElementById('temp').innerHTML = data.temperature + ' &deg;C';
                document.getElementById('hum').innerHTML = data.humidity + ' %';
                document.getElementById('distance').innerHTML = data.distance + ' cm';
                document.getElementById('led1_pwm').innerHTML = data.led1_pwm + ' %';
                document.getElementById('led2_pwm').innerHTML = data.led2_pwm + ' %';
                document.getElementById('led3_pwm').innerHTML = data.led3_pwm + ' %';
                document.getElementById('ldrValue').innerHTML = data.ldr_value + ' *';
                // Atualize outros campos conforme necessário
            })
            .catch(error => console.error('Erro ao obter dados do sensor:', error));
    }
    

    // Atualiza os dados a cada 2 segundos
    setInterval(updateData, 2000);
    updateData();

    // Alternar entre modo claro e escuro
    toggleModeButton.addEventListener('click', function() {
        if (isDarkMode) {
            document.body.classList.remove('dark-mode');
            toggleModeButton.innerText = 'Modo Escuro';
        } else {
            document.body.classList.add('dark-mode');
            toggleModeButton.innerText = 'Modo Claro';
        }
        isDarkMode = !isDarkMode;
        localStorage.setItem('isDarkMode', isDarkMode);
    });

    // Alternar entre versão mobile e web
    toggleViewButton.addEventListener('click', function() {
        if (isMobileView) {
            document.body.classList.remove('mobile-view');
            toggleViewButton.innerText = 'Versão Mobile';
        } else {
            document.body.classList.add('mobile-view');
            toggleViewButton.innerText = 'Versão Web';
        }
        isMobileView = !isMobileView;
        localStorage.setItem('isMobileView', isMobileView);
    });
});
