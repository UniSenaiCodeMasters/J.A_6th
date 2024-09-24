import 'package:flutter/material.dart';

class SettingsPage extends StatefulWidget {
    @override
    _SettingsPageState createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
    final _formKey = GlobalKey<FormState>();
    String plantName = '';
    double optimalTemperature = 25.0;
    double optimalHumidity = 50.0;
    TimeOfDay lightStartTime = TimeOfDay(hour: 6, minute: 0);
    TimeOfDay lightEndTime = TimeOfDay(hour: 18, minute: 0);
    int ledRedIntensity = 255;
    int ledGreenIntensity = 255;
    int ledWhiteIntensity = 255;

    // Função para enviar as configurações ao servidor
    void submitSettings() {
        // Implementar chamada HTTP POST para o endpoint /api/set-plant-settings
        // ...
    }

    @override
    Widget build(BuildContext context) {
        return Scaffold(
            appBar: AppBar(
                title: Text('Configurações da Planta'),
            ),
            body: Padding(
                padding: EdgeInsets.all(16.0),
                child: Form(
                    key: _formKey,
                    child: ListView(
                        children: [
                            TextFormField(
                                decoration: InputDecoration(labelText: 'Nome da Planta'),
                                onSaved: (value) {
                                    plantName = value!;
                                },
                            ),
                            TextFormField(
                                decoration: InputDecoration(labelText: 'Temperatura Ótima (°C)'),
                                keyboardType: TextInputType.number,
                                onSaved: (value) {
                                    optimalTemperature = double.parse(value!);
                                },
                            ),
                            TextFormField(
                                decoration: InputDecoration(labelText: 'Umidade Ótima (%)'),
                                keyboardType: TextInputType.number,
                                onSaved: (value) {
                                    optimalHumidity = double.parse(value!);
                                },
                            ),
                            // Adicionar seletores de tempo para lightStartTime e lightEndTime
                            // Adicionar sliders para ledRedIntensity, ledGreenIntensity, ledWhiteIntensity
                            ElevatedButton(
                                onPressed: () {
                                    if (_formKey.currentState!.validate()) {
                                        _formKey.currentState!.save();
                                        submitSettings();
                                        ScaffoldMessenger.of(context).showSnackBar(
                                            SnackBar(content: Text('Configurações salvas!')),
                                        );
                                    }
                                },
                                child: Text('Salvar Configurações'),
                            ),
                        ],
                    ),
                ),
            ),
        );
    }
}
