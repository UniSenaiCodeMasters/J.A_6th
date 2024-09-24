function submitSettings() {
    var settings = {
        plant_name: document.getElementById('plant-name').value,
        optimal_temperature: parseFloat(document.getElementById('optimal-temperature').value),
        optimal_humidity: parseFloat(document.getElementById('optimal-humidity').value),
        light_start_time: document.getElementById('light-start-time').value,
        light_end_time: document.getElementById('light-end-time').value,
        led_red_intensity: parseInt(document.getElementById('led-red-intensity').value),
        led_green_intensity: parseInt(document.getElementById('led-green-intensity').value),
        led_white_intensity: parseInt(document.getElementById('led-white-intensity').value)
    };

    fetch('/api/set-plant-settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Resposta do servidor:', data);
        alert('Configurações salvas com sucesso!');
    });
}
