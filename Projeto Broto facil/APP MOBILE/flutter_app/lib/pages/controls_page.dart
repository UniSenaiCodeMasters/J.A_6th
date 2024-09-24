import 'package:flutter/material.dart';

class ControlsPage extends StatelessWidget {
    // Função para enviar comandos aos atuadores
    void controlActuator(String actuator, String action) {
        // Implementar chamada MQTT para enviar comandos
        // ...
    }

    @override
    Widget build(BuildContext context) {
        return Scaffold(
            appBar: AppBar(
                title: Text('Controles'),
            ),
            body: Center(
                child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                        ElevatedButton(
                            onPressed: () {
                                controlActuator('water_pump', 'on');
                            },
                            child: Text('Ligar Bomba de Água'),
                        ),
                        ElevatedButton(
                            onPressed: () {
                                controlActuator('water_pump', 'off');
                            },
                            child: Text('Desligar Bomba de Água'),
                        ),
                        // Adicionar mais controles conforme necessário
                    ],
                ),
            ),
        );
    }
}
