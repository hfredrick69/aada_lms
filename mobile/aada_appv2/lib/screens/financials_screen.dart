import 'package:flutter/material.dart';
import 'login_screen.dart';

class FinancialsScreen extends StatelessWidget {
  void logout(BuildContext context) {
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (_) => LoginScreen()),
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Financials"),
        actions: [
          IconButton(
            icon: Icon(Icons.logout),
            onPressed: () => logout(context),
          )
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Card(
              color: Colors.red[100],
              child: ListTile(
                title: Text("Past Due"),
                subtitle: Text("\$400 due on June 15"),
              ),
            ),
            SizedBox(height: 12),
            Card(
              color: Colors.orange[100],
              child: ListTile(
                title: Text("Upcoming"),
                subtitle: Text("\$500 due on July 10"),
              ),
            ),
            SizedBox(height: 12),
            Card(
              color: Colors.blue[100],
              child: ListTile(
                title: Text("Tuition Balance"),
                subtitle: Text("\$2,100 remaining"),
              ),
            ),
          ],
        ),
      ),
    );
  }
}