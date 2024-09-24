import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'pages/home_page.dart';
import 'pages/settings_page.dart';
import 'pages/controls_page.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  // Este widget é a raiz da sua aplicação.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Cultivo Inteligente',
      theme: ThemeData(
        primarySwatch: Colors.green,
      ),
      home: MyHomePage(title: 'Cultivo Inteligente'),
    );
  }
}
