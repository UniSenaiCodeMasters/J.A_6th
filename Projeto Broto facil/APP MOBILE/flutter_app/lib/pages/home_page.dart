import 'package:flutter/material.dart';
import 'settings_page.dart';
import 'controls_page.dart';

class MyHomePage extends StatefulWidget {
  MyHomePage({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
    // Variáveis para armazenar os dados dos sensores
    double temperature = 0.0;
    double humidity = 0.0;
    String waterLevel = 'Desconhecido';
    double lightLevel = 0.0;
    double plantHeight = 0.0;

    @override
    void initState() {
        super.initState();
        // Inicializar a conexão MQTT e subscrever aos tópicos
        // ...
    }

    @override
    Widget build(BuildContext context) {
        return Scaffold(
            appBar: AppBar(
                title: Text(widget.title),
            ),
            body: Center(
                child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: <Widget>[
                        Text(
                            'Temperatura: $temperature °C',
                        ),
                        Text(
                            'Umidade: $humidity %',
                        ),
                        Text(
                            'Nível de Água: $waterLevel',
                        ),
                        Text(
                            'Nível de Luz: $lightLevel %',
                        ),
                        Text(
                            'Altura da Planta: $plantHeight cm',
                        ),
                    ],
                ),
            ),
            drawer: Drawer(
                child: ListView(
                    padding: EdgeInsets.zero,
                    children: [
                        DrawerHeader(
                            decoration: BoxDecoration(
                                color: Colors.green,
                            ),
                            child: Text(
                                'Menu',
                                style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 24,
                                ),
                            ),
                        ),
                        ListTile(
                            leading: Icon(Icons.home),
                            title: Text('Início'),
                            onTap: () {
                                Navigator.pop(context);
                            },
                        ),
                        ListTile(
                            leading: Icon(Icons.settings),
                            title: Text('Configurações da Planta'),
                            onTap: () {
                                Navigator.push(
                                    context,
                                    MaterialPageRoute(builder: (context) => SettingsPage()),
                                );
                            },
                        ),
                        ListTile(
                            leading: Icon(Icons.control_camera),
                            title: Text('Controles'),
                            onTap: () {
                                Navigator.push(
                                    context,
                                    MaterialPageRoute(builder: (context) => ControlsPage()),
                                );
                            },
                        ),
                    ],
                ),
            ),
        );
    }
}
