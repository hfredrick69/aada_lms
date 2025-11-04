import 'package:flutter/material.dart';
import 'dashboard_screen.dart';
import 'quizzes_screen.dart';
import 'job_board_screen.dart';
import 'login_screen.dart';

class MyTuitionScreen extends StatelessWidget {
  final Map<String, dynamic> student;
  MyTuitionScreen({required this.student});

  void logout(BuildContext context) {
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (_) => LoginScreen()),
      (route) => false,
    );
  }

  void navigateTo(BuildContext context, Widget screen) {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => screen),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: Text("My Tuition"),
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
              color: Colors.redAccent,
              child: ListTile(
                title: Text("Past Due"),
                subtitle: Text("\$400 due on June 15"),
              ),
            ),
            SizedBox(height: 12),
            Card(
              color: Colors.green[300],
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
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: 3,
        selectedItemColor: Colors.black,
        unselectedItemColor: Colors.grey,
        onTap: (index) {
          if (index == 0) navigateTo(context, DashboardScreen(student: student));
          if (index == 1) navigateTo(context, QuizzesScreen(student: student));
          if (index == 2) navigateTo(context, JobBoardScreen(student: student));
        },
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: "Dashboard"),
          BottomNavigationBarItem(icon: Icon(Icons.quiz), label: "Quizzes"),
          BottomNavigationBarItem(icon: Icon(Icons.work), label: "Job Board"),
          BottomNavigationBarItem(icon: Icon(Icons.attach_money), label: "My Tuition"),
        ],
      ),
    );
  }
}
