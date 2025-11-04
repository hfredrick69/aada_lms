import 'package:flutter/material.dart';
import 'dashboard_screen.dart';
import 'job_board_screen.dart';
import 'my_tuition_screen.dart';
import 'login_screen.dart';

class QuizzesScreen extends StatelessWidget {
  final Map<String, dynamic> student;
  QuizzesScreen({required this.student});

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
        title: Text("Quizzes"),
        actions: [
          IconButton(
            icon: Icon(Icons.logout),
            onPressed: () => logout(context),
          )
        ],
      ),
      body: ListView(
        padding: EdgeInsets.all(16),
        children: [
          Card(
            color: Colors.grey[100],
            child: ListTile(
              title: Text("Dental Anatomy Quiz"),
              subtitle: Text("Status: Not Started"),
            ),
          ),
          Card(
            color: Colors.orange[100],
            child: ListTile(
              title: Text("Chairside Assisting Quiz"),
              subtitle: Text("Status: In Progress"),
            ),
          ),
          Card(
            color: Colors.green[100],
            child: ListTile(
              title: Text("OSHA Guidelines Quiz"),
              subtitle: Text("Status: Completed • Score: 90%"),
            ),
          ),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: 1,
        selectedItemColor: Colors.black,
        unselectedItemColor: Colors.grey,
        onTap: (index) {
          if (index == 0) navigateTo(context, DashboardScreen(student: student));
          if (index == 2) navigateTo(context, JobBoardScreen(student: student));
          if (index == 3) navigateTo(context, MyTuitionScreen(student: student));
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
